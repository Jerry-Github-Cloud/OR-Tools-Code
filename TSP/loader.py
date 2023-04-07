import os
import tsplib95
import numpy as np

class Loader:
    def __init__(self, path):
        self.problem = tsplib95.load(path)
        self.num_node = len(list(self.problem.get_nodes()))
        self.nodes = [list(self.problem.get_nodes())]

    def load_tour(self, path):
        tour = tsplib95.load(path)
        # print(f"tour.tours: {tour.tours}")
        # print(f"self.nodes: {self.nodes}")
        print(f"tour cost: {self.problem.trace_tours(tour.tours)}")
        # print(f"canonical tour cost: {self.problem.trace_tours(self.nodes)}")
        # print(f"trace_canonical_tour: {self.problem.trace_canonical_tour()}")

    def check_tsp_instance(self):
        print(self.problem.name)
        print(f"edge_weight_type: {self.problem.edge_weight_type}")
        print(f"is_symmetric: {self.problem.is_symmetric()}")
        print(f"is_weighted: {self.problem.is_weighted()}")
        print(f"is_special: {self.problem.is_special()}")
        print(f"is_explicit: {self.problem.is_explicit()}")

    def print_weight(self, start, end):
        print(f"weight between node {start} {self.problem.node_coords[start]} "
            f"and node {end} {self.problem.node_coords[end]}: "
            f"{self.problem.get_weight(start, end)}")

    def get_weight_matrix(self):
        weight_matrix = np.zeros((self.num_node, self.num_node))
        for start in self.problem.get_nodes():
            for end in self.problem.get_nodes():
                weight_matrix[start - 1, end - 1] = self.problem.get_weight(start, end)
        return weight_matrix

if __name__ == "__main__":
    # tsp_path = "ALL_tsp/a280.tsp"
    # loader = Loader(tsp_path)
    # loader.check_tsp_instance()
    # loader.print_weight(100, 200)
    # loader.print_weight(1, 3)

    # tour_path = "ALL_tsp/a280.opt.tour"
    # loader.load_tour(tour_path)
    # weight_matrix = loader.get_weight_matrix()
    # print(weight_matrix)
    
    tsp_dir = "ALL_tsp"
    for tsp_file in os.listdir(tsp_dir):
        name, ext = os.path.splitext(tsp_file)
        if ext == ".tsp":
            loader = Loader(os.path.join(tsp_dir, tsp_file))
            print(f"{name}\t{loader.num_node}")
