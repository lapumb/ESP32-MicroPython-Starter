#!/bin/bash

set -e

cd $REPO_ROOT

echo "Uploading aws_config.."
ampy -p $ESPPORT put aws_config

cd -
