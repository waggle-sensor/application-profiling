import json
from collections import deque
import time
import threading
import logging
import subprocess
import os
from tau_parser import parser
from collections import OrderedDict
from pathlib import Path
from datetime import datetime,timedelta
from waggle.plugin import Plugin


 
def current_memory():
    """ 
    when using UNIX / Mac OS host cgroup directory is /sys/fs/cgroup/memory.current
    current works on Ubuntu Linux.

    This function returns current memory usage in bytes of running container.
    """

    return int(open("/sys/fs/cgroup/memory/memory.usage_in_bytes").readline()[:-1])
    # return int(open("/sys/fs/cgroup/memory.current").readline()[:-1])


def memory_stat():
   
    """ 
    when using UNIX / Mac OS host cgroup directory is /sys/fs/cgroup/memory.stat
    current works on Ubuntu Linux.

    Function returns memory statistics from cgroup directory.
    """
    a = {}
    with open("/sys/fs/cgroup/memory/memory.stat") as f:
    # with open("/sys/fs/cgroup/memory.stat") as f:
        for line in f:
            (k, v) = line.split()
            a[k] = v
        f.close()
    return(a)


def cpu_utilization():
    """ 
    This function calculates the CPU Utilization of a running container
    takes average of 10 readings in 1/10th of a second.

    """


    cpu_util =[]
    u = 0
    last_idle = last_total = 0
    while u < 10:
        with open('/proc/stat') as f:
            fields = [float(column) for column in f.readline().strip().split()[1:]]
        idle, total = fields[3], sum(fields)
        idle_delta, total_delta = idle - last_idle, total - last_total
        last_idle, last_total = idle, total
        utilization = 100.0 * (1.0 - idle_delta / total_delta)
        cpu_util.append(utilization)
        time.sleep(0.1)
        u += 1

    return sum(cpu_util)/len(cpu_util)


class profiler:
    def __init__(self, command):

        """
        This profiler class to initialize 
       
        """
        self.indir = os.getcwd()
        self.metric = {}
        self.entrypoint = command
        
        #self.server_thread = threading.Thread(target=self.runSystemProfile)
        #self.server_thread.start()


    
    def send_data(self):
        with Plugin() as plugin:
            if os.path.exists('profile.0.0.0'):
                # self.parse()
                logging.info('Tau Profiling Completed')
                logging.info('Sending Data to Beehive')
                plugin.upload_file('profile.0.0.0', timestamp=str(datetime.now()))
                plugin.publish('test.bytes',self.parse())

            else:
                logging.info("Sending System Data to Beehive")
                plugin.publish('test.bytes',json.dumps(self.metric))


    def system_profile(self):

        """ 
        This function stores and records system utilization.

        """
        self.metric["container_ram_usage"] = current_memory()
        self.metric["cpu_utilization"] = cpu_utilization()
        # self.metric["memory_stat"] = memory_stat()

        # Records the tegrastarts of the host NVIDIA Nx device
        # with jtop() as jetson:
        #     if jetson.ok():
        #         self.metric['tegrastats'] = jetson.stats
        # print(self.metric)
        self.send_data()

       


    def parse(self):

        """ Parses the data from Tau and System Utilization
            sends to beehive via pywaggle
        """
        tau = parser()
        data = OrderedDict()
        index = 1
        print ("Processing:", self.indir)

        # p.parse_directory(self.indir, index, data)
        application = OrderedDict()
        #application["source directory"] = indir

        # add the application to the master dictionary
        # tmp = "Application " + str(index)
        #data[tmp] = application
        data[self.indir] = application
        
        # get the list of profile files
        profiles = [f for f in os.listdir(self.indir) if os.path.isfile(os.path.join (self.indir, f))]
        #application["num profiles"] = len(profiles)

        application["metadata"] = OrderedDict()
        function_map = {}
        counter_map = {}
        for p in profiles:
            if p == 'profile.0.0.0':
                tau.parse_profile(p, application, function_map, counter_map)        
        
        return json.dumps(data, indent=2, sort_keys=False)