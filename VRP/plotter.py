import networkx as nx
from bokeh.models import Circle, MultiLine
from bokeh.plotting import figure, from_networkx, save, output_file
from pypathway import FromNetworkX, StylePresets
from pyvis.network import Network

class Plotter:
    def __init__(self, nx_graph):
        self.nx_graph = nx_graph

    def plot_bokeh_scatter(self, path):
        plot = figure(width=1000, height=1000, x_range=(-1.2, 1.2), y_range=(-1.2, 1.2),
                    x_axis_location=None, y_axis_location=None, toolbar_location=None,
                    background_fill_color="#efefef",
                    tooltips="index: @index, club: @club")
        plot.grid.grid_line_color = None

        graph_renderer = from_networkx(self.nx_graph, nx.spring_layout, scale=1, center=(0, 0))
        graph_renderer.node_renderer.glyph = Circle(size=10, fill_color="lightblue")
        graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color",
                                                    line_alpha=0.8, line_width=1.5)
        plot.renderers.append(graph_renderer)
        output_file(filename=path)
        save(plot)

    def plot_pyviz_network(self, path):
        net = Network(notebook=False)
        net.from_nx(self.nx_graph)
        net.show(path)
        

if __name__ == "__main__":
    nx_graph = nx.karate_club_graph()
    plotter = Plotter(nx_graph)
    # bokeh
    # path = "out/bokeh_example.html"
    # plotter.plot_bokeh_network(path)
