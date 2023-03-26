from ortools.sat.python import cp_model


def solve(widths, heights, panel_width, panel_height, selected_blocks=None):
    # Number of blocks
    n = len(widths)

    # Create the model
    model = cp_model.CpModel()

    # Variables
    x = [
        model.NewIntVar(
            0,
            panel_width - w,
            f'x{i}') for i,
        w in enumerate(widths)]
    y = [
        model.NewIntVar(
            0,
            panel_height - h,
            f'y{i}') for i,
        h in enumerate(heights)]
    x_e = [model.NewIntVar(-panel_width, panel_width,
                           f'x_end{i}') for i in range(n)]
    y_e = [model.NewIntVar(-panel_height, panel_height,
                           f'y_end{i}') for i in range(n)]
    on_panel = [model.NewBoolVar(f'on_panel_{i}') for i in range(n)]

    # Constraints
    for i in range(n):
        # x_end = x + w
        model.Add(x_e[i] == x[i] + widths[i]).OnlyEnforceIf(on_panel[i])
        # y_end = y + h
        model.Add(y_e[i] == y[i] + heights[i]).OnlyEnforceIf(on_panel[i])
        # Block is on panel if on_panel[i] is True
        # model.AddImplication(on_panel[i], x_e[i] <= panel_width)
        # model.AddImplication(on_panel[i], y_e[i] <= panel_height)
        model.Add(x_e[i] <= panel_width).OnlyEnforceIf(on_panel[i])
        model.Add(y_e[i] <= panel_height).OnlyEnforceIf(on_panel[i])

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
            model.AddBoolOr([bx_ij.Not(), bx_ji.Not(),
                            by_ij.Not(), by_ji.Not()])

    # Objective function
    panel_area = panel_width * panel_height
    blocks_area = model.NewIntVar(0, panel_area, "blocks_area")
    model.Add(
        blocks_area == sum(
            on_panel[i] *
            widths[i] *
            heights[i] for i in range(n)))
    num_blocks_on_panel = model.NewIntVar(0, n, "num_blocks_on_panel")
    model.Add(num_blocks_on_panel == sum(on_panel[i] for i in range(n)))

    scale = 1000000
    # panel_coverage
    panel_coverage = model.NewIntVar(0, 1 * scale, "panel_coverage")
    model.AddDivisionEquality(panel_coverage, blocks_area * scale, panel_area)

    # block utilization
    block_utilization = model.NewIntVar(0, 1 * scale, "block_utilization")
    model.AddDivisionEquality(
        block_utilization,
        num_blocks_on_panel *
        scale,
        n)

    model.Maximize(panel_coverage * (1 / scale) - 
                   block_utilization * (1 / scale))
    # model.Maximize(panel_coverage * (1 / scale))

    # Constraints on selected blocks
    if selected_blocks is not None:
        for i in selected_blocks:
            model.Add(on_panel[i])

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Return the result
    if status == cp_model.OPTIMAL:
        positions = [(solver.Value(x[i]), solver.Value(y[i]))
                     for i in range(n)]
        on_panel = [solver.Value(on_panel[i]) for i in range(n)]
        print(f"positions: {positions}\n"
              f"num_blocks_on_panel: {solver.Value(num_blocks_on_panel)}\n"
              f"on_panel: {[solver.Value(on_panel[i]) for i in range(n)]}\n"
              f"panel_coverage: {solver.Value(panel_coverage) / scale}\n"
              f"block_utilization: {solver.Value(block_utilization) / scale}\n")
    elif cp_model.INFEASIBLE:
        print("INFEASIBLE")


if __name__ == "__main__":
    # Input 1
    # widths = [100, 200, 150, 100]
    # heights = [100, 150, 100, 200]
    # panel_width = 600
    # panel_height = 600

    # # Input 2
    # widths = [100, 200, 150, 100, 600, 500, 400, 100, 50]
    # heights = [100, 150, 100, 200, 50, 100, 450, 200, 100]
    # panel_width = 600
    # panel_height = 600

    # Input 3
    widths =    [1, 2, 3, 5, 3, 2, 3, 3,]
    heights =   [5, 4, 3, 1, 1, 2, 5, 2,]
    panel_width = 6
    panel_height = 6

    solve(widths, heights, panel_width, panel_height)
