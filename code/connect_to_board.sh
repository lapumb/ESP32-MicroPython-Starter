#!/bin/bash

set -e

echo "Executing 'screen' command to connect to the ESP32 on port $ESPPORT"

screen "$ESPPORT" 115200