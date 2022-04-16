import os
import json
from tokenize import PlainToken
import numpy as np
import pandas as pd
import plotly.express as px
from pprint import pprint

from djsp_logger import DJSP_Logger

class DJSP_Plotter(object):
    def __init__(self, logger):
        self.logger = logger
    def _get_tooltip(self, op_info):
        if op_info['job_type'] == 'NOOP':
            return  'NOOP, start:%d, finish:%d, before O_%d,%d' %(op_info['start_time'], op_info['finish_time'], op_info['job_id'], op_info['op_id'])
        return 'Job%d, Op%d, start:%d, finish:%d' %(op_info['job_id'], op_info['op_id'], op_info['start_time'], op_info['finish_time'])
    def _get_job_id(self, op_info):
        if op_info['job_type'] == 'NOOP':
            return 'NOOP'
        return '%d' %(op_info['job_id'])
    def _get_color(self, op_info):
        if op_info['job_type'] == 'NOOP':
            return '#000000'
        return ''
    def plot_googlechart_timeline(self, html_out_file):
        jsp_result_dir = '../ortools_result'
        out_dir = '.'
        scale = 10
        # fn: abz5.json
        # history = self.logger.history
        history = sorted(self.logger.history, key=lambda op_info: op_info['job_id'])
        # history = self.logger
        html_text = ''
        html_text += self.logger.google_chart_front_text
        for op_info in history:
            d = [ 
                'Machine %d' %(op_info['machine_id']), 
                self._get_job_id(op_info),
                self._get_color(op_info),
                self._get_tooltip(op_info),
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


# if __name__ == '__main__':
#     in_file = './abz5.json'
#     logger = DJSP_Logger()
#     logger.load(in_file)
#     logger.find_noop()
#     plotter = DJSP_Plotter(logger)
#     plotter.plot_googlechart_timeline('timeline/google_charts_abz5.html')
#     plotter.plot_plotly_timeline('timeline/abz5.html')

if __name__ == '__main__':
    ### run all
    ortools_result_dir = '../ortools_result_6000'
    # html_out_dir = 'timeline/6000'
    html_out_dir = 'timeline/6000_noop'
    if not os.path.exists(html_out_dir):
        os.makedirs(html_out_dir)
    for i, file_name in enumerate(os.listdir(ortools_result_dir)): 
        json_in_file = os.path.join(ortools_result_dir, file_name)
        logger = DJSP_Logger()
        logger.load(json_in_file)
        logger.find_noop()
        plotter = DJSP_Plotter(logger)
        fn, _ = os.path.splitext(file_name)
        html_out_file = os.path.join(html_out_dir, fn+'.html')
        print(html_out_file)
        plotter.plot_googlechart_timeline(html_out_file)

    ### run one case
    # ortools_result_dir = '../ortools_result_6000'
    # html_out_dir = 'timeline/6000_noop'
    # file_name = 'la01.json'
    # json_in_file = os.path.join(ortools_result_dir, file_name)
    # logger = DJSP_Logger()
    # logger.load(json_in_file)
    # logger.find_noop()
    # plotter = DJSP_Plotter(logger)
    # fn, _ = os.path.splitext(file_name)
    # html_out_file = os.path.join(html_out_dir, fn+'.html')
    # print(html_out_file)
    # plotter.plot_googlechart_timeline(html_out_file)

