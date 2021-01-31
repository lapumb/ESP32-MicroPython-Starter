#!/bin/bash

set -e

esptool.py --chip esp32 --port $ESPPORT write_flash -z 0x1000 $MICROPYTHON_ESP_FIRMWARE
