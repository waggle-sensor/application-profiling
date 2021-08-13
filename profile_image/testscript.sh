#!/bin/sh

timeout 60 python3 test.py &
while [1]
do
timeout 4 mpstat -P ALL 3 
free -t -s  
done
