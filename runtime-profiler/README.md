<!-- docker build -t my-ml-container:latest . -->

### How to RUN 

- First step is build the docker image. For the example name application as app-example:latest run the following command in terminal

    ``` cd runtime-profiler ```

    ``` docker build -t app-example:latest . ```

- Second step change the mounted volume directory for your use in profile.sh. This example use a mounted volume so it need to be a valid directory in your machine.

    ``` -v /your/directory/Desktop/metrics:/app/output ```


- Third step is to run. Run the profile script by providing container name and the image name provided in step 1. This example has CONTAINER_NAME = profiler and IMAGE_NAME = app-example:latest

    ``` sh profile.sh profiler app-example:latest ```

- Fourth step find profile metrics on mounted volume directory. This metric should be sent to beehive however the current pywaggle used help saves in a mounted directory.


