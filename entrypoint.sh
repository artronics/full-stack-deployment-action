#!/bin/sh -l

echo "all $*"
echo "Hello $1"

echo terraform -chdir="$1" init
echo terraform plan
