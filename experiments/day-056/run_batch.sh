#!/usr/bin/env bash
# Runs all trials of Day 056 in sequence. Requires SEED, MINI, WORKROOT (see README.md).
cd "$(dirname "$0")"
for m in qwen2.5:7b-instruct qwen2.5:14b-instruct gemma4:e4b qwen2.5-coder:3b-instruct-q4_K_M; do
  tag=$(echo "$m" | sed 's/qwen2.5-coder:3b.*/coder3b/; s/qwen2.5:\([0-9]*b\).*/\1/; s/gemma4:e4b/gemma4e4b/')
  for i in 1 2 3; do
    [ "$tag-$i" = "14b-1" ] && continue   # ctx16k-14b-1 was the first run, kept as-is
    NUM_CTX=16384 ./run_trial.sh "ollama_chat/$m" "ctx16k-$tag-$i"
  done
done
for i in 2 3; do ./run_trial.sh ollama_chat/qwen2.5:14b-instruct "ctx4096-14b-$i"; done
