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
## Build the Docker Image
Build the Docker image using docker-compose:
```sh
docker-compose up --build
```
