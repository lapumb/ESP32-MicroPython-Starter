#!/bin/bash

set -e

# Upload all python modules to the ESP32 using ampy
for module in py/*; do
    echo "Uploading module $module"
    ampy -p $ESPPORT put $module
done
