import collections
import json
import os
from ortools.sat.python import cp_model

from djsp_logger import DJSP_Logger
from djsp_plotter import DJSP_Plotter



def solve():
    jobs_data = [
        [  # Job 0 (process time, machine id)
            [(3, 0), (1, 1), (5, 2)],  # op 0 with 3 alternatives
            [(2, 0), (4, 1), (6, 2)],  # op 1 with 3 alternatives
            [(2, 0), (3, 1), (1, 2)],  # op 2 with 3 alternatives
        ],
        [  # Job 1
            [(2, 0), (3, 1), (4, 2)],
            [(1, 0), (5, 1), (4, 2)],
            [(2, 0), (1, 1), (4, 2)],
        ],
        [  # Job 2
            [(2, 0), (1, 1), (4, 2)],
            [(2, 0), (3, 1), (4, 2)],
            [(3, 0), (1, 1), (5, 2)],
        ],
    ]

    num_jobs = len(jobs_data)
    all_jobs = range(num_jobs)

    num_machines = 2
    all_machines = range(num_machines)

    # Model the flexible jobshop problem.
    fjsp_model = cp_model.CpModel()

    horizon = 0
    for job in jobs_data:
        for op in job:
            max_task_duration = 0
            for alternative in op:
                max_task_duration = max(max_task_duration, alternative[0])
            horizon += max_task_duration

    # print('Horizon = %i' % horizon)

    # Global storage of variables.
    intervals_per_resources = collections.defaultdict(list)
    starts = {}  # indexed by (job_id, task_id).
    presences = {}  # indexed by (job_id, task_id, alt_id).
    job_ends = []

    # Scan the jobs and create the relevant variables and intervals.
    for job_id, job in enumerate(jobs_data):
        previous_end = None
        for op_id, op in enumerate(job):
            min_duration = op[0][0]
            max_duration = op[0][0]
            num_alternatives = len(op)
            all_alternatives = range(num_alternatives)

            for machine_id in range(1, num_alternatives):
                alt_duration = op[machine_id][0]
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)

            # Create main interval for the task.
            suffix = '_%i_%i' % (job_id, op_id)
            start = fjsp_model.NewIntVar(0, horizon, 'start' + suffix)
            duration = fjsp_model.NewIntVar(min_duration, max_duration, 'duration' + suffix)
            finish = fjsp_model.NewIntVar(0, horizon, 'finish' + suffix)
            interval = fjsp_model.NewIntervalVar(start, duration, finish, 'interval' + suffix)

            # Store the start for the solution.
            starts[(job_id, op_id)] = start

            # Add precedence with previous task in the same job.
            if previous_end is not None:
                fjsp_model.Add(start >= previous_end)
            previous_end = finish

            # Create alternative intervals.
            if num_alternatives > 1:
                alt_presences = []
                for machine_id in all_alternatives:
                    alt_suffix = '_j%i_t%i_a%i' % (job_id, op_id, machine_id)
                    alt_presence = fjsp_model.NewBoolVar('presence' + alt_suffix)
                    alt_start = fjsp_model.NewIntVar(0, horizon, 'start' + alt_suffix)
                    alt_duration = op[machine_id][0]
                    alt_finish = fjsp_model.NewIntVar(0, horizon, 'finish' + alt_suffix)
                    alt_interval = fjsp_model.NewOptionalIntervalVar(alt_start, alt_duration, alt_finish, alt_presence, 'interval' + alt_suffix)
                    alt_presences.append(alt_presence)

                    # Link the master variables with the local ones.
                    fjsp_model.Add(start == alt_start).OnlyEnforceIf(alt_presence)
                    fjsp_model.Add(duration == alt_duration).OnlyEnforceIf(alt_presence)
                    fjsp_model.Add(finish == alt_finish).OnlyEnforceIf(alt_presence)

                    # Add the local interval to the right machine.
                    intervals_per_resources[op[machine_id][1]].append(alt_interval)

                    # Store the presences for the solution.
                    presences[(job_id, op_id, machine_id)] = alt_presence

                # Select exactly one presence variable.
                fjsp_model.Add(sum(alt_presences) == 1)
            else:
                intervals_per_resources[op[0][1]].append(interval)
                presences[(job_id, op_id, 0)] = fjsp_model.NewConstant(1)

        job_ends.append(previous_end)

    # Create machines constraints.
    for machine_id in all_machines:
        intervals = intervals_per_resources[machine_id]
        if len(intervals) > 1:
            fjsp_model.AddNoOverlap(intervals)

    # Makespan objective
    makespan = fjsp_model.NewIntVar(0, horizon, 'makespan')
    fjsp_model.AddMaxEquality(makespan, job_ends)
    fjsp_model.Minimize(makespan)

    # Solve model.
    solver = cp_model.CpSolver()
    status = solver.Solve(fjsp_model)

    result = []
    # Print final solution.
    for job_id in all_jobs:
        # print('Job %i:' % job_id)
        for op_id in range(len(jobs_data[job_id])):
            start_value = fjsp_model.Value(starts[(job_id, op_id)])
            machine = -1
            duration = -1
            selected = -1
            for machine_id in range(len(jobs_data[job_id][op_id])):
                if fjsp_model.Value(presences[(job_id, op_id, machine_id)]):
                    duration = jobs_data[job_id][op_id][machine_id][0]
                    machine = jobs_data[job_id][op_id][machine_id][1]
                    selected = machine_id
            # print(
            #     '  task_%i_%i starts at %i (alt %i, machine %i, duration %i)' %
            #     (job_id, op_id, start_value, selected, machine, duration))
            op_info = {
                'Order':        None,
                'job_id':       job_id,
                'op_id':        op_id,
                'machine_id':   machine,
                'start_time':   start_value,
                'process_time': duration,
                'finish_time':  start_value + duration,
                'job_type':     None,
            }
            result.append(op_info)
    return result


if __name__ == '__main__':
    # jsp_result = solve(in_file, time_limit=time_limit)
    # out_file = os.path.join(fn+'.json')
    out_file = 'sample.json'
    fjsp_result = solve()
    with open(out_file, 'w') as f:
        json.dump(fjsp_result, f, indent=4)
    
    # visualization
    logger = DJSP_Logger()
    plotter = DJSP_Plotter(logger)
    logger.load(out_file)
    print(logger)
    # plotter.plot_googlechart_timeline(os.path.json('timeline', fn+'.html'))
    plotter.plot_googlechart_timeline(os.path.join('sample.html'))