# Pre-requisites

The following are the libraries and hardware needed for DeepStream 7.0 on x86 platform
```
Ubuntu 22.04
CUDA 12.2 Update 2
TensorRT 8.6 GA (8.6.1.6)
NVIDIA Driver 535 (>= 535.161.08)
NVIDIA DeepStream SDK 7.0
GStreamer 1.20.3
DeepStream-Yolo
```
# Building Deepstream Pipelines with Docker

This guide outlines the step-by-step implementation on how to run a Deepstream pipeline with Docker.

## Step 1: Clone the Repository
Clone the `deepstream-development` repository:
```sh
git clone <repository_url>
```
## Step 2: Enter the Repository Directory
Clone the `Deepstream` repository:
```sh
git clone <repository_url>
```
## Step 3: Modify the Environment Variables
Edit the .env file to set the dynamic path to the location where this repository is cloned. Modify the DISPLAY value if necessary.
## Step 4: Build the Docker Image
Build the Docker image using docker-compose:
```sh
docker-compose up --build
```
## Step 5
Execute the following command to enter the Docker container:
```
docker exec -ti $DEEPSTREAM_CONTAINER bash
```
## Step 6
Run the deepstream pipeline in Deepstream/apps
```
python3 deepstream_test_1.py /opt/nvidia/deepstream/deepstream-7.0/samples/streams/sample_qHD.h264 
```
# Custom Models
