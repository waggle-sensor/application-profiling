import pycuda.autoinit
import pycuda.driver
import subprocess
import time
import threading
from queue import Queue
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server


class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()


def parse_tegra_stats(stats_str: str) -> dict:
    split_line = stats_str.split(' ')

    ram_usage = split_line[1]
    swap_usage = split_line[5]
    emc_usage = split_line[11]
    gpu_usage = split_line[13]

    # CPU usage is in the format of a list of 'USAGE%@FREQUENCY' or 'off'
    cpus_usage = split_line[9][1:-1].split(',')

    ao_temp = split_line[-6].split('@')[-1]
    gpu_temp = split_line[-5].split('@')[-1]
    pmic_temp = split_line[-4].split('@')[-1]
    aux_temp = split_line[-3].split('@')[-1]
    cpu_temp = split_line[-2].split('@')[-1]
    thermal = split_line[-1].split('@')[-1]

    stats = {
        'usage': {
            'RAM': ram_usage,
            'swap': swap_usage,
            'CPU': cpus_usage,
            'EMC': emc_usage,
            'GPU': gpu_usage
        },
        'temp': {
            'CPU': cpu_temp,
            'GPU': gpu_temp,
            'AUX': aux_temp,
            'thermal': thermal
        }
    }
    return stats


class CustomCollector:

	def __init__(self, pycuda_device, pycuda_context):
		command = ['tegrastats']
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		print("Starting tegrastats queue...")
		self.stdout_queue = Queue()
		self.stdout_reader = AsynchronousFileReader(process.stdout, self.stdout_queue)
		self.stdout_reader.start()
		print("Finished up collector initialization.")
		
		self.device = pycuda_device
		self.context = pycuda_context

	def collect(self):
		print("Collecting metrics...", end='')
		export_tegrastats = GaugeMetricFamily("RAMUsage", 'Global RAM usage reported by tegrastats', labels=["testbed_device"])
		export_gpu_usage = GaugeMetricFamily("GPUMemoryUsage", 'Global GPU usage reported by pycuda', labels=["testbed_device"])

		self.context.push()
		mem_free, mem_total = pycuda.driver.mem_get_info()
		self.context.pop()
		metric_mem = mem_free
		export_gpu_usage.add_metric(["nvidia-nx"], metric_mem)
		print('(GPU MEM: %d) ' % metric_mem, end='')
		yield export_gpu_usage
				
		tegrastats_line = self.stdout_queue.get()
		
		if tegrastats_line != '':
			system_stats = parse_tegra_stats(str(tegrastats_line)[2:-2])
			ram_usage = int(system_stats['usage']['RAM'].split('/')[0])
		else:
			ram_usage = -1
		print('(RAM: %dMB) ' % ram_usage, end='')
		export_tegrastats.add_metric(["nvidia-nx"], ram_usage)
		yield export_tegrastats
		
		print("...done")


if __name__ == '__main__':
	# Setup custom Prometheus metric exporter
	start_http_server(9090)
	REGISTRY.register(CustomCollector(pycuda.autoinit.device, pycuda.autoinit.context))
	print('Started HTTP server on port 9090!')

	while True:
		time.sleep(1)


