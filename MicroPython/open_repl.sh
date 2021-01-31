#!/bin/bash

set -e

echo "Executing \'screen\' command to open a Python prompt on $ESPPORT"

screen "$ESPPORT" 115200