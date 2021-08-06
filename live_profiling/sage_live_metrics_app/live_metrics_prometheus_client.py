import json
import time, random
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import socket
import socketserver
import threading


n_apps = 0
metrics_table = {}  # The metrics tables, updated by handler threads, is exported by the Prometheus HTTP server endpoint


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
            metric = str(self.request.recv(4096))[2:-5]
            # print(metric)  # Debug that we are able to receive metrics from the apps
            metric_obj = {}
            try:
                metric_obj = json.loads(metric)
            except json.JSONDecodeError:
                print('[METRICS] JSONDecodeError: ', str(metric))
            metrics_table[app_id].update(metric_obj)


class CustomCollector(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):

    SOCKET_FILE = "/app/live_metrics.sock"  # The socket which every hooked app connects to

    def __init__(self, address, handler, run_memory_monitoring=True):
        """
        Initialize the metrics collection service by hosting the unix socket.
        """
        super().__init__(address, handler)

    @staticmethod
    def collect():
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
        """
        # g = GaugeMetricFamily("MemoryUsage", 'Help text', labels=['instance'])
        # g.add_metric(["instance01.us.west.local"], 20)
        # g.add_metric(["nvidia-nx"], random.random()*1000)
        # yield g
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
    start_http_server(9090)

    collector = CustomCollector('/app/live_metrics.sock', CollectorHandler)
    with collector:
        print('Starting unix socket server in separate thread...')
        server_thread = threading.Thread(target=collector.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print('Registering collector...')
        REGISTRY.register(collector)
        while True:
            time.sleep(5)
            print(metrics_table)
