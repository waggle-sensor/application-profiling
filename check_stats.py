import subprocess, threading
import queue as Queue


class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
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


def get_stats():
    command = ['tegrastats']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout_queue = Queue.Queue()
    stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()

    line = stdout_queue.get()

    if line == '':
        return None

    stats = parse_tegra_stats(str(line)[2:-2])  # Splice out the byte prefix/suffix and the newline
    return stats


if __name__ == '__main__':
    while True:
        print(get_stats())
