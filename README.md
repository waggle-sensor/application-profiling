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

## Running with Chris's Profiler

This profile has been built into a modified version of the waggle plugn base image. The files added to this new image are in the profile_image directory. The files are:
- parser.py
- stats.py
- profiler.sh
- tau.tgz
- wrappertest.py
- test.py(for debugging)


To add this profiling suite to your app container, in your dockerfile switch "FROM Wagglepluginbase... " to "FROM chrispkraemer/profiler:0.0.0" and set the entrypoint to "./profiler.sh" and run docker run -ti --rm  --name thisone -v /home/nvidia/data-config.json:/run/waggle/data-config.json -v (path to dir):/app/profile_output --runtime nvidia --network host waggle/plugin-(name) [args]. Path to dir is the path to your local directory where you want the profile output to be placed. Name is the name of the app you are running and args are the arguments you are passing to app.py. 


The profiling script will collect data by running the app twice, each for 60 seconds.

## Understand the result

The output of the profiler will be ftimes.csv, ltimes.csv, profile.0.0.0, and stats.csv. Run python3 plotstats in the directory where the csv files are stored to map function and loop to resource usage. The output of profile.0.0.0 is displayed as the container finishes running the app. Run pprof locally if Tunining and Analysis Utilities (TAU) is installed


