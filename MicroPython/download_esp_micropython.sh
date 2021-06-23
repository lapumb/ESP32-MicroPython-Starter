#!/bin/bash

cd $REPO_ROOT/MicroPython

# Remove the binary if it already exists
rm "$MICROPYTHON_ESP_FIRMWARE"

echo "Installing MicroPython: $MICROPYTHON_ESP_FIRMWARE"
wget https://micropython.org/resources/firmware/$MICROPYTHON_ESP_FIRMWARE

cd -
