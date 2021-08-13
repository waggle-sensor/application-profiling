import tau
import subprocess
import os
from sys import argv
import time
import pytau
#print("Running TAU on " + sys.argv[1])
argv[0] = 'python3'
#argv.insert(0,'python3')


def main():
    print(argv)
    p = subprocess.Popen(argv)
    time.sleep(60)
    p.terminate()

 
#pytau.trackMemory()
#pytau.trackMemory()
tau.run("main()")
