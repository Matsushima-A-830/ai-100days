#!/bin/bash
# usage: run_inv.sh <model> <alert.json> <tag>
M=$1; A=$2; T=$3; W=$HOME/.cache/day058-work
mkdir -p $W/out
start=$(date +%s)
docker run --rm --network host --user 1000:1000 -v $W:/work \
  -e LLM_PROVIDER=ollama -e OLLAMA_MODEL=$M -e OLLAMA_HOST=http://127.0.0.1:11599 \
  -e DO_NOT_TRACK=1 -e OPENSRE_ANALYTICS_DISABLED=1 \
  day058-opensre:2026.4.5 timeout 1800 opensre investigate -i /work/$A -o /work/out/$T.json \
  > $W/out/$T.log 2>&1
rc=$?
echo "tag=$T model=$M alert=$A rc=$rc wall=$(( $(date +%s)-start ))s" | tee -a $W/out/runs.txt
