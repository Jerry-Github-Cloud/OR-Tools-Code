import numpy as np
import bisect
import torch
from env.utils.mach_job_op import *
from env.utils.generator import *
from env.utils.graph import Graph
from tools.logger import Logger


class JSP_Instance:
    def __init__(self, args):
        self.args = args
        self.machine_num = args.machine_num
        self.initial_job_num = args.initial_job_num
        self.op_num = args.op_num
        self.process_time_range = [1, args.max_process_time]
        
    ##### basic functions
    def generate_case(self):
        # initial jobs, not dynamic
        self.insert_jobs(job_num=self.initial_job_num)
        
    def insert_jobs(self, job_num):
        for i in range(job_num):
            job_id = len(self.jobs)
            self.register_time(self.arrival_time)
            op_config = gen_operations(self.op_num, self.machine_num, self.process_time_range)
            self.jobs.append(Job(job_id=job_id, arrival_time=self.arrival_time, op_config=op_config))
            self.graph.add_job(self.jobs[-1])
        
    def reset(self):
        self.jobs = []
        self.machines = [Machine(machine_id) for machine_id in range(self.machine_num)]
        self.arrival_time = 0
        self.current_time = 0
        self.time_stamp = []
        self.graph = Graph(self.args)
        self.logger = Logger(self.args)
        self.generate_case()
        self.max_process_time = self.get_max_process_time()
        
    def load_instance(self, filename):
        self.jobs = []
        self.arrival_time = 0
        self.current_time = 0
        self.time_stamp = []
        
        f = open(filename)
        line = f.readline()
        while line[0] == '#':
            line = f.readline()
        line = line.split()
        self.initial_job_num, self.machine_num = int(line[0]), int(line[1])
        self.machines = [Machine(machine_id) for machine_id in range(self.machine_num)]
        self.args.machine_num, self.args.initial_job_num, self.args.op_num = self.machine_num, self.initial_job_num, self.machine_num
        self.graph = Graph(self.args)
        self.logger = Logger(self.args)

        for i in range(self.initial_job_num):
            op_config = []
            line = f.readline().split()
            for j in range(self.machine_num):
                machine_id, process_time = int(line[j * 2]), int(line[j * 2 + 1])
                op_config.append({"id": j, "machine_id": machine_id, "process_time": process_time})
            self.jobs.append(Job(job_id=i, arrival_time=self.arrival_time, op_config=op_config))
            self.graph.add_job(self.jobs[-1])
        self.max_process_time = self.get_max_process_time()
        
    def done(self):
        for job in self.jobs:
            if job.done() == False:
                return False
        return True
    
    def current_state(self):
        avai_ops = self.available_ops()
        data = self.graph.get_data()
        return (avai_ops, data.to(self.args.device))
        
    def assign(self, job_id, op_id):
        assert op_id == self.jobs[job_id].current_op_id
        op = self.jobs[job_id].current_op()
        op_info = {
            "job_id": job_id,
            "op_id": op.op_id,
            "current_time": self.current_time,
            "process_time": op.process_time
        }
        op_finished_time = self.machines[op.machine_id].process_op(op_info)
        self.jobs[job_id].current_op().update(self.current_time)
        # add op to logger
        self.logger.add_op(op)
        if self.jobs[job_id].next_op() != -1:
            self.jobs[job_id].update_current_op(avai_time=op_finished_time)
        self.register_time(op_finished_time)
    
    ##### about time control
    def register_time(self, time):
        # maintain a list in sorted order
        bisect.insort(self.time_stamp, time)
    
    def update_time(self):
        self.current_time = self.time_stamp.pop(0)
    
    """
    def available_ops(self):
        if self.done() == True:
            return None
        avai_ops = []
        find = False
        for m in self.machines:
            m_avai_ops = []
            for job in self.jobs:
                if job.done() == False and job.current_op().avai_time <= self.current_time:
                    if m.avai_time() <= self.current_time and m.machine_id == job.current_op().machine_id:
                        find = True
                        m_avai_ops.append({'job_id': job.job_id, 'op_id': job.current_op_id, 'node_id': job.current_op().node_id})
            avai_ops.append(m_avai_ops)
            
        if find == True:
            self.graph.update_feature(self.jobs, self.machines, self.current_time)
            return avai_ops
        else:
            self.update_time()
            return self.available_ops()
    """
    
    def available_ops(self):
        if self.done() == True:
            return None
        avai_ops = []
        select_action = False 
        for m in self.machines:
            m_avai_ops = []
            for job in self.jobs:
                if job.done() == False and job.current_op().avai_time <= self.current_time:
                    if m.avai_time() <= self.current_time and m.machine_id == job.current_op().machine_id:
                        m_avai_ops.append({'job_id': job.job_id, 'op_id': job.current_op_id, 'node_id': job.current_op().node_id})
            
            if len(m_avai_ops) == 1:
                self.assign(m_avai_ops[0]['job_id'], m_avai_ops[0]['op_id'])
                avai_ops.append([])
            else:
                if len(m_avai_ops) > 1:
                    select_action = True
                avai_ops.append(m_avai_ops)
                
        if select_action == True:
            self.graph.update_feature(self.jobs, self.machines, self.current_time, self.max_process_time)
            return avai_ops
        else:
            self.update_time()
            return self.available_ops()
        
    def get_max_process_time(self):
        max_process_time = -1
        for job in self.jobs:
            for op in job.operations:
                if op.process_time > max_process_time:
                    max_process_time = op.process_time
        return max_process_time
    