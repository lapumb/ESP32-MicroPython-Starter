#!/bin/bash

set -e

# Upload all python modules to the ESP32 using ampy
for module in py/*.py; do
    echo "Uploading module $module"
    ampy -p $ESPPORT put "$module"
done

# Note: Could also use `ampy -p $ESPPORT put py/` to achieve the same as above