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

def solve(file_name, jobs_due , time_limit=10.0):
  """Minimal jobshop problem."""
  # Data.
#   jobs_data = [  # task = (machine_id, processing_time).
#     [(0, 3), (1, 2), (2, 2)],  # Job 0
#     [(0, 2), (2, 1), (1, 4)],  # Job 1
#     [(1, 4), (2, 3)]           # Job 2
#   ]
  jobs_data = load_instance(file_name)

#   jobs_due = [20, 5, 10]

  assert(len(jobs_data) == len(jobs_due))

  machines_count = 1 + max(task[0] for job in jobs_data for task in job)
  all_machines = range(machines_count)
  # Compute horizon dynamically as the sum of all durations.
  horizon = sum(task[1] for job in jobs_data for task in job)

  # Create the model.
  model = cp_model.CpModel()

  # Named tuple to store information about created variables.
  task_type = collections.namedtuple('task_type', 'start end interval')
  # Named tuple to manipulate solution information.
  assigned_task_type = collections.namedtuple('assigned_task_type', 'start job index duration')

  # Create job intervals and add to the corresponding machine lists.
  all_tasks = {}
  machine_to_intervals = collections.defaultdict(list)

  for job_id, job in enumerate(jobs_data):
    for task_id, task in enumerate(job):
      machine = task[0]
      duration = task[1]
      suffix = f'_{job_id}_{task_id}'
      start_var = model.NewIntVar(0, horizon, 'start' + suffix)
      end_var = model.NewIntVar(0, horizon, 'end' + suffix)
      interval_var = model.NewIntervalVar(start_var, duration, end_var, 'interval' + suffix)
      all_tasks[job_id, task_id] = task_type(start=start_var, end=end_var, interval=interval_var)
      machine_to_intervals[machine].append(interval_var)
  
  # Create and add disjunctive constraints.
  for machine in all_machines:
    model.AddNoOverlap(machine_to_intervals[machine])
  
  # Precedences inside a job.
  for job_id, job in enumerate(jobs_data):
    for task_id in range(len(job) - 1):
      model.Add(all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end)
  
  # Makespan objective.
  makespan_var = model.NewIntVar(0, horizon, 'makespan')
  model.AddMaxEquality(makespan_var, [
    all_tasks[job_id, len(job) - 1].end
    for job_id, job in enumerate(jobs_data)
  ])

  # Tardiness objective.
  tardiness_var = 0
  delays = []
  for job_id, job in enumerate(jobs_data):
    due = jobs_due[job_id]
    end = all_tasks[job_id, len(job) - 1].end

    delay_var = model.NewIntVar(0, horizon, f'delay_{job_id}')
    model.AddMaxEquality(delay_var, [(end - due), 0])
    delays.append(delay_var)
    tardiness_var += delay_var

#   obj_var = makespan_var + tardiness_var
    obj_var = tardiness_var
  model.Minimize(obj_var)

  # Create the solver and solve.
  solver = cp_model.CpSolver()
  solver.parameters.max_time_in_seconds = time_limit
  status = solver.Solve(model)

  if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('Solution:')
    # Create on elist of assigned tasks per machine.
    assigned_jobs = collections.defaultdict(list)
    for job_id, job in enumerate(jobs_data):
      for task_id, task in enumerate(job):
        machine = task[0]
        assigned_jobs[machine].append(
          assigned_task_type(
            start=solver.Value(
              all_tasks[job_id, task_id].start),
            job=job_id,
            index=task_id,
            duration=task[1]
          )
        )
    
    # Create per machine output lines.
    output = ''
    result = []
    for machine in all_machines:
      # Sort by starting time.
      assigned_jobs[machine].sort()
      sol_line_tasks = 'Machine ' + str(machine) + ': '
      sol_line = '           '

      for assigned_task in assigned_jobs[machine]:
        name = f'job_{assigned_task.job}_task_{assigned_task.index}'
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
        sol_line_tasks += f'{name:15s}'

        start = assigned_task.start
        duration = assigned_task.duration
        sol_tmp = f'[{start},{start + duration}]'
        # Add spaces to output to align columns.
        sol_line += f'{sol_tmp:15s}'
      
      sol_line += '\n'
      sol_line_tasks += '\n'
      output += sol_line_tasks
      output += sol_line
    
    # Finally print the solution found.
    print(f'Optimal Schedule Objective: {solver.ObjectiveValue()}')
    print(f'                 Tardiness: {solver.Value(tardiness_var)}')
    print(f'                 Makespan:  {solver.Value(makespan_var)}')
    print(output)
  else:
    print('No solution found.')
  return result
  
  # Statistics.
  print('\nStatistics')
  print(f'  - conflicts: {solver.NumConflicts()}')
  print(f'  - branches : {solver.NumBranches()}')
  print(f'  - wall time: {solver.WallTime():f} s')


if __name__ == '__main__':
    in_file = 'easy1'
    # in_file = 'abz5'
    fn, _ = os.path.splitext(in_file)
    time_limit = 60     # in second
    jobs_due = [10, 5, 10]
    jsp_result = solve(in_file, jobs_due, time_limit=time_limit)
    out_file = os.path.join(fn+'.json')
    with open(out_file, 'w') as f:
        json.dump(jsp_result, f, indent=4)

    # visualization
    logger = DJSP_Logger()
    plotter = DJSP_Plotter(logger)
    logger.load(out_file)
    print(logger)
    # plotter.plot_googlechart_timeline(os.path.json('timeline', fn+'.html'))
    plotter.plot_googlechart_timeline(os.path.join('timeline', fn+'_tardiness.html'))