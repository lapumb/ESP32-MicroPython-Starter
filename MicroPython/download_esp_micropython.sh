#!/bin/bash

cd $REPO_ROOT/MicroPython

# Remove the binary if it already exists
rm "$MICROPYTHON_ESP_FIRMWARE"

echo "Installing MicroPython ESP-IDF v3"
wget https://micropython.org/resources/firmware/$MICROPYTHON_ESP_FIRMWARE

cd -
