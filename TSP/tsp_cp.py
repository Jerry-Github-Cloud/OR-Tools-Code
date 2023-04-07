import os 
from ortools.sat.python import cp_model

from loader import Loader

def solve(tsp_path, time_limit=60, num_thread=8):
    loader = Loader(tsp_path)
    weight_matrix = loader.get_weight_matrix()
    num_nodes = len(weight_matrix)
    all_nodes = range(num_nodes)
    # print('Num nodes =', num_nodes)

    # Model.
    model = cp_model.CpModel()

    obj_vars = []
    obj_coeffs = []

    # Create the circuit constraint.
    arcs = []
    arc_literals = {}
    for i in all_nodes:
        for j in all_nodes:
            if i == j:
                continue

            lit = model.NewBoolVar('%i follows %i' % (j, i))
            arcs.append([i, j, lit])
            arc_literals[i, j] = lit

            obj_vars.append(lit)
            obj_coeffs.append(weight_matrix[i][j])

    model.AddCircuit(arcs)

    # Minimize weighted sum of arcs. Because this s
    model.Minimize(
        sum(obj_vars[i] * obj_coeffs[i] for i in range(len(obj_vars))))

    # Solve and print out the solution.
    solver = cp_model.CpSolver()
    # time limit
    solver.parameters.max_time_in_seconds = time_limit
    # number of threads
    solver.parameters.num_workers = num_thread
    solver.parameters.log_search_progress = False
    # To benefit from the linearization of the circuit constraint.
    solver.parameters.linearization_level = 2

    status = solver.Solve(model)
    # print(solver.ResponseStats())

    current_node = 0
    str_route = '%i' % current_node
    route_is_finished = False
    tour_cost = 0
    while not route_is_finished:
        for i in all_nodes:
            if i == current_node:
                continue
            if solver.BooleanValue(arc_literals[current_node, i]):
                str_route += ' -> %i' % i
                tour_cost += weight_matrix[current_node][i]
                current_node = i
                if current_node == 0:
                    route_is_finished = True
                break
    # print('Route:', str_route)
    # print('Travelled distance:', route_distance)
    print(f"{tsp_path}\t"
          f"{loader.num_node}\t"
          f"{tour_cost}\t"
          f"{round(solver.WallTime(), 2)}\t"
          f"{bool(status == cp_model.OPTIMAL)}\t")


if __name__ == '__main__':
    # tsp_path = "ALL_tsp/a280.tsp"
    # tsp_path = "ALL_tsp/att48.tsp"
    # tsp_path = "ALL_tsp/berlin52.tsp"
    # tsp_path = "ALL_tsp/bays29.tsp"
    # tsp_path = "ALL_tsp/gr96.tsp"
    # solve(tsp_path)
    
    tsp_dir = "ALL_tsp"
    for tsp_file in os.listdir(tsp_dir):
        name, ext = os.path.splitext(tsp_file)
        if ext == ".tsp":
            tsp_path = os.path.join(tsp_dir, tsp_file)
            loader = Loader(tsp_path)
            solve(tsp_path)
