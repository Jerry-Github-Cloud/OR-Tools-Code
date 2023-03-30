import json
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go

class Plotter:
    def __init__(self, path):
        self.path = path
        with open(path, 'r') as fp:
            self.result = json.load(fp)

    def plot_sns_heatmap(self):
        width = self.result['width']
        height = self.result['height']
        matrix = np.zeros((width, height), dtype=int)
        for i, block in enumerate(self.result["block"]):
            x, y, w, h = block['x'], block['y'], block['w'], block['h']
            if block["border"]:
                matrix[x:x+w, y:y+h] = -1
            else:
                matrix[x:x+w, y:y+h] = i + 1
        fig = sns.heatmap(pd.DataFrame(matrix), annot=True).get_figure()
        fig.savefig("viz/output.png") 

    def plot_plotly_heatmap(self):
        width = self.result['width']
        height = self.result['height']
        matrix = np.zeros((width, height), dtype=int)
        for i, block in enumerate(self.result["block"]):
            x, y, w, h = block['x'], block['y'], block['w'], block['h']
            matrix[x:x+w, y:y+h] = i + 1
        # fig = go.Figure(go.Histogram2d(x=x,y=y))
        fig.write_html("viz/output.html")


if __name__ == "__main__":
    # result_path = "result/3.json"
    # result_path = "result/0004.json"
    # result_path = "result/0005.json"
    result_path = "result/0001_d=10.json"
    plotter = Plotter(result_path)
    # plotter.plot_plotly_heatmap()
    plotter.plot_sns_heatmap()
