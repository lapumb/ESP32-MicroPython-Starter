#!/bin/bash

set -e

cd $REPO_ROOT/MicroPython

echo "Flashing MicroPython: $MICROPYTHON_ESP_FIRMWARE"
esptool.py --chip esp32 --port $ESPPORT --baud 460800 write_flash -z 0x1000 $MICROPYTHON_ESP_FIRMWARE

cd -
