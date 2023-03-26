from ortools.sat.python import cp_model

def floorplanning(widths, heights, panel_width, panel_height):
    # Number of blocks
    n = len(widths)

    # Create the model
    model = cp_model.CpModel()

    # Variables
    x = [model.NewIntVar(0, panel_width - w, f'x{i}') for i, w in enumerate(widths)]
    y = [model.NewIntVar(0, panel_height - h, f'y{i}') for i, h in enumerate(heights)]
    x_e = [model.NewIntVar(-panel_width, panel_width, f'x_end{i}') for i in range(n)]
    y_e = [model.NewIntVar(-panel_height, panel_height, f'y_end{i}') for i in range(n)]

    # Constraints
    for i in range(n):
        # x_end = x + w
        model.Add(x_e[i] == x[i] + widths[i])
        # y_end = y + h
        model.Add(y_e[i] == y[i] + heights[i])

    # Non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            # Boolean variables for each constraint
            bx_ij = model.NewBoolVar(f'bx_{i}_{j}')
            bx_ji = model.NewBoolVar(f'bx_{j}_{i}')
            by_ij = model.NewBoolVar(f'by_{i}_{j}')
            by_ji = model.NewBoolVar(f'by_{j}_{i}')

            # Constraints
            model.Add(x_e[i] <= x[j] + panel_width * bx_ij)
            model.Add(x_e[j] <= x[i] + panel_width * bx_ji)
            model.Add(y_e[i] <= y[j] + panel_height * by_ij)
            model.Add(y_e[j] <= y[i] + panel_height * by_ji)

            # Use model.AddBoolOr() for each constraint
            model.AddBoolOr([bx_ij.Not(), bx_ji.Not(), by_ij.Not(), by_ji.Not()])

    # Objective function
    objective = model.NewIntVar(0, panel_width * panel_height, "objective")
    model.AddMaxEquality(objective, [x_e[i] for i in range(n)])
    model.Minimize(objective)

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Return the result
    if status == cp_model.OPTIMAL:
        positions = [(solver.Value(x[i]), solver.Value(y[i])) for i in range(n)]
        max_x = solver.Value(objective)
        max_y = max(solver.Value(y_e[i]) for i in range(n))
        return positions, max_x, max_y
    else:
        return None, None, None

# Input 1
# widths = [100, 200, 150, 100]
# heights = [100, 150, 100, 200]
# panel_width = 600
# panel_height = 600

# Input 2
widths = [100, 200, 150, 100, 600, 500, 400, 100, 50]
heights = [100, 150, 100, 200, 50, 100, 450, 200, 100]
panel_width = 600
panel_height = 600

# Input 3
# widths = [10,80,20,40,30,10,50,100,20,30,140,10,70,]
# heights = [20,30,60,50,40,80,60,20,20,30,90,80,20,]
# panel_width = 350
# panel_height = 90

positions, max_x, max_y = floorplanning(widths, heights, panel_width, panel_height)
print("Positions:", positions)
