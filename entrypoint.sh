#!/bin/sh -l

echo "all $*"
echo "Hello $1"

terraform -chdir "$1" init
terraform plan

time=$(date)
echo "::set-output name=time::$time"

