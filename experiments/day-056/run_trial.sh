#!/usr/bin/env bash
# Usage: [NUM_CTX=16384] [TEXTBASED=1] run_trial.sh <model> <trial-name>   (NUM_CTX unset = Ollama default context)
# Resets a scratch clone to the commit with the injected bug, runs mini-swe-agent inside a
# network-less Docker container (python:3.12-slim, repo mounted at /repo), then grades the result.
set -u
MODEL="$1"; NAME="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${SEED:?set SEED to the scratch clone with the buggy commit}"
: "${MINI:?set MINI to the mini executable}"
W="$WORKROOT/$NAME"; rm -rf "$W"; git clone -q "$SEED" "$W"; git -C "$W" checkout -q buggy
cat > "$W.yaml" <<YAML
environment:
  environment_class: docker
  image: python:3.12-slim
  cwd: /repo
  run_args: ["--rm", "--network", "none", "--user", "$(id -u):$(id -g)", "-v", "$W:/repo"]
  timeout: 60
model:
  model_name: "$MODEL"
  cost_tracking: ignore_errors
  model_kwargs:
    api_base: "http://localhost:11434"
$( [ -n "${NUM_CTX:-}" ] && echo "    num_ctx: $NUM_CTX" )
agent:
  step_limit: ${STEP_LIMIT:-30}
  wall_time_limit_seconds: ${WALL:-900}
YAML
export MSWEA_CONFIGURED=true MSWEA_GLOBAL_CONFIG_DIR="$WORKROOT/.mswea"
start=$(date +%s)
if [ -n "${TEXTBASED:-}" ]; then BASE=(-c mini_textbased.yaml --model-class litellm_textbased); else BASE=(-c mini.yaml); fi
"$MINI" -y --exit-immediately "${BASE[@]}" -c "$W.yaml" -t "$(cat "$HERE/task.txt")" -o "$HERE/traj/$NAME.traj.json" > "$HERE/logs/$NAME.log" 2>&1 < /dev/null
rc=$?; end=$(date +%s)
python3 "$HERE/grade.py" "$W" "$HERE/traj/$NAME.traj.json" "$((end-start))" "$rc" | tee -a "$HERE/results.jsonl"
