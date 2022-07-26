### utility to visualize profiler output

import logging
import os
import json
import ast
import time
import matplotlib.pyplot as plt

def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    directory = os.getcwd() 
    output_file = directory + "/" + "output.json"
    if os.path.isfile(output_file) is True:
        # logging.info("Output File Found")
        # read_file = open(output_file)
        # data = json.load(read_file)
        # x = []
        # ram_y1 = []
        # cpu_y2 = []
        # for i in range(len(data)):
        #     d = ast.literal_eval(data[i])
        #     for k , v in d.items():
        #         if k == "ram_utilization":
        #             ram_y1.append(v)
        #         elif k == "cpu_utilization":
        #             cpu_y2.append(v)
        #         else:
        #             x.append(v)

        # logging.info("Plotting")
        # plt.plot(x, ram_y1,label = "container RAM")
        # plt.plot(x, cpu_y2, label = "CPU")
        # plt.xlabel('Timestamp')
        # # plt.ylabel('y - axis')
        # # giving a title to my graph
        # plt.title('Container Profile')
        # plt.show()

        logging.info("Plotting Snapshots")
        os.system('paraprof snapshot.0.0.0')

        time.sleep(5)

        logging.info("Plotting TAU Profile")
        os.system('paraprof profile.0.0.0')

        



       
    else:
        logging.info("Output file not found")

if __name__ == "__main__":
    main()