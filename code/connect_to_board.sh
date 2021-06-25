#!/bin/bash

set -e

echo "Executing 'picocom' command to connect to the ESP32 on port $ESPPORT"

picocom $ESPPORT -b115200