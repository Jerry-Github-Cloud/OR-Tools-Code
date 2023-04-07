import os
import math
import tsplib95
import numpy as np
import networkx as nx

from plotter import Plotter

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
        # print(f"self.problem.get_nodes(): {list(self.problem.get_nodes())}")
        for start in self.problem.get_nodes():
            for end in self.problem.get_nodes():
                weight_matrix[start - 1, end - 1] = self.problem.get_weight(start, end) * 10
                # print(f"{self.nodes[start]}\t{self.nodes[end]}")
                # weight_matrix[start, end] = tsplib95.distances.euclidean(
                #     self.problem.node_coords[start], self.problem.node_coords[end])
                # weight_matrix[start-1, end-1] = self.distance(self.problem.node_coords[start], self.problem.node_coords[end])
        return weight_matrix

    def distance(self, start, end):
        return math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)

    def plot(self, html_name):
        nx_graph = self.problem.get_graph()
        plotter = Plotter(nx_graph)
        # plotter.plot_bokeh_scatter(html_name)
        plotter.plot_pyviz_network(html_name)


if __name__ == "__main__":
    tsp_path = "../TSP/ALL_tsp/a280.tsp"
    loader = Loader(tsp_path)
    loader.plot("out/a280.tsp.html")


    # tour_path = "../TSP/ALL_tsp/a280.opt.tour"
    # loader.load_tour(tour_path)

    # tsp_dir = "../TSP/ALL_tsp"
    # for tsp_file in os.listdir(tsp_dir):
    #     name, ext = os.path.splitext(tsp_file)
    #     if ext == ".tsp":
    #         loader = Loader(os.path.join(tsp_dir, tsp_file))
    #         print(f"{name}\t{loader.num_node}")
    #         print(loader)
