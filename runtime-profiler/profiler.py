from cProfile import run
from runtime_metrics import profiler
import logging
import time
import psutil
import sys, getopt
import sched, schedule, time
import argparse
import subprocess

s = sched.scheduler(time.time, time.sleep)
stack = []


def is_proccess_found(name):
    """
    This function returns a boolean indicating whether the process is in progress

    """

    is_running = False
    for p in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
        l = ","
        running_command = l.join(p.info["cmdline"])
        # app_command_list = ["python", "-m", "tau_python_wrapper", "firstprime.py"]
        app_command_list = name.split()
        app_command = l.join(app_command_list)
        if app_command in running_command:
            is_running = True
    return is_running


def find_proccess(stack,metric_service):
    """
    This function looks up a process and starts profiling

    """

    logging.info("Finding Application")
    cmd = metric_service.entrypoint
    
    if is_proccess_found(cmd) == True:
        if len(stack) == 0:
            stack.append(time.time())
            logging.info("Profiling Application Started")
        else:
            logging.info("Profiling ... ")
        metric_service.system_profile()
    else:
        if len(stack) == 1:
            stack.append(time.time())
        logging.info("No Application to profile")

def cronjob(stack,metric_service):
    """ 
    This function is creates a cronjob and runs every 1/10th to check the running process

    """

    job = schedule.every(0.1).seconds.do(lambda: find_proccess(stack,metric_service))

    while True:
        schedule.run_pending()
        if len(stack) == 2:
            schedule.cancel_job(job)
            logging.info("Profiling completed")
            break
        time.sleep(1)
    

def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(
        description='record cpu and memory usage for a process')

    parser.add_argument('command', type=str,
                        help='the process id or command')
    

    parser.add_argument("local",nargs='?',default="local", const="local", type=str, choices=('local', 'beehive'), help=" choose where to store profile local or beehive")

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


    metric_service = profiler(args.command,args.local)
    cronjob(stack,metric_service)


if __name__ == "__main__":
    main()
