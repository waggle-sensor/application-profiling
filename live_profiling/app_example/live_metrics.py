import json
import socket
import sys
from collections import deque
import time
import threading


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


def get_container_memory() -> int:
    """Returns the memory usage of the container that this script is running in."""
    return int(open('/sys/fs/cgroup/memory/memory.usage_in_bytes').readline()[:-1])


class SageAppMetricsServer:

    """
    This class describes a server which exposes a unix socket to the Prometheus client container running on the same
    node. This server handles the Python hooks into the developer's application that can give them explicit control over
    live metrics. The metrics are collected by the Prometheus client and accessible from there by the edge controller.
    """

    METRIC_TIMER = 0
    METRIC_RATE = 1
    METRIC_NUMBER = 2

    def connect_to_metrics_socket(self):
        """
        Block until the server connects to the metrics socket. NOTE: this file must be shared with the Docker container
        that this script runs inside.
        """
        self.socket.connect(self.socket_path)

    def host_metrics_server(self):
        """
        A thread that runs in the background which sends metrics immediately to the custom Prometheus client when a new
        metric arrives in the queue.
        """
        report_cycle = 0
        while True:
            time.sleep(0.1)  # A little delay so that this thread doesn't fry the CPU

            # Every half-second report RAM usage of the currently-running container
            if report_cycle % 5 == 0:
                self.push_metric('RAM_usage', get_container_memory())
            report_cycle += 1

            if len(self.metric_queue) > 0:
                metric_to_send = self.metric_queue.pop()
                print('[METRICS] Sending: %s' % metric_to_send)
                try:
                    self.socket.sendall(metric_to_send.encode() + b'\n\n')
                except BrokenPipeError:
                    print('[METRICS] BrokenPipeError, exiting...')
                    sys.exit(-1)

    def __init__(self, metrics: dict, socket_path="/metrics/live_metrics.sock"):
        """
        Init server with a dictionary of
            {metric_name: METRIC_TYPE}
        and host at the default socket path (unless otherwise specified as a str)
        """
        # Metrics
        self.metrics = {}
        self.metrics_definition = metrics
        self.metric_queue = deque()  # A queue of JSON strings
        # Networking
        self.socket_path = socket_path
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect_to_metrics_socket()
        # Launch server loop in the background as a thread
        self.server_thread = threading.Thread(target=self.host_metrics_server)
        self.server_thread.start()

    def push_metric(self, metric_name: str, metric_value: object):
        """
        Add a metric value to the server queue. This will be retrieved by the Prometheus client which is running in
        a container on the node.
        """
        self.metric_queue.appendleft(json.dumps({metric_name: {'value': metric_value, 'timestamp': time.time()}}))

    def start_timer(self, metric_name: str):
        self.metrics[metric_name] = time.time()

    def stop_timer(self, metric_name: str):
        """
        Once this arbitrary timer is stopped, the measurement of the code block that it timed will be processed further.
        For example, in the simple case of a developer just wanting to time a code block, no processing is needed. But
        if the developer wants to know the average FPS of a code block, then that requires more processing to find the
        rate. At the moment I have just computed the "instantaneous" FPS, not the average FPS. That may need to be done
        in the future to get more accurate FPS measurements.
        """

        stop_time = time.time()
        elapsed_time = stop_time - self.metrics[metric_name]
        # If metric is a simple timer, report time elapsed
        if self.metrics_definition[metric_name] == self.METRIC_TIMER:
            self.push_metric(metric_name, elapsed_time)
        # If metric is an FPS measurement, report the rate (TODO: Make this an average of many timing measurements for more accurate FPS)
        elif self.metrics_definition[metric_name] == self.METRIC_RATE:
            self.push_metric(metric_name, 1.0 / elapsed_time)
        else:
            print('[Error] Unable to make sense of timing measurement, no valid measurement type for %s specified'
                  % metric_name)
