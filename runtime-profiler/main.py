import argparse
import time
import os
import psutil
import subprocess
import json
from waggle.plugin import Plugin

from subprocess import Popen, PIPE

def get_cpu(process):
    return process.cpu_percent(interval=1.0)


## Parsers Memory Statistics of current running container
def memory_stat():
    a = {}
    ## when using UNIX / Mac OS host cgroup directory is /sys/fs/cgroup/memory.stat
    ## current works on Ubuntu Linux
    with open("/sys/fs/cgroup/memory/memory.stat") as f:
        for line in f:
            (k, v) = line.split()
            a[k] = v
        f.close()
    return(a)


## Returns current memory usage in bytes of running container.
def current_memory():
    ## when using UNIX / Mac OS host cgroup directory is /sys/fs/cgroup/memory.current
    ## current works on Ubuntu Linux
    return int(open("/sys/fs/cgroup/memory/memory.usage_in_bytes").readline()[:-1])


def main():

    parser = argparse.ArgumentParser(
        description='record cpu and memory usage for a process')

    parser.add_argument('command', type=str,
                        help='the process id or command')

    args = parser.parse_args()

    try:
        pid = int(args.command)
        print("Attaching to process {0}".format(pid))
        sprocess = None
    except Exception:
        command = args.command
        print("Starting up command '{0}' and attaching to process"
              .format(command))
        sprocess = subprocess.Popen(command,shell=True)
        pid = sprocess.pid
        #### 
    t_command = f"tegrastats --interval 10"
    r = subprocess.run(t_command,stdout=subprocess.PIPE)
    r = json.loads(r.stdout)
    print(r)


    profiler(pid)


    if sprocess is not None:
        sprocess.kill()

def profiler(pid):
    p = psutil.Process(pid)
    start = time.time()

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
            metric = {
                'time' : c - start,
                'cpu' : cpu,
                'current memory' : mem,
                'memory_stats' : mem_stats,
                # 'memory_virtual' : mem_virtual,
            }

            ## sends metrics to beehive, current installed pywaggle stores metrics locally
            ## if a volume is mounted
            with Plugin() as plugin:
                plugin.publish('test.bytes',json.dumps(metric))
                
    except KeyboardInterrupt:
        try:
            p.terminate()
        except OSError:
            pass

if __name__ == "__main__":
    main()