from ortools.linear_solver import pywraplp

def solve_weighted_set_cover(universe, subsets, weights):
    # Create a MILP solver with the CBC backend
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    # Define the decision variables
    x = {}
    for j in range(len(subsets)):
        x[j] = solver.IntVar(0, 1, 'x[%d]' % j)
        
    # Define the constraints
    for i in range(len(universe)):
        constraint = solver.RowConstraint(1, solver.infinity(), '')
        for j in range(len(subsets)):
            if universe[i] in subsets[j]:
                constraint.SetCoefficient(x[j], 1)
    
    # Define the objective function
    objective = solver.Objective()
    objective.SetMinimization()
    for j in range(len(subsets)):
        objective.SetCoefficient(x[j], weights[j])
        
    # Solve the problem
    time_limit = 1000  # Time limit in milliseconds
    solver.set_time_limit(time_limit)
    status = solver.Solve()
    
    # Check solution status and print solution
    if status == pywraplp.Solver.OPTIMAL:
        print('Optimal solution found.')
        print('Objective value =', solver.Objective().Value())
        for j in range(len(subsets)):
            if x[j].solution_value() > 0:
                print('Subset', j, ':', subsets[j], 'Weight:', weights[j])
    elif status == pywraplp.Solver.FEASIBLE:
        print('Feasible solution found, but not optimal.')
        print('Objective value =', solver.Objective().Value())
        for j in range(len(subsets)):
            if x[j].solution_value() > 0:
                print('Subset', j, ':', subsets[j], 'Weight:', weights[j])
    else:
        print('The solver could not find a feasible solution.')

if __name__ == '__main__':
    # universe = list(range(11))
    # subsets = [
    #     {0},
    #     {1, 2, 3, 4},
    #     {4, 5, 6},
    #     {7, 8, 9},
    #     {1, 2, 5, 6},
    #     {2, 3, 4, 5},
    #     {6, 7, 8, 9, 10}
    # ]
    # weights = [10, 3, 2, 1, 5, 4, 6]
    
    # universe = list(range(1, 6))
    # print(f"Universe: {universe}")
    # subsets = [
    #     {4,1,3},
    #     {2,5},
    #     {1,4,3,2},
    # ]
    # weights = [5, 10, 3]
    
    universe = list(range(1, 14))
    print(f"Universe: {set(universe)}")
    subsets = [
        {1, 2},
        {2, 3, 4, 5},
        {6, 7, 8, 9, 10, 11, 12, 13},
        {1, 3, 5, 7, 9, 11, 13},
        {2, 4, 6, 8, 10, 12, 13},
    ]
    weights = [1, 1, 1, 1, 1]

    solve_weighted_set_cover(universe, subsets, weights)
