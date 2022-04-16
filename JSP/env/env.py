import os
import gym
from env.utils.instance import JSP_Instance
from tools.plotter import Plotter

class JSP_Env(gym.Env):
    def __init__(self, args):
        self.args = args
        self.jsp_instance = JSP_Instance(args)
        #self.count = -1

    def step(self, action):
        current_makespan = self.get_makespan()
        self.jsp_instance.assign(action['job_id'], action['op_id'])
        state = self.jsp_instance.current_state()
        #self.count += 1 
        #print("state: ", self.count)
        #self.jsp_instance.graph.print_feature()
        next_makespan = self.get_makespan()
        return state, current_makespan - next_makespan, self.done() 
    
    def reset(self):
        self.jsp_instance.reset()
        #self.jsp_instance.graph.print_structure()
        init_state = self.jsp_instance.current_state()
        #self.jsp_instance.graph.print_feature()
        return init_state
       
    def done(self):
        return self.jsp_instance.done()

    def get_makespan(self):
        return max(m.avai_time() for m in self.jsp_instance.machines)    
    
    def load_instance(self, filename):
        self.jsp_instance.load_instance(filename)
        #self.jsp_instance.graph.print_structure()
        init_state = self.jsp_instance.current_state()
        #self.count = 0
        #print("state: ", self.count)
        #self.jsp_instance.graph.print_feature()
        return init_state
    
    def visualize(self, name):
        plotter = Plotter(self.args, self.jsp_instance.logger)
        plotter.plot_interactive_gantt(name + ".html")
        """
        if os.path.isdir(name) == True:
            for f in os.listdir(name):
                os.remove(os.path.join(name, f))
        else:
            os.makedirs(name)
        plotter.plot_scheduling_process(name)
        plotter.images_to_video(name)
        """
        