#!/bin/bash
# usage: run.sh <dir> <model>  (config.toml in <dir>)
cd $1 && start=$(date +%s)
HERETIC_CONFIG_FILE=./config.toml ../.venv/bin/heretic --model $2 --checkpoint-action restart --trial-index 0 \
  --model-action save --save-directory $1/model > heretic_run.log 2>&1
echo "dir=$1 model=$2 rc=$? wall=$(( $(date +%s)-start ))s" | tee -a ../runs.txt
