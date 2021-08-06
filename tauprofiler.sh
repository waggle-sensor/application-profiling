#!/bin/sh

# =================== Profiler ==========================
# =======================================================

printf "\n\n========== SAGE PROFILER ==========\n\n"

APP_MAX_ELAPSED_TIME=20


# Purpose: Tests if a process is alive by querying ps
# Arguments: [proc id]
is_proc_alive() {
	ps --pid $1 >/dev/null;
	return $([ $? -eq 1 ]);
}

# Purpose: Send a kill signal to a process until it dies >:)
# Arguments: [proc id] [signal (either 2 or 9)]
interrupt_process () {
	printf "[PROFILER] Sending interrupt signal to process %d..." $1
	until ! is_proc_alive $1; do
		#DEBUG: printf "kill -s %d %d >/dev/null\n" $2 $1
		kill -s $2 $1 >/dev/null
		printf "."
		sleep 1s
	done
	printf "killed\n"
}

/usr/local/cuda/bin/nvprof --profile-all-processes --log-file profile_nvprof_%p.log -o profile_nvprof_%p.out &
NVPROF_PID=$!

tegrastats --interval 2000 --logfile profile_tegrastats.log &
TEGRASTATS_PID=$!

printf "[PROFILER] Started nvprof (pid %d) and tegrastats (pid %d)\n[PROFILER] Starting app...\n" $NVPROF_PID $TEGRASTATS_PID

python3 wrappertest.py app.py "$@" &
APP_PID=$!

# Start the timer for the app and kill an interrupt to it when it is finished
printf "[PROFILER] Waiting for %ds or for the app to close\n\n" $APP_MAX_ELAPSED_TIME
APP_START_TIME=$(date +%s)
while is_proc_alive $APP_PID; do
	APP_ELAPSED_TIME=$(($(date +%s)-$APP_START_TIME))
	if [ $APP_ELAPSED_TIME -gt $APP_MAX_ELAPSED_TIME ] 
	then
		interrupt_process $APP_PID 2
		break
	fi
	sleep 2s
done

#The tool pprof can be used to output a parsing of the profile dump to stdout:
#pprof

interrupt_process $NVPROF_PID 2
interrupt_process $TEGRASTATS_PID 9

mv profile.0.0.0 profile_output
mv profile_nvprof_* profile_output
mv profile_tegrastats.log profile_output

