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

To be added

## Understand the result

To be added


