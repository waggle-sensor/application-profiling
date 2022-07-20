#!/bin/bash
# A script to run and profile a docker container


## Build Container
# docker build -t app-example:latest .

IMAGE_NAME=$1
CONTAINER_NAME=$2

echo "USAGE: profile.sh 'container_name' 'image_name' "


if [ $( docker ps -a -f name=$IMAGE_NAME | wc -l ) -eq 2 ]; then
  echo "$IMAGE_NAME exists"
  # docker run --name $IMAGE_NAME -v /Users/abayomi/Desktop/metrics:/app/output -e PYWAGGLE_LOG_DIR=/app/output $CONTAINER_NAME
  docker rm $IMAGE_NAME
#   docker run --name $IMAGE_NAME $CONTAINER_NAME
else
  echo "$CONTAINER_NAME does not exist"
  echo "Building $IMAGE_NAME ...."
  # docker build -t $IMAGE_NAME .
  echo "Completed $IMAGE_NAME ...."
  echo "Running $IMAGE_NAME ...."
  docker run --name $IMAGE_NAME -v /Users/abayomi/Desktop/metrics:/app/output -e PYWAGGLE_LOG_DIR=/app/output $CONTAINER_NAME
fi