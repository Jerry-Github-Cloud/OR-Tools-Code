import numpy as np
from ortools.sat.python import cp_model

def solve(all_block, panel_width, panel_height):
    # Number of blocks
    n = len(all_block)

    # Create the model
    model = cp_model.CpModel()

    # Variables
    all_x_st, all_y_st, all_x_ed, all_y_ed, on_panel = [], [], [], [], []
    for i, block in enumerate(all_block):
        if block['x'] == None:
            all_x_st.append(model.NewIntVar(0, panel_width - block['w'], f"x{i}"))
        else:
            all_x_st.append(model.NewIntVar(block['x'], block['x'], f"x{i}"))
        all_x_ed.append(model.NewIntVar(-panel_width, panel_width, f"x_end{i}"))

        if block['y'] == None:
            all_y_st.append(model.NewIntVar(0, panel_height - block['h'], f"y{i}"))
        else:
            all_y_st.append(model.NewIntVar(block['y'], block['y'], f"y{i}"))
        all_y_ed.append(model.NewIntVar(-panel_width, panel_width, f"y_end{i}"))

        if block['x'] == None and block['y'] == None:
            on_panel.append(model.NewBoolVar(f"on_panel_{i}"))
        else:
            on_panel.append(model.NewConstant(1))

    # width & height constraints
    for i, block in enumerate(all_block):
        model.Add(all_x_ed[i] == all_x_st[i] + block['w']).OnlyEnforceIf(on_panel[i])
        model.Add(all_y_ed[i] == all_y_st[i] + block['h']).OnlyEnforceIf(on_panel[i])
        model.Add(all_x_ed[i] <= panel_width).OnlyEnforceIf(on_panel[i])
        model.Add(all_y_ed[i] <= panel_height).OnlyEnforceIf(on_panel[i])

    # Non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            bx_ij = model.NewBoolVar(f'bx_{i}_{j}')
            bx_ji = model.NewBoolVar(f'bx_{j}_{i}')
            by_ij = model.NewBoolVar(f'by_{i}_{j}')
            by_ji = model.NewBoolVar(f'by_{j}_{i}')

            model.Add(all_x_ed[i] <= all_x_st[j] + panel_width * bx_ij)
            model.Add(all_x_ed[j] <= all_x_st[i] + panel_width * bx_ji)
            model.Add(all_y_ed[i] <= all_y_st[j] + panel_height * by_ij)
            model.Add(all_y_ed[j] <= all_y_st[i] + panel_height * by_ji)

            model.AddBoolOr([bx_ij.Not(), bx_ji.Not(),
                            by_ij.Not(), by_ji.Not()])

    # Objective function
    panel_area = panel_width * panel_height
    blocks_area = model.NewIntVar(0, panel_area, "blocks_area")
    model.Add(
        blocks_area == sum(
            on_panel[i] *
            block['w'] *
            block['h'] for i, block in enumerate(all_block)))
    num_blocks_on_panel = model.NewIntVar(0, n, "num_blocks_on_panel")
    model.Add(num_blocks_on_panel == sum(on_panel[i] for i, block in enumerate(all_block)))

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

    # model.Maximize(panel_coverage * (1 / scale) - 
    #                block_utilization * (1 / scale))
    model.Maximize(panel_coverage * (1 / scale))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print the result
    if status == cp_model.OPTIMAL:
        positions = [(solver.Value(all_x_st[i]), solver.Value(all_y_st[i]))
                     for i in range(n)]
        on_panel = [solver.Value(on_panel[i]) for i in range(n)]
        print(f"positions: {positions}\n"
              f"num_blocks_on_panel: {solver.Value(num_blocks_on_panel)}\n"
              f"on_panel: {[solver.Value(on_panel[i]) for i in range(n)]}\n"
              f"panel_coverage: {solver.Value(panel_coverage) / scale}\n"
              f"block_utilization: {solver.Value(block_utilization) / scale}\n"
              f"objective: {solver.ObjectiveValue()}")
    elif cp_model.INFEASIBLE:
        print("INFEASIBLE")


def generate_circle_matrix(size):
    if size % 2 == 0:
        size += 1 

    matrix = np.zeros((size, size), dtype=int)
    radius = size // 2

    for i in range(size):
        for j in range(size):
            if (i - radius) ** 2 + (j - radius) ** 2 <= radius ** 2:
                matrix[i][j] = 1

    return matrix


def generate_wafer(diameter):
    # matrix = generate_circle_matrix(diameter)
    matrix = np.ones((diameter, diameter), dtype=int)
    matrix[0, 0] = 0
    matrix[0, 1] = 0
    matrix[0, 2] = 0
    matrix[1, 0] = 0
    matrix[2, 0] = 0
    matrix[1, 1] = 0


def wafer2blocks(wafer):
    pass

if __name__ == "__main__":
    # Input 1
    # all_block = [
    #     {"w": 1, "h": 5, "x": None, "y": None}, 
    #     {"w": 2, "h": 4, "x": None, "y": None}, 
    #     {"w": 3, "h": 3, "x": None, "y": None}, 
    #     {"w": 5, "h": 1, "x": None, "y": None}, 
    #     {"w": 3, "h": 1, "x": None, "y": None}, 
    #     {"w": 2, "h": 2, "x": None, "y": None}, 
    #     {"w": 3, "h": 5, "x": None, "y": None}, 
    #     {"w": 3, "h": 2, "x": None, "y": None}, 
    # ]
    # panel_width = 6
    # panel_height = 6
    # solve(all_block, panel_width, panel_height)

    # Input 2
    all_block = [
        {"w": 2, "h": 2, "x": 0, "y": 0, "border": True}, 
        {"w": 1, "h": 1, "x": 0, "y": 2, "border": True}, 
        {"w": 1, "h": 1, "x": 2, "y": 0, "border": True}, 
        {"w": 2, "h": 2, "x": 0, "y": 8, "border": True}, 
        {"w": 1, "h": 1, "x": 0, "y": 7, "border": True}, 
        {"w": 1, "h": 1, "x": 2, "y": 9, "border": True}, 
        {"w": 2, "h": 2, "x": 8, "y": 0, "border": True}, 
        {"w": 1, "h": 1, "x": 7, "y": 0, "border": True}, 
        {"w": 1, "h": 1, "x": 9, "y": 2, "border": True}, 
        {"w": 2, "h": 2, "x": 8, "y": 8, "border": True}, 
        {"w": 1, "h": 1, "x": 9, "y": 7, "border": True}, 
        {"w": 1, "h": 1, "x": 7, "y": 9, "border": True}, 
        {"w": 1, "h": 1, "x": 2, "y": 3, "border": True}, 
        {"w": 1, "h": 1, "x": 3, "y": 7, "border": True}, 
        {"w": 1, "h": 1, "x": 4, "y": 4, "border": True}, 
        {"w": 1, "h": 1, "x": 5, "y": 5, "border": True}, 
        {"w": 2, "h": 1, "x": 6, "y": 3, "border": True}, 
        {"w": 1, "h": 1, "x": 8, "y": 5, "border": True}, 
        {"w": 2, "h": 2, "x": None, "y": None, "border": False}, 
        {"w": 1, "h": 5, "x": None, "y": None, "border": False}, 
        {"w": 2, "h": 4, "x": None, "y": None, "border": False}, 
        {"w": 3, "h": 3, "x": None, "y": None, "border": False}, 
        {"w": 5, "h": 1, "x": None, "y": None, "border": False},
        {"w": 3, "h": 1, "x": None, "y": None, "border": False},  
        {"w": 2, "h": 2, "x": None, "y": None, "border": False}, 
        {"w": 3, "h": 5, "x": None, "y": None, "border": False}, 
    ]
    panel_width = 10
    panel_height = 10
    solve(all_block, panel_width, panel_height)
