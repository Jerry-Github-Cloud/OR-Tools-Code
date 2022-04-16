from cgitb import html
import os
import json

if __name__ == '__main__':
    front_text = '''
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

    back_text = '''
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

    # [ 'Machine 1', 'Job2', 'Op0, start:10 , finish:80  ', 10 *scale, 80  *scale ],
    
    jsp_result_dir = '../ortools_result_6000'
    out_dir = '.'
    scale = 10
    for i, fn in enumerate(os.listdir(jsp_result_dir)):
        # fn: abz5.json
        file_name = os.path.join(jsp_result_dir, fn)
        with open(file_name, 'r') as f:
            history = json.load(f)
        html_text = ''
        html_text += front_text
        for op_info in history:
            d = [ 
                'Machine %d' %(op_info['machine_id']), 
                '%d' %(op_info['job_id']),
                'Job%d, Op%d, start:%d, finish:%d' %(op_info['job_id'], op_info['op_id'], op_info['start_time'], op_info['finish_time']),
                op_info['start_time']*scale, op_info['finish_time']*scale ]
            line = str(d) + ',\n'
            html_text += line
        html_text += back_text
        html_file_name, _ = os.path.splitext(fn)
        html_file_name += '.html'
        print(html_text)
        print(html_file_name)
        with open(html_file_name, 'w') as f:
            f.write(html_text)


