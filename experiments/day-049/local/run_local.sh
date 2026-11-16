#!/usr/bin/env bash
# Day 049 local run: OpenWorker (headless CLI) + Ollama Qwen2.5 on the human's PC.
# usage: run_local.sh <name> <ollama-model> <approval-mode> <timeout> <prompt>
set -uo pipefail
W=/home/matsu/work-day049
NOTES=/home/matsu/workspace/ai-100days/experiments/day-049
name=$1 model=$2 mode=$3 timeout=$4 prompt=$5
ws=$W/ws/$name out=$W/out/$name
rm -rf "$ws" "$out"; mkdir -p "$ws" "$W/home"
cp "$NOTES/notes1.md" "$NOTES/notes2.md" "$ws/"
cd "$ws"
HOME=$W/home OPENWORKER_OLLAMA_NUM_CTX=${NUM_CTX:-16384} \
  "$W/venv/bin/openworker" run --isolated --workspace "$ws" \
  --model "ollama:$model" --approval-mode "$mode" --out "$out" \
  --timeout-seconds "$timeout" --prompt "$prompt" </dev/null 2>&1
echo "exit=$?"
echo "--- workspace after run:"; ls -la "$ws" | tail -n +4
