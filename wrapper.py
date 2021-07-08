import tau
import subprocess
from sys import argv

argv[0] = 'python3'


def main():
    print(argv)
    subprocess.call(argv)

tau.run("main()")