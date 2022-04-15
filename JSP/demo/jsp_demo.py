import os
import json
import collections
from ortools.sat.python import cp_model

from djsp_logger import DJSP_Logger
from djsp_plotter import DJSP_Plotter

def load_instance(filename):
    data = []
    
    f = open(filename)
    line = f.readline()
    while line[0] == '#':
        line = f.readline()
    line = line.split()
    num_job, num_machine = int(line[0]), int(line[1])

    for i in range(num_job):
        job_data = []
        line = f.readline().split()
        for j in range(num_machine):
            machine_id, processing_time = int(line[j * 2]), int(line[j * 2 + 1])
            # print('Machine', machine_id, 'processing_time:', processing_time)
            job_data.append((machine_id, processing_time))
        data.append(job_data)
    return data

def solve(file_name, time_limit=10.0):
    # jobs_data = [  # op = (machine_id, processing_time).
    #     [(0, 3), (1, 2), (2, 2)],  # Job0
    #     [(0, 2), (2, 1), (1, 4)],  # Job1
    #     [(1, 4), (2, 3)]  # Job2
    # ]
    result = []
    jobs_data = load_instance(file_name)

    num_machines = 1 + max(op[0] for job in jobs_data for op in job)
    all_machines = range(num_machines)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(op[1] for job in jobs_data for op in job)

    # Create the model.
    jsp_model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start finish interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_ops = {}
    machine_to_intervals = collections.defaultdict(list)
    print(jobs_data)
    for job_id, job in enumerate(jobs_data):
        for op_id, op in enumerate(job):
            machine = op[0]
            duration = op[1]
            suffix = '_%i_%i' % (job_id, op_id)
            start = jsp_model.NewIntVar(0, horizon, 'start' + suffix)
            finish = jsp_model.NewIntVar(0, horizon, 'finish' + suffix)
            interval = jsp_model.NewIntervalVar(start, duration, finish, 'interval' + suffix)
            all_ops[job_id, op_id] = task_type(start=start, finish=finish, interval=interval)
            machine_to_intervals[machine].append(interval)

    # No overlap constraints.
    for machine in all_machines:
        jsp_model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences constraints
    for job_id, job in enumerate(jobs_data):
        for op_id in range(len(job) - 1):
            jsp_model.Add(all_ops[job_id, op_id].finish <= all_ops[job_id, op_id + 1].start)

    # set objective function (makespan)
    makespan = jsp_model.NewIntVar(0, horizon, 'makespan')
    jsp_model.AddMaxEquality(makespan, [
        all_ops[job_id, len(job) - 1].finish for job_id, job in enumerate(jobs_data)
    ])
    # minimize makespan
    jsp_model.Minimize(makespan)

    # Creates the solver.
    solver = cp_model.CpSolver()
    # set time limit
    solver.parameters.max_time_in_seconds = time_limit
    # solve
    status = solver.Solve(jsp_model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('%s\t%f\t%f\t%r' %(
            file_name, 
            solver.ObjectiveValue(), solver.WallTime(), 
            bool(status == cp_model.OPTIMAL)))
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for op_id, op in enumerate(job):
                machine = op[0]
                assigned_jobs[machine].append(
                    assigned_task_type(start=solver.Value(
                        all_ops[job_id, op_id].start),
                                       job=job_id,
                                       index=op_id,
                                       duration=op[1]))

        # Create per machine output lines.
        output = ''
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            for assigned_task in assigned_jobs[machine]:
                start = assigned_task.start
                duration = assigned_task.duration
                # Add spaces to output to align columns.
                op_info = {
                    'Order':        None,
                    'job_id':       assigned_task.job,
                    'op_id':        assigned_task.index,
                    'machine_id':   machine,
                    'start_time':   start,
                    'process_time': duration,
                    'finish_time':  start + duration,
                    'job_type':     None,
                }
                result.append(op_info)
    else:
        print('No solution found.')
    return result

if __name__ == '__main__':
    # in_file = 'easy1'
    in_file = 'abz5'
    fn, _ = os.path.splitext(in_file)
    time_limit = 60     # in second
    jsp_result = solve(in_file, time_limit=time_limit)
    out_file = os.path.join(fn+'.json')
    with open(out_file, 'w') as f:
        json.dump(jsp_result, f, indent=4)
    
    # visualization
    logger = DJSP_Logger()
    plotter = DJSP_Plotter(logger)
    logger.load(out_file)
    print(logger)
    # plotter.plot_googlechart_timeline(os.path.json('timeline', fn+'.html'))
    plotter.plot_googlechart_timeline(os.path.join('timeline', fn+'_makespan.html'))


    # logger = DJSP_Logger()
    # plotter = DJSP_Plotter(logger)
    # logger.load('easy1.json')
    # print(logger)
    # # plotter.plot_googlechart_timeline(os.path.json('timeline', fn+'.html'))
    # plotter.plot_googlechart_timeline(os.path.join('timeline/overlap.html'))

