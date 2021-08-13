import psutil
import time
import csv

with open('stats.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['time']+['CPU']*psutil.cpu_count(False)+['Memory%'])
    x = time.time()
    while((time.time()-x) < 65.0):
        cpu_stats = psutil.cpu_percent(0.125,True)
        mem_stats = psutil.virtual_memory()
        spamwriter.writerow([time.time()]+[cpu_stats[0]]+[cpu_stats[1]]+[cpu_stats[2]]+[cpu_stats[3]]+[cpu_stats[4]]+[cpu_stats[5]]+[mem_stats.percent])
        #print(time.time()-x)
        #print(psutil.cpu_percent(0,True))
        #print(psutil.virtual_memory())
        #time.sleep(1)




