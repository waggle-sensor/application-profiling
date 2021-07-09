#!/bin/sh

# Start nvprof in the background and direct its output to a log file and a visualization file
/usr/local/cuda/bin/nvprof --profile-all-processes --log-file profile_nvprof_%p.log -o profile_nvprof_%p.out &
NVPROF_PID=$!  # Store the PID of nvprof so that it can be killed later

python3 wrappertest.py app.py "$@"

pprof

cp profile.0.0.0 profile_output

# Send interrupts to nvprof till it dies
nvprof_dead=0
until [ $nvprof_dead -eq 1 ]; do
	echo $NVPROF_PID
	kill -2 $NVPROF_PID >/dev/null
	echo "Sending interrupt signal to nvprof..."
	sleep 3s
	ps --pid $NVPROF_PID >/dev/null; nvprof_dead=$?
done

cp profile_nvprof_* profile_output
