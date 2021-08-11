import json
import time, random
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import socket
import socketserver
import subprocess
import threading
from queue import Queue
import pycuda.driver
import sys
import os.path


n_apps = 0
metrics_table = {}  # The metrics tables, updated by handler threads, is exported by the Prometheus HTTP server endpoint


class AsynchronousFileReader(threading.Thread):
    """
    This code is for asyncronously grabbing tegrastats output lines at the request of the HTTP user.

    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    """

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        """The body of the tread: read lines and put them on the queue."""
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        """Check whether there is no more content to expect."""
        return not self.is_alive() and self._queue.empty()


class CollectorHandler(socketserver.BaseRequestHandler):
    """
    This thread handles the connection requests from client apps that are reporting their hook metrics.
    """

    def handle(self) -> None:
        global n_apps
        app_id = n_apps
        metrics_table[app_id] = {}
        n_apps += 1
        while True:
            # It is OK that this blocks because when it gets unblocked, the handler will have something to do
            metric = str(self.request.recv(4096))[2:-5]
            # print(metric)  # Debug that we are able to receive metrics from the apps
            metric_obj = {}
            try:
                metric_obj = json.loads(metric)
            except json.JSONDecodeError:  # TODO Add better error handling features here- this causes an infinite loop in this thread
                print('[METRICS] JSONDecodeError: ', str(metric), flush=True)
            metrics_table[app_id].update(metric_obj)


class CustomCollector(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):

    SOCKET_FILE = "/metrics/live_metrics.sock"  # The socket which every hooked app connects to

    @staticmethod
    def parse_tegra_stats(stats_str: str) -> dict:
        """
        Note that this function will fail if the NX is not using swap, since this will screw up the spacing assumptions
        that I have made when parsing the tegrastats line.

        TODO: Fix the dependency on output spacing ^
        """

        split_line = stats_str.split(' ')

        ram_usage = split_line[1]
        swap_usage = split_line[5]
        emc_usage = split_line[11]
        gpu_usage = split_line[13]

        # CPU usage is in the format of a list of 'USAGE%@FREQUENCY' or 'off'
        cpus_usage = split_line[9][1:-1].split(',')
        fmt_cpus_usage = []
        for cpu in cpus_usage:
            if cpu == 'off':
                continue
            utilization, freq = cpu.split('%@')
            fmt_cpus_usage.append((int(utilization), int(freq)))

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
                'CPU': fmt_cpus_usage,
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

    def __init__(self, address, handler, run_system_monitoring=True, run_gpu_monitoring=True):
        """
        Initialize the metrics collection service by hosting the unix socket.

        TODO: Add logging features that allow developers to see errors in metrics collection
        TODO: Add reliability features like error handling before pushing this to production
        """
        if os.path.exists(address):
            os.unlink(address)

        super().__init__(address, handler)

        import pycuda.autoinit
        self.pycuda_context = pycuda.autoinit.context

        # If user wishes to export system-wide memory/CPU utilization metrics
        self.run_memory_monitoring = run_system_monitoring
        if run_system_monitoring:
            command = ['tegrastats']
            sys.stdout.write('Starting tegrastats...')
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            sys.stdout.write("Starting tegrastats queue...")
            self.stdout_queue = Queue()
            self.tegrastats_reader = AsynchronousFileReader(process.stdout, self.stdout_queue)
            self.tegrastats_reader.start()

        # For GPU profiling with pycuda
        self.run_gpu_monitoring = run_gpu_monitoring
        if run_gpu_monitoring:
            pass

    def collect(self):
        """
        This function will be queried by the collector every 1s, so this needs to be fast and non-blocking.
        I am thinking that the connection threads update a metrics table that is shared between all threads.
        This table will be in the following format:
            {
                APP_NAME_A: {
                    METRIC_1: (Current value of metric 1)
                    METRIC_2: (Current value of metric 2)
                }
                APP_NAME_B: {
                    METRIC_5: (Current value of metric 5)
                }
            }
        (APP_NAME_A would just be 0 and APP_NAME_B would be 1, being the second app that connects to the socket)
        For each app, there is a connection thread responsible for handling its metrics and updating the shared metrics
        table that corresponds to its app number (1 through n apps).

        TODO: FEATURE: Add rolling averages. Some metrics like CPU/GPU utilization are best seen as rolling averages.
        TODO: Add meaningful labels to the Prometheus metrics if helpful
        """
        # Export tegrastats metrics
        if self.run_memory_monitoring:
            print('===== Memory monitoring =====', flush=True)
            tegra_ram_usage = GaugeMetricFamily("TegraRAMUsage", 'Global RAM usage reported by tegrastats',
                                                  labels=["testbed_device"])
            tegra_cpu_total_usage = GaugeMetricFamily("TegraCPUUsage", 'Global CPU usage reported by tegrastats- '
                                                                       'percentage means utilization across many cores',
                                                  labels=["testbed_device"])
            # Query the tegrastats output queue
            tegrastats_line = self.stdout_queue.get()  # TODO Implement clearing this queue to save memory (might require a mutex)
            # Default metric values
            ram_usage = -1
            cpu_total_usage = -1
            if tegrastats_line != '':
                system_stats = self.parse_tegra_stats(str(tegrastats_line)[2:-2])
                ram_usage = int(system_stats['usage']['RAM'].split('/')[0])
                # Sum over percentages
                cpu_total_usage = sum([utilization for utilization, _ in system_stats['usage']['CPU']])

            tegra_ram_usage.add_metric(["nvidia-nx"], ram_usage)
            tegra_cpu_total_usage.add_metric(["nvidia-nx"], cpu_total_usage)
            yield tegra_ram_usage
            yield tegra_cpu_total_usage

        # Extract pycuda metrics
        if self.run_gpu_monitoring:
            print('===== GPU monitoring =====', flush=True)
            export_gpu_usage = GaugeMetricFamily("GPUMemoryUsage", 'Global GPU usage reported by pycuda',
                                                 labels=["testbed_device"])
            export_gpu_total = GaugeMetricFamily("GPUMemoryTotal", 'Global total GPU memory reported by pycuda',
                                                 labels=["testbed_device"])

            # This is necessary because pycuda retains context per-thread, so on this thread it is necessary to refresh the context
            self.pycuda_context.push()
            mem_free, mem_total = pycuda.driver.mem_get_info()
            self.pycuda_context.pop()

            # Add metrics to stack
            export_gpu_usage.add_metric(["nvidia-nx"], mem_free)
            export_gpu_total.add_metric(["nvidia-nx"], mem_total)
            yield export_gpu_usage
            yield export_gpu_total

        # Report metrics from metrics table (these are metrics taken from socket connections)
        for app_id, app_metrics in metrics_table.items():
            for metric_name, metric_pt in app_metrics.items():
                value = metric_pt['value']
                timestamp = metric_pt['timestamp']
                g1 = GaugeMetricFamily("app%d_%s_timestamp" % (app_id, metric_name), '')
                g2 = GaugeMetricFamily("app%d_%s_value" % (app_id, metric_name), '')
                g1.add_metric([], timestamp)
                g2.add_metric([], value)
                yield g1
                yield g2


if __name__ == '__main__':
    prometheus_port = 9090
    sys.stdout.write('Starting prometheus server on port %d' % prometheus_port)
    start_http_server(prometheus_port)

    collector = CustomCollector('/metrics/live_metrics.sock', CollectorHandler)
    with collector:
        print('Starting unix socket server in separate thread...', flush=True)
        server_thread = threading.Thread(target=collector.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        REGISTRY.register(collector)
        while True:
            time.sleep(5)
            print(metrics_table, flush=True)
