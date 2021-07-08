# Waggle Application Profiler (WaAP)

Waggle application profiler measures performance factors of applications and resources consumed by execution of the applications. WaAP launches target application as a container and mounts the profiling probes, test dataset, and user-provided instructions on how to run the application. Upon completion of user-instructed execution, the profiler outputs profiling result in a given format.

This tool uses Docker to deploy profiling jobs by default. However, the tool can be configured with a Jenkins server to manage multiple profiling jobs. The tool also supports GPU profiling if profiling can be performed on Nvidia GPU machine.

![Overview](image/overview.jpg)

## Requirements

The tool requires,
- PyWaggle v0.40.5 or higher
- Docker ce 19 or higher
- Jenkins (optional)
- Nvidia CUDA driver and library (only for GPU profiling)

## Build The Profiling Tool

To be added

## Run Profiling

## Running with TAU Profiler

(to be cleaned up soon)

- git clone objectcounter plugin
- cp Dockerfile, tauprofiler.sh, and wrappertest.py into that repo

- build the docker image with make image
	- make sure you download tau.tgz from the tau website and put it in the same directory as the Dockerfile
	- make sure you have the coco ssd in your directory(same as above)
- docker run -ti --rm --name objcounter -v /home/nvidia/data-config.json:/run/waggle/data-config.json -v profile_ouput:/app/profile_output --runtime nvidia --network host waggle/plugin-object-counter:0.0.0 -stream bottom_image -object person -interval 1
	- This does a few things
		- runs the docker image in a container
		- entrypoint is set to shell script
			- that script runs a python wrapper to apply the auto instrumentation tau profiler for app.py
			- also runs pprof (to show profiler output)
			- copies the profile output file (profile.0.0.0) to a volume names profile_output
			- run docker inspect volume to find where this is in the host


## Understand the result

To be added


