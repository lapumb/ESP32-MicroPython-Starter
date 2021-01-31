#!/bin/bash

set -e

# Warning about erasing flash, ask for confirmation before proceeding
echo ""
echo "WARNING: You are about to erase flash, which will delete any unsecure data on the board."
echo "         This cannot be undone."
echo ""
echo "  After erasing flash, a new firmware image will need to be flashed"
echo "  to the device"
echo ""

# Ask for user confirmation before proceeding (default: don't proceed)
read -r -p "Would you like to proceed? [y/N]: " response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
if [[ ! $response =~ ^(yes|y) ]]; then
    echo "Exiting"
    exit 1
fi

echo "Erasing flash.."
esptool.py --port "$ESPPORT" erase_flash
