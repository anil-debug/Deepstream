#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting script..."

# Run user_additional_install.sh script in the current directory
# ./user_additional_install.sh
# echo "Ran user_additional_install.sh"

# # Check if user_additional_install.sh was successful
# if [ $? -ne 0 ]; then
#   echo "user_additional_install.sh failed"
#   exit 1
# fi

# Check if deepstream-python-apps folder exists
if [ ! -d "/opt/nvidia/deepstream/deepstream-7.0/sources/deepstream-python-apps" ]; then
    echo "deepstream-python-apps folder does not exist, proceeding..."

    # Navigate to the deepstream-7.0/Deepstream directory
    cd /opt/nvidia/deepstream/deepstream-7.0/Deepstream
    echo "Changed directory to Deepstream"

    # Run user_deepstream_python_apps_install.sh script with --version 1.1.6 option
    ./user_deepstream_python_apps_install.sh --version 1.1.11
    echo "Ran user_deepstream_python_apps_install.sh --version 1.1.11"
    
    # Capture the exit status of user_deepstream_python_apps_install.sh --version 1.1.6
    install_status=$?

    # Check if user_deepstream_python_apps_install.sh --version 1.1.6 was successful
    if [ $install_status -ne 0 ]; then
      echo "user_deepstream_python_apps_install.sh --version 1.1.11 failed with exit code $install_status"
      # Optionally handle the failure or just log it
    fi

    # Reset the working directory to the original
    cd -
    echo "Reset directory back to original"
fi

# Keep the container running
tail -f /dev/null
