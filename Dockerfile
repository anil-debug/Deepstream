# Use the base image
FROM nvcr.io/nvidia/deepstream:7.0-samples-multiarch

# Set the working directory
WORKDIR /opt/nvidia/deepstream/deepstream-7.0

# Copy the entrypoint script using the dynamically set path
COPY ${DYNAMIC_PATH}/start.sh /opt/nvidia/deepstream/deepstream-7.0/Deepstream/start.sh

# Ensure the script is executable
RUN chmod +x /opt/nvidia/deepstream/deepstream-7.0/Deepstream/start.sh

# Set the entrypoint script
ENTRYPOINT ["/opt/nvidia/deepstream/deepstream-7.0/Deepstream/start.sh"]

