import os
import json
import numpy as np
from ortools.sat.python import cp_model

def solve(all_block, wafer_width, wafer_height):
    ### wafer sampling
    # Number of blocks
    n = len(all_block)
    print(f"n: {n}")

    # wafer Variables
    all_wafer_x_st, all_wafer_y_st, all_wafer_x_ed, all_wafer_y_ed, sampled, all_ng = [], [], [], [], [], []
    for i, block in enumerate(all_block):
        if block['x'] == None:
            all_wafer_x_st.append(model.NewIntVar(0, wafer_width - block['w'], f"wafer_x{i}"))
        else:
            all_wafer_x_st.append(model.NewIntVar(block['x'], block['x'], f"wafer_x{i}"))
        all_wafer_x_ed.append(model.NewIntVar(-wafer_width, wafer_width, f"wafer_x_end{i}"))

        if block['y'] == None:
            all_wafer_y_st.append(model.NewIntVar(0, wafer_height - block['h'], f"wafer_y{i}"))
        else:
            all_wafer_y_st.append(model.NewIntVar(block['y'], block['y'], f"wafer_y{i}"))
        all_wafer_y_ed.append(model.NewIntVar(-wafer_height, wafer_height, f"wafer_y_end{i}"))

        if block['x'] == None and block['y'] == None:
            sampled.append(model.NewBoolVar(f"sampled_{i}"))
        else:
            sampled.append(model.NewConstant(1))
        if block['ng']:
            all_ng.append(model.NewConstant(1))
        else:
            all_ng.append(model.NewConstant(0))

    # wafer width & height constraints
    for i, block in enumerate(all_block):
        model.Add(all_wafer_x_ed[i] == all_wafer_x_st[i] + block['w']).OnlyEnforceIf(sampled[i])
        model.Add(all_wafer_y_ed[i] == all_wafer_y_st[i] + block['h']).OnlyEnforceIf(sampled[i])
        model.Add(all_wafer_x_ed[i] <= wafer_width).OnlyEnforceIf(sampled[i])
        model.Add(all_wafer_y_ed[i] <= wafer_height).OnlyEnforceIf(sampled[i])

    # wafer Non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            wafer_bx_ij = model.NewBoolVar(f"wafer_bx_{i}_{j}")
            wafer_bx_ji = model.NewBoolVar(f"wafer_bx_{j}_{i}")
            wafer_by_ij = model.NewBoolVar(f"wafer_by_{i}_{j}")
            wafer_by_ji = model.NewBoolVar(f"wafer_by_{j}_{i}")

            model.Add(all_wafer_x_ed[i] <= all_wafer_x_st[j] + wafer_width * wafer_bx_ij)
            model.Add(all_wafer_x_ed[j] <= all_wafer_x_st[i] + wafer_width * wafer_bx_ji)
            model.Add(all_wafer_y_ed[i] <= all_wafer_y_st[j] + wafer_height * wafer_by_ij)
            model.Add(all_wafer_y_ed[j] <= all_wafer_y_st[i] + wafer_height * wafer_by_ji)

            model.AddBoolOr([wafer_bx_ij.Not(), wafer_bx_ji.Not(),
                            wafer_by_ij.Not(), wafer_by_ji.Not()])

    ### place to sample panel
    panel_width = 6
    panel_height = 6
    # panel Variables
    all_panel_x_st, all_panel_y_st, all_panel_x_ed, all_panel_y_ed, on_panel = [], [], [], [], []
    for i, block in enumerate(all_block):
        all_panel_x_st.append(model.NewIntVar(0, panel_width - block['w'], f"panel_x{i}"))
        all_panel_x_ed.append(model.NewIntVar(-panel_width, panel_width, f"panel_x_end{i}"))
        all_panel_y_st.append(model.NewIntVar(0, panel_height - block['h'], f"panel_y{i}"))
        all_panel_y_ed.append(model.NewIntVar(-panel_height, panel_height, f"panel_y_end{i}"))
        on_panel.append(model.NewBoolVar(f"on_panel_{i}"))
    
    # exclude ng
    for i, block in enumerate(all_block):
        model.AddBoolAnd([sampled[i], all_ng[i].Not()]).OnlyEnforceIf(on_panel[i])
    # panel width & height constraints
    
    for i, block in enumerate(all_block):
        model.Add(all_panel_x_ed[i] == all_panel_x_st[i] + block['w']).OnlyEnforceIf(on_panel[i])
        model.Add(all_panel_y_ed[i] == all_panel_y_st[i] + block['h']).OnlyEnforceIf(on_panel[i])
        model.Add(all_panel_x_ed[i] <= panel_width).OnlyEnforceIf(on_panel[i])
        model.Add(all_panel_y_ed[i] <= panel_height).OnlyEnforceIf(on_panel[i])
    
    # panel Non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            panel_bx_ij = model.NewBoolVar(f"panel_bx_{i}_{j}")
            panel_bx_ji = model.NewBoolVar(f"panel_bx_{j}_{i}")
            panel_by_ij = model.NewBoolVar(f"panel_by_{i}_{j}")
            panel_by_ji = model.NewBoolVar(f"panel_by_{j}_{i}")

            model.Add(all_panel_x_ed[i] <= all_panel_x_st[j] + panel_width * panel_bx_ij)
            model.Add(all_panel_x_ed[j] <= all_panel_x_st[i] + panel_width * panel_bx_ji)
            model.Add(all_panel_y_ed[i] <= all_panel_y_st[j] + panel_height * panel_by_ij)
            model.Add(all_panel_y_ed[j] <= all_panel_y_st[i] + panel_height * panel_by_ji)

            model.AddBoolOr([panel_bx_ij.Not(), panel_bx_ji.Not(),
                            panel_by_ij.Not(), panel_by_ji.Not()])

    # panel must be filled by blocks
    model.Add(sum(on_panel[i] * block['w'] * block['h'] for i, block in enumerate(all_block)) == panel_width * panel_height)

    # Objective function
    wafer_area = wafer_width * wafer_height
    blocks_area = model.NewIntVar(0, wafer_area, "blocks_area")
    model.Add(
        blocks_area == sum(
            on_panel[i] *
            block['w'] *
            block['h'] for i, block in enumerate(all_block)))
    num_blocks_sampled = model.NewIntVar(0, n, "num_blocks_sampled")
    model.Add(num_blocks_sampled == sum(on_panel[i] for i, block in enumerate(all_block)))

    scale = 1000000
    # wafer_coverage
    wafer_coverage = model.NewIntVar(0, 1 * scale, "wafer_coverage")
    model.AddDivisionEquality(wafer_coverage, blocks_area * scale, wafer_area)

    # block utilization
    block_utilization = model.NewIntVar(0, 1 * scale, "block_utilization")
    model.AddDivisionEquality(
        block_utilization,
        num_blocks_sampled * scale,
        n)

    # model.Maximize(wafer_coverage * (1 / scale) - 
    #                block_utilization * (1 / scale))
    # model.Maximize(wafer_coverage * (1 / scale))
    model.Maximize(-block_utilization * (1 / scale))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print
    if status == cp_model.OPTIMAL:
        block_positions_on_wafer = [(solver.Value(all_wafer_x_st[i]), solver.Value(all_wafer_y_st[i]))
                     for i in range(n) if solver.Value(on_panel[i])]
        block_positions_on_panel = [(solver.Value(all_panel_x_st[i]), solver.Value(all_panel_y_st[i]))
                     for i in range(n) if solver.Value(on_panel[i])]
        print(f"block_positions_on_wafer: {block_positions_on_wafer}\n"
              f"block_positions_on_panel: {block_positions_on_panel}\n"
              f"num_blocks_sampled: {solver.Value(num_blocks_sampled)}\n"
            #   f"sampled: {[solver.Value(sampled[i]) for i in range(n)]}\n"
            #   f"on_panel: {[solver.Value(on_panel[i]) for i in range(n)]}\n"
              f"blocks_on_panel: {[(block['w'], block['h']) for i, block in enumerate(all_block) if solver.Value(on_panel[i])]}\n"
              f"wafer_coverage: {solver.Value(wafer_coverage) / scale}\n"
              f"block_utilization: {solver.Value(block_utilization) / scale}\n"
              f"objective: {solver.ObjectiveValue()}")
        all_block_sampled = []
        for i, block in enumerate(all_block):
            if not solver.Value(sampled[i]):
                continue
            block['x'] = solver.Value(all_wafer_x_st[i])
            block['y'] = solver.Value(all_wafer_y_st[i])
            all_block_sampled.append(block)
        result = {}
        result['width'] = wafer_width
        result['height'] = wafer_height
        result["block"] = all_block_sampled
        with open(os.path.join(result_path, file_name), 'w') as fp:
            json.dump(result, fp, indent=4)
    elif cp_model.INFEASIBLE:
        print("INFEASIBLE")


if __name__ == "__main__":
    data_path = "block_data"
    result_path = "result"
    file_name = "0003.json"
    # file_name = "0005.json"
    # file_name = "0001_d=10.json"
    # Create the model
    model = cp_model.CpModel()
    with open(os.path.join(data_path, file_name), 'r') as fp:
        data = json.load(fp)
    wafer_width = data["width"]
    wafer_height = data["height"]
    all_block = data["block"]
    solve(all_block, wafer_width, wafer_height)
