import os
import json
import numpy as np
from ortools.sat.python import cp_model

def wafer_sampled(path):
    with open(path, 'r') as fp:
        data = json.load(fp)
    wafer_width = data["width"]
    wafer_height = data["height"]
    all_block = data["block"]
    # Number of blocks
    n = len(all_block)

    # Create the model
    model = cp_model.CpModel()

    # Variables
    all_x_st, all_y_st, all_x_ed, all_y_ed, sampled = [], [], [], [], []
    for i, block in enumerate(all_block):
        if block['x'] == None:
            all_x_st.append(model.NewIntVar(0, wafer_width - block['w'], f"x{i}"))
        else:
            all_x_st.append(model.NewIntVar(block['x'], block['x'], f"x{i}"))
        all_x_ed.append(model.NewIntVar(-wafer_width, wafer_width, f"x_end{i}"))

        if block['y'] == None:
            all_y_st.append(model.NewIntVar(0, wafer_height - block['h'], f"y{i}"))
        else:
            all_y_st.append(model.NewIntVar(block['y'], block['y'], f"y{i}"))
        all_y_ed.append(model.NewIntVar(-wafer_width, wafer_width, f"y_end{i}"))

        if block['x'] == None and block['y'] == None:
            sampled.append(model.NewBoolVar(f"sampled_{i}"))
        else:
            sampled.append(model.NewConstant(1))

    # width & height constraints
    for i, block in enumerate(all_block):
        model.Add(all_x_ed[i] == all_x_st[i] + block['w']).OnlyEnforceIf(sampled[i])
        model.Add(all_y_ed[i] == all_y_st[i] + block['h']).OnlyEnforceIf(sampled[i])
        model.Add(all_x_ed[i] <= wafer_width).OnlyEnforceIf(sampled[i])
        model.Add(all_y_ed[i] <= wafer_height).OnlyEnforceIf(sampled[i])

    # Non-overlapping constraints
    for i in range(n):
        for j in range(i + 1, n):
            bx_ij = model.NewBoolVar(f"bx_{i}_{j}")
            bx_ji = model.NewBoolVar(f"bx_{j}_{i}")
            by_ij = model.NewBoolVar(f"by_{i}_{j}")
            by_ji = model.NewBoolVar(f"by_{j}_{i}")

            model.Add(all_x_ed[i] <= all_x_st[j] + wafer_width * bx_ij)
            model.Add(all_x_ed[j] <= all_x_st[i] + wafer_width * bx_ji)
            model.Add(all_y_ed[i] <= all_y_st[j] + wafer_height * by_ij)
            model.Add(all_y_ed[j] <= all_y_st[i] + wafer_height * by_ji)

            model.AddBoolOr([bx_ij.Not(), bx_ji.Not(),
                            by_ij.Not(), by_ji.Not()])

    # Objective function
    wafer_area = wafer_width * wafer_height
    blocks_area = model.NewIntVar(0, wafer_area, "blocks_area")
    model.Add(
        blocks_area == sum(
            sampled[i] *
            block['w'] *
            block['h'] for i, block in enumerate(all_block)))
    num_blocks_sampled = model.NewIntVar(0, n, "num_blocks_sampled")
    model.Add(num_blocks_sampled == sum(sampled[i] for i, block in enumerate(all_block)))

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
    model.Maximize(wafer_coverage * (1 / scale))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print
    if status == cp_model.OPTIMAL:
        positions = [(solver.Value(all_x_st[i]), solver.Value(all_y_st[i]))
                     for i in range(n)]
        print(f"positions: {positions}\n"
              f"num_blocks_sampled: {solver.Value(num_blocks_sampled)}\n"
              f"sampled: {[solver.Value(sampled[i]) for i in range(n)]}\n"
              f"wafer_coverage: {solver.Value(wafer_coverage) / scale}\n"
              f"block_utilization: {solver.Value(block_utilization) / scale}\n"
              f"objective: {solver.ObjectiveValue()}")
        all_block_sampled = []
        for i, block in enumerate(all_block):
            if not solver.Value(sampled[i]):
                continue
            block['x'] = solver.Value(all_x_st[i])
            block['y'] = solver.Value(all_y_st[i])
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
    # file_name = "0004.json"
    file_name = "0005.json"
    # file_name = "0001_d=10.json"
    wafer_sampled(os.path.join(data_path, file_name))
