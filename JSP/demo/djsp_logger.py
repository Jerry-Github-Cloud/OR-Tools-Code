import json
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta 
from pprint import pprint

class DJSP_Logger(object):
    def __init__(self, num_job=50, num_machine=5, num_job_type=5):
        self.history = []
        self.jobs_to_schedule = []
        self.num_machine = num_machine
        self.num_job_type = num_job_type
        self.num_job = num_job
        self.order = 0
        self.NOOP_JOB_ID = 1 << 20
        self.NOOP_OP_ID = 1 << 20

        self.google_chart_front_text = '''
<html>
<head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <!-- <style>div.google-visualization-tooltip { transform: rotate(30deg); }</style> -->
    <script type="text/javascript">
    google.charts.load('current', {'packages':['timeline']});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        // var container = document.getElementById('timeline');
        var container = document.getElementById('timeline-tooltip');
        // var container = document.getElementById('example7.1');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn({ type: 'string', id: 'Machine' });
        dataTable.addColumn({ type: 'string', id: 'Name' });
        dataTable.addColumn({ type: 'string', role: 'style' });
        dataTable.addColumn({ type: 'string', role: 'tooltip' });
        // dataTable.addColumn({ type: 'date', id: 'Start' });
        // dataTable.addColumn({ type: 'date', id: 'End' });
        dataTable.addColumn({ type: 'number', id: 'Start' });
        dataTable.addColumn({ type: 'number', id: 'End' });
        var scale = 10;
        dataTable.addRows([
    '''

        self.google_chart_back_text = '''
        ]);
        var options = {
          // timeline: {showRowLabels: true}, 
          // avoidOverlappingGridLines: false
          tooltip: { textStyle: { fontName: 'verdana', fontSize: 30 } }, 
        }
        chart.draw(dataTable, options);
      }
    </script>
  </head>
  <body>
    <!-- <div id="timeline" style="height: 300px;"></div> -->
    <div id="timeline-tooltip" style="height: 800px;"></div>
  </body>
</html>
    '''
        # self.db_path = os.path.join('loggerDB', datetime.now().strftime("%Y-%m-%d-%H:%M:%S:%f") +'.db') 
        # self.conn = sqlite3.connect(self.db_path)
        # self.cursor = self.conn.cursor()
        # self.cursor.execute(
        #     '''CREATE TABLE LOGGER
        #     (TIMESTAMP  INT     PRIMARY KEY     NOT NULL,
        #     MACHINE_ID  INT     NOT NULL,
        #     JOB_TYPE    INT     NOT NULL,
        #     JOB_ID      INT     NOT NULL,
        #     OP_ID       INT     NOT NULL,
        #     START_TIME  REAL    NOT NULL,
        #     FINISH_TIME REAL    NOT NULL, 
        #     RPT         REAL    NOT NULL
        #     );''')
    
    def add_job(self, job):
        job_info = {
            'job_id':           job.job_id,
            'arrival_time':     job.arrival_time, 
            'due_time':         job.due_date, 
            'job_type':         job.job_type,
            'DDT':              job.DDT,
        }
        self.jobs_to_schedule.append(job_info)

    def add_op(self, op, machine_id, job_type):
        # add op information to history
        op_info = {
            'Order':        self.order,
            'job_id':       op.job_id,
            'op_id':        op.op_id,
            'machine_id':   machine_id,
            'start_time':   op.startTime, 
            'process_time': op.RPT,
            'finish_time':  op.startTime+op.RPT,
            'job_type':     job_type,
        }
        self.order += 1
        self.history.append(op_info)
        # print(op_info)
        # self.cursor.execute(
        #         "INSERT INTO LOGGER (TIMESTAMP, MACHINE_ID, JOB_TYPE, JOB_ID, OP_ID, START_TIME, FINISH_TIME, RPT) \
        #         VALUES (%d, %d, %d, %d, %d, %f, %f, %f)" %(
        #             op_info['timestamp'], op_info['machine_id'], op_info['job_type'], op_info['job_id'], op_info['op_id'], 
        #             op_info['start_time'], op_info['finish_time'], op_info['process_time']))
    
    def save(self, json_out_file):
        with open(json_out_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def load(self, json_in_file):
        with open(json_in_file, 'r') as f:
            self.history = list(json.load(f))

    def arrange_history_by(self, key, need_sort=False):
        res = {}
        for op_info in self.history:
            if op_info[key] in res:
                res[op_info[key]].append(op_info)
            else:
                res[op_info[key]] = [op_info]
        for k, op_infos in res.items():
            op_infos.sort(key = lambda op_info : op_info['start_time'])
        # pprint(res)
        return res

    def _previous_op_infos_in_job(self, current_op_info):
        history_in_job_id = self.arrange_history_by('job_id')
        previous_op_infos = []
        job_id = current_op_info['job_id']
        op_id = current_op_info['op_id']
        for op_info in history_in_job_id[job_id]:
            if op_info['op_id'] < op_id:
                previous_op_infos.append(op_info)
            else:
                break
        return previous_op_infos

    def _previous_op_info_in_job(self, current_op_info):
        history_in_job_id = self.arrange_history_by('job_id', need_sort=True)
        job_id = current_op_info['job_id']
        op_id = current_op_info['op_id']
        if op_id == 0:
            return None
        return history_in_job_id[job_id][op_id-1]
    def _previous_op_info_in_machine(self, current_op_info):
        history_in_machine_id = self.arrange_history_by('machine_id')
        history_in_machine_id[current_op_info['machine_id']]

    # def _empty_interval_helper(self, left_op, right_op):
    #     if right_op['op_id'] == 0:
    #         noop_info = {
    #             'Order':        None,
    #             'job_id':       self.NOOP_JOB_ID,
    #             'op_id':        self.NOOP_OP_ID,
    #             'machine_id':   left_op['machine_id'],
    #             'start_time':   left_op['finish_time'], 
    #             'process_time': right_op['start_time'] - left_op['finish_time'],
    #             'finish_time':  right_op['start_time'],
    #             'job_type':     'noop',
    #         }
    #         self.history.append(noop_info)
    #     else:
    #         pre_op_info = self._previous_op_info_in_job(right_op)
    #         if pre_op_info == None:
    #             return 
    #         if left_op['finish_time'] < pre_op_info['finish_time'] and pre_op_info['finish_time'] < right_op['start_time']:
    #             # print('\t', left_op)
    #             # print('\t', right_op)
    #             # print('\tno op machine %d, [%d,%d]' %(left_op['machine_id'], pre_op_info['finish_time'], right_op['start_time']))
    #             noop_info = {
    #                 'Order':        None,
    #                 'job_id':       self.NOOP_JOB_ID,
    #                 'op_id':        self.NOOP_OP_ID,
    #                 'machine_id':   left_op['machine_id'],
    #                 'start_time':   pre_op_info['finish_time'], 
    #                 'process_time': right_op['start_time']-pre_op_info['finish_time'],
    #                 'finish_time':  right_op['start_time'],
    #                 'job_type':     'noop',
    #             }
    #             self.history.append(noop_info)

    def _find_all_empty_intervals(self, left_time, right_time, machine_id):
        # print('left_time, right_time, machine_id:', left_time, right_time, machine_id)
        history_in_machine_id = self.arrange_history_by('machine_id', need_sort=True)
        op_infos_in_machine_id = history_in_machine_id[machine_id]
        if left_time >= right_time:
            return []
        else:
            nonempty_intervals = []
            empty_intervals = []
            for op_info in op_infos_in_machine_id:
                if left_time < op_info['finish_time'] and op_info['finish_time'] <= right_time:
                    # print('op_info:', op_info)
                    nonempty_intervals.append([op_info['start_time'], op_info['finish_time']])
            # print('\tnonempty_intervals:', nonempty_intervals)
            if len(nonempty_intervals) == 0:
                return [[left_time, right_time]]
            # left = left_time
            # if left < nonempty_intervals[0][1]:
            #     left = nonempty_intervals[0][1]
            # for i, interval in enumerate(nonempty_intervals):
            #     if left < interval[0]:
            #         empty_intervals.append([left, interval[0]])
            #         left = interval[1]
            # if left < right_time:
            #     empty_intervals.append([left, right_time])
            # print('\tempty_intervals:', empty_intervals)

            # if left_time < nonempty_intervals[0][0]:
            #     empty_intervals.append([left_time, nonempty_intervals[0][0]])
            if nonempty_intervals[0][0] < left_time:
                left_time = nonempty_intervals[0][1]
            elif nonempty_intervals[0][0] > left_time:
                empty_intervals.append([left_time, nonempty_intervals[0][0]])
            if nonempty_intervals[-1][1] < right_time:
                empty_intervals.append([nonempty_intervals[-1][1], right_time])
            for i, interval in enumerate(nonempty_intervals):
                if i == len(nonempty_intervals)-1:
                    continue
                noop_start = nonempty_intervals[i][1]
                noop_finish = nonempty_intervals[i+1][0]
                if noop_start < noop_finish:
                    empty_intervals.append([noop_start, noop_finish])
            # print('\tempty_intervals:', empty_intervals)
            return empty_intervals
    def find_noop(self):
        history_in_job_id = self.arrange_history_by('job_id', need_sort=True)
        # pprint(history_in_job_id)
        for job_id, op_infos in history_in_job_id.items():
            previous_op_info = None
            for op_id, op_info in enumerate(op_infos):
                # print('pre_op_info:\t', previous_op_info)
                # print('op_info:\t', op_info)
                if previous_op_info == None:
                    empty_intervals = self._find_all_empty_intervals(0, op_info['start_time'], op_info['machine_id'])
                else:
                    empty_intervals = self._find_all_empty_intervals(previous_op_info['finish_time'], op_info['start_time'], op_info['machine_id'])
                for interval in empty_intervals:
                    noop_start = interval[0]
                    noop_finish = interval[1]
                    if noop_start < noop_finish:
                        noop_info = {
                            'Order':        None,
                            'job_id':       op_info['job_id'],
                            'op_id':        op_info['op_id'],
                            'machine_id':   op_info['machine_id'],
                            'start_time':   noop_start, 
                            'process_time': noop_finish-noop_start,
                            'finish_time':  noop_finish,
                            'job_type':     'NOOP',
                        }
                        self.history.append(noop_info)
                previous_op_info = op_info

    # def find_noop(self):
    #     history_in_machine_id = self.arrange_history_by('machine_id', need_sort=True)
    #     # history_in_job_id = self.arrange_history_by('job_id')
    #     for machine_id, op_infos in history_in_machine_id.items():
    #         for i in range(len(op_infos)-1):
    #             if (op_infos[i]['finish_time'] < op_infos[i+1]['start_time']):
    #                 # print('empty interval in machine %d, [%d, %d]' %(machine_id, op_infos[i]['finish_time'], op_infos[i+1]['start_time']))
    #                 self._empty_interval_helper(op_infos[i], op_infos[i+1])
    
    def get_plotly_timeline_input(self, color_by):        
        unix_epoch = datetime.strptime('1970-01-01', '%Y-%m-%d')
        data = []
        import plotly.express as px
        for t, op_info in enumerate(self.history):
            d = dict(
                Task =              'Machine '+str(op_info['machine_id']), 
                machine_id =        str(op_info['machine_id']),
                Start =             op_info['start_time'],
                Finish =            op_info['finish_time'],
                StartDateTime =     unix_epoch + timedelta(days=op_info['start_time']),
                FinishDateTime =    unix_epoch + timedelta(days=op_info['finish_time']),
                process_time =      op_info['process_time'],
                # job_type =          str(op_info['job_type']),
                job_type =          t % 5,
                job_id =            str(op_info['job_id']),
                op_id =             op_info['op_id'],
            )
            if isinstance(color_by, tuple):
                d['color'] = (d['job_type'], op_info[color_by[1]])
            data.append(d)
        return data
    def radiantQ_json(self):
        unix_epoch = datetime.strptime('2020-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        data = []
        for t, op_info in enumerate(self.history):
            # if t >= 3:
            #     break
            start_time = unix_epoch + timedelta(hours=op_info['start_time'])
            d = {
                # "Name":         "Task " + str(t),
                "Name":         "Job%d, Op%d, Machine%d, Start time:%f, RPT:%f" %(
                    op_info['job_id'], op_info['op_id'], op_info['machine_id'], op_info['start_time'], op_info['process_time']),
                "ID":           t,
                "SortOrder":    t,
                "StartTime":    str(start_time.strftime('%Y-%m-%dT%H:%M:%SZ')),
                "Effort":       str(int(op_info['process_time'])) + ":00:00",
            }
            data.append(d)
        with open('sample.json', 'w') as f:
            json.dump(data, f, indent=4)

    def __str__(self):
        s = ''
        for job_info in self.jobs_to_schedule:
            s += 'job_id: {}, arrival_time: {}, due_time: {}, job_type: {}, DDT: {}\n'.format(
                job_info['job_id'], job_info['arrival_time'], job_info['due_time'], job_info['job_type'], job_info['DDT']
            )
        for op_info in self.history:
            job_id = op_info['job_id']
            machine_id = op_info['machine_id']
            s += 'machine_id: {}, job_type: {}, job_id: {}, op_id: {}, op.start_time: {}, op.finish_time: {}, op.RPT: {}\n'.format(
                machine_id, op_info['job_type'], job_id, op_info['op_id'], op_info['start_time'], op_info['finish_time'], op_info['process_time'])
        return s
    
google_chart_front_text = '''
<html>
<head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <!-- <style>div.google-visualization-tooltip { transform: rotate(30deg); }</style> -->
    <script type="text/javascript">
    google.charts.load('current', {'packages':['timeline']});
    google.charts.setOnLoadCallback(drawChart);
    function drawChart() {
        // var container = document.getElementById('timeline');
        var container = document.getElementById('timeline-tooltip');
        // var container = document.getElementById('example7.1');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn({ type: 'string', id: 'Machine' });
        dataTable.addColumn({ type: 'string', id: 'Name' });
        dataTable.addColumn({ type: 'string', role: 'tooltip' });
        // dataTable.addColumn({ type: 'date', id: 'Start' });
        // dataTable.addColumn({ type: 'date', id: 'End' });
        dataTable.addColumn({ type: 'number', id: 'Start' });
        dataTable.addColumn({ type: 'number', id: 'End' });
        var scale = 10;
        dataTable.addRows([
    '''

google_chart_back_text = '''
        ]);
        var options = {
          // timeline: {showRowLabels: true}, 
          // avoidOverlappingGridLines: false
          tooltip: { textStyle: { fontName: 'verdana', fontSize: 30 } }, 
        }
        chart.draw(dataTable, options);
      }
    </script>
  </head>
  <body>
    <!-- <div id="timeline" style="height: 300px;"></div> -->
    <div id="timeline-tooltip" style="height: 800px;"></div>
  </body>
</html>
    '''

if __name__ == '__main__':
    logger = DJSP_Logger()
    logger.load('')
    # print(logger)


