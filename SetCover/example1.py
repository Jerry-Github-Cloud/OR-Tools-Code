from ortools.linear_solver import pywraplp

def solve_set_cover(universe, subsets):
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
        objective.SetCoefficient(x[j], 1)
        
    # Solve the problem
    status = solver.Solve()
    
    # Check solution status and print solution
    if status == pywraplp.Solver.OPTIMAL:
        print('Optimal solution found.')
        print('Objective value =', solver.Objective().Value())
        for j in range(len(subsets)):
            if x[j].solution_value() > 0:
                print('Subset', j, ':', subsets[j])
    elif status == pywraplp.Solver.FEASIBLE:
        print('Feasible solution found, but not optimal.')
        print('Objective value =', solver.Objective().Value())
        for j in range(len(subsets)):
            if x[j].solution_value() > 0:
                print('Subset', j, ':', subsets[j])
    else:
        print('The solver could not find a feasible solution.')

if __name__ == '__main__':
    # universe = list(range(11))
    # print(f"Universe: {universe}")
    # subsets = [
    #     {1, 2, 3, 4},
    #     {4, 5, 6},
    #     {7, 8, 9},
    #     {1, 2, 5, 6},
    #     {2, 3, 4, 5},
    #     {6, 7, 8, 9, 10}
    # ]
    
    # universe = list(range(1, 6))
    # print(f"Universe: {universe}")
    # subsets = [
    #     {1, 2, 3},
    #     {2, 4},
    #     {3, 4},
    #     {4, 5},
    # ]


    solve_set_cover(universe, subsets)
