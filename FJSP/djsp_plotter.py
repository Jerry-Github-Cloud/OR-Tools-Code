import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
from pprint import pprint

from djsp_logger import DJSP_Logger

class DJSP_Plotter(object):
    def __init__(self, logger):
        self.logger = logger

    def plot_googlechart_timeline(self, html_out_file):
        scale = 1000
        # fn: abz5.json
        history = self.logger.history
        html_text = ''
        html_text += self.logger.google_chart_front_text
        for op_info in history:
            d = [ 
                'Machine %d' %(op_info['machine_id']), 
                '%d' %(op_info['job_id']),
                'Job%d, Op%d, start:%d, finish:%d' %(op_info['job_id'], op_info['op_id'], op_info['start_time'], op_info['finish_time']),
                op_info['start_time']*scale, op_info['finish_time']*scale ]
            line = str(d) + ',\n'
            html_text += line
        html_text += self.logger.google_chart_back_text
        with open(html_out_file, 'w') as f:
            f.write(html_text)

    def plot_plotly_timeline(self, html_name, color_by='job_id'):
        ### timeline
        ### x-axis: date
        if isinstance(color_by, str):
            data = self.logger.get_plotly_timeline_input(color_by)
            df = pd.DataFrame(data)
            fig = px.timeline(
                df, x_start='StartDateTime', x_end='FinishDateTime', y='machine_id', color='job_id', 
                hover_name='job_id', hover_data=['job_id', 'op_id', 'process_time', 'Start', 'Finish']
            )
            fig.update_layout(xaxis_type='date')    # ['-', 'linear', 'log', 'date', 'category', 'multicategory']
            fig.write_html(html_name)
        if isinstance(color_by, tuple):
            # colors = [ 'red', 'green', 'blue', 'orange', 'purple' ]
            color_maps = [ 
                px.colors.sequential.Reds[1:],      px.colors.sequential.Greens[1:],    px.colors.sequential.Blues[1:], 
                px.colors.sequential.Greys[1:],   px.colors.sequential.Purples[1:],   px.colors.sequential.Oranges[1:],
                px.colors.sequential.PuRd[1:]]
            color_discrete_map = {}
            for i in range(5):
                for j in range(10):
                    size = len(color_maps[i])
                    color_discrete_map[(i, j)] = color_maps[i][j%size]
            data = self.logger.get_plotly_timeline_input(color_by)
            print(data)
            df = pd.DataFrame(data)
            fig = px.timeline(
                df, x_start='StartDateTime', x_end='FinishDateTime', y='machine_id', color='color', 
                hover_name='job_id', hover_data=['job_id', 'op_id', 'process_time', 'Start', 'Finish'],
                color_discrete_map = color_discrete_map
            )
            fig.update_layout(xaxis_type='date')    # ['-', 'linear', 'log', 'date', 'category', 'multicategory']
            fig.write_html(html_name)


if __name__ == '__main__':
    in_file = '/mnt/nfs/work/oo12374/JSP/Ortools/JSP/ortools_result/abz5.json'
    logger = DJSP_Logger()
    logger.load(in_file)

    plotter = DJSP_Plotter(logger)
    plotter.plot_plotly_timeline('test/interactive_timeline.html')



