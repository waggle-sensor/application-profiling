import argparse
import time
import os
import psutil
import subprocess
import json

from subprocess import Popen, PIPE

def get_cpu(process):
    return process.cpu_percent(interval=1.0)

# def c(s):
#     return process.cpu_percent(interval=1.0)

def memory_stat():
    a = {}
    with open("/sys/fs/cgroup/memory.stat") as f:
        for line in f:
            (k, v) = line.split()
            a[k] = v
        f.close()
    return(a)

def current_memory() -> int:
    """ Returns the memory usage of the container that this script is running in. """
    return int(open("/sys/fs/cgroup/memory.current").readline()[:-1])


def main():

    parser = argparse.ArgumentParser(
        description='record cpu and memory usage for a process')

    parser.add_argument('command', type=str,
                        help='the process id or command')

    args = parser.parse_args()

    try:
        pid = int(args.command)
        # print(pid)
        print("Attaching to process {0}".format(pid))
        sprocess = None
    except Exception:
        command = args.command
        # print(command)
        print("Starting up command '{0}' and attaching to process"
              .format(command))
        sprocess = subprocess.Popen(command,shell=True)
        # print(sprocess)
        pid = sprocess.pid
        

    profiler(pid)


    if sprocess is not None:
        sprocess.kill()

def profiler(pid):
    p = psutil.Process(pid)
    start = time.time()
    # print(pid)

    metric = {}
    # metric['time'] = []
    # metric['cpu_percent'] = []
    # metric['memory_real'] = []
    # metric['memory_virtual'] = []

    # CPU_CORE = psutil.cpu_count()

    try:
        while True:
            
            c = time.time()
            try:
                status = p.status()
            except TypeError:
                status = p.status
            except psutil.NoSuchProcess:
                break
            

            if p.status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                print("Profiling completed in ", c - start)
                break

            try:
                time.sleep(5)
                cpu = get_cpu(p)
                mem = current_memory()
                mem_stats = memory_stat()
            except Exception:
                print("Profiling failed")
                break
        
            # mem_real = mem.rss / 1024. ** 2
            # mem_virtual = mem.vms / 1024. ** 2

            current_metric ={
                'time' : c - start,
                'cpu' : cpu,
                'current memory' : mem,
                'memory_stats' : mem_stats,
                # 'memory_virtual' : mem_virtual,
            }

            # metric.add()
            print("current_metric", current_metric)
    except KeyboardInterrupt:
        try:
            p.terminate()
        except OSError:
            pass

if __name__ == "__main__":
    main()