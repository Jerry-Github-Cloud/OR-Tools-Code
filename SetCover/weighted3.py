from ortools.sat.python import cp_model

def set_cover(universe, time_limit):
    model = cp_model.CpModel()

    # 定义变量
    num_subsets = len(universe)
    num_elements = len(universe[0])
    subsets = [model.NewBoolVar(f'subset{i}') for i in range(num_subsets)]
    elements_covered = [model.NewBoolVar(f'element{i}') for i in range(num_elements)]

    # 定义约束条件
    for j in range(num_elements):
        model.Add(sum([subsets[i] * universe[i][j] for i in range(num_subsets)]) >= elements_covered[j])

    for i in range(num_subsets):
        model.Add(sum([universe[i][j] * elements_covered[j] for j in range(num_elements)]) >= subsets[i])

    # 定义目标函数
    model.Maximize(sum(subsets))

    # 添加互斥约束条件
    for i in range(num_subsets):
        for j in range(i+1, num_subsets):
            model.Add(sum([subsets[i], subsets[j]]) <= 1)

    # 设置求解器
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit

    # 求解模型
    status = solver.Solve(model)

    # 输出结果
    if status == cp_model.OPTIMAL:
        num_subsets_used = sum([solver.Value(subsets[i]) for i in range(num_subsets)])
        subset_sizes = [sum(universe[i]) for i in range(num_subsets)]
        used_subsets = [i for i in range(num_subsets) if solver.Value(subsets[i])]
        elements_covered = [i for i in range(num_elements) if solver.Value(elements_covered[i])]
        return (num_subsets_used, subset_sizes, used_subsets, elements_covered)
    else:
        return None



universe = [
    [0,0,0],
    [1,1,0],
    [0,0,0],
    [0,1,1],
    [0,0,0]]

print(set_cover(universe, 1000))

# num_subsets, num_elements, covered_elements = set_cover(universe, 1000)
# print(f'Number of subsets selected: {num_subsets}')
# print(f'Number of elements in each subset: {num_elements}')
# print(f'Number of elements covered: {len(covered_elements)}')
