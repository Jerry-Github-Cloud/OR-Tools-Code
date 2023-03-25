from ortools.linear_solver import pywraplp
import numpy as np

def solve_weighted_set_cover_binary(universe, subsets):
    # Convert the universe set and subsets to binary matrices
    universe_mat = np.zeros((len(universe), len(universe)))
    for i in range(len(universe)):
        for j in range(len(universe)):
            if universe[j] in subsets[i]:
                universe_mat[i, j] = 1
    subset_weights = np.sum(universe_mat, axis=1)
    
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
            if universe_mat[i][j] == 1:
                constraint.SetCoefficient(x[j], 1)
    
    # Define the objective function
    objective = solver.Objective()
    objective.SetMinimization()
    for j in range(len(subsets)):
        objective.SetCoefficient(x[j], subset_weights[j])
        
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
                print('Subset', j, ':', subsets[j], 'Weight:', subset_weights[j])
    elif status == pywraplp.Solver.FEASIBLE:
        print('Feasible solution found, but not optimal.')
        print('Objective value =', solver.Objective().Value())
        for j in range(len(subsets)):
            if x[j].solution_value() > 0:
                print('Subset', j, ':', subsets[j], 'Weight:', subset_weights[j])
    else:
        print('The solver could not find a feasible solution.')

if __name__ == '__main__':
    universe = set(range(1, 11))
    subsets = [
        {1, 2, 3, 4},
        {4, 5, 6},
        {7, 8, 9},
        {1, 2, 5, 6},
        {2, 3, 4, 5},
        {6, 7, 8, 9, 10}
    ]

    solve_weighted_set_cover_binary(universe, subsets)
