### utility to visualize profiler output
### This script will generate plots from the profiler output and 
### hard coded and not fully implemented for multiple metrics.

import logging
import os
import json
import ast
import time
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, DateFormatter

def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    directory = os.getcwd() 
    output_file = directory + "/" + "output.json"
    if os.path.isfile(output_file) is True:
        logging.info("Output File Found")
        read_file = open(output_file)
        data = json.load(read_file)
        x = []
        ram_y1 = []
        cpu_y2 = []
        for i in range(len(data)):
            d = ast.literal_eval(data[i])
            for k , v in d.items():
                if k == "container_ram_usage":
                    ram_y1.append(int(v/1024/1024))
                elif k == "cpu_utilization":
                    cpu_y2.append(int(v))
                elif k == "timestamp":
                    x.append(datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f'))
                else:
                    pass
        # print(len(x),len(ram_y1),len(cpu_y2))
        # print(type(x[0]))

        logging.info("Plotting")

        memory_color = "#0000FF"
        cpu_color = "#00FF00"

        fig, ax1 = plt.subplots(figsize=(6, 6))
        ax2 = ax1.twinx()

        ax1.plot(x,  ram_y1, color= memory_color, lw=1)
        ax2.plot(x, cpu_y2, color=cpu_color, lw=1)

        ax1.set_xlabel("Timestamp")
        ax1.set_ylabel("Memory Usage + swap  (GB)", color= memory_color)
        ax1.tick_params(axis="y", labelcolor= memory_color)

        ax2.set_ylabel("CPU Utilization (%)", color=cpu_color)
        ax2.tick_params(axis="y", labelcolor=cpu_color)

        fig.suptitle("container profile")
        fig.autofmt_xdate()

        plt.show()

        logging.info("Plotting Snapshots")
        os.system('paraprof snapshot.0.0.0')

        time.sleep(5)

        logging.info("Plotting TAU Profile")
        os.system('paraprof profile.0.0.0')

        



       
    else:
        logging.info("Output file not found")

if __name__ == "__main__":
    main()