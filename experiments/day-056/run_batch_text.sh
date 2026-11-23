#!/usr/bin/env bash
# Second batch: same task with mini_textbased.yaml (commands parsed from a ```mswea_bash_command block
# in plain text instead of the tool-calling API). Requires SEED, MINI, WORKROOT.
cd "$(dirname "$0")"
for m in qwen2.5:7b-instruct qwen2.5:14b-instruct gemma4:e4b qwen2.5-coder:3b-instruct-q4_K_M; do
  tag=$(echo "$m" | sed 's/qwen2.5-coder:3b.*/coder3b/; s/qwen2.5:\([0-9]*b\).*/\1/; s/gemma4:e4b/gemma4e4b/')
  for i in 1 2 3; do TEXTBASED=1 NUM_CTX=16384 ./run_trial.sh "ollama_chat/$m" "text16k-$tag-$i"; done
done
