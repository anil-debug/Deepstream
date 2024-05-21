# Use a base image compatible with Jetson devices
FROM nvcr.io/nvidia/deepstream:6.4-triton-multiarch

# Step 1: Install required dependencies
RUN apt-get update && apt-get install -y \
    python3-gi \
    python3-dev \
    python3-gst-1.0 \
    python-gi-dev \
    git \
    python-dev \
    python3 \
    python3-pip \
    python3.8-dev \
    cmake \
    g++ \
    build-essential \
    libglib2.0-dev \
    libglib2.0-dev-bin \
    libgstreamer1.0-dev \
    libtool \
    m4 \
    autoconf \
    automake \
    libgirepository1.0-dev \
    libcairo2-dev \
    apt-transport-https \
    ca-certificates \
    && update-ca-certificates -y


# Step 2: Install gst python
RUN apt-get install -y apt-transport-https ca-certificates -y

# Step 3: 

RUN update-ca-certificates