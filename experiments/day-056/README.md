# Day 056: Can mini-swe-agent with local LLMs fix a one-line bug in this repository?

Source: https://github.com/SWE-agent/mini-swe-agent (MIT). Tested version: mini-swe-agent 2.4.6.

I injected one bug into `experiments/day-055/regrade.py` (`nums[-1]` → `nums[0]`), then gave mini-swe-agent a fix request.
It ran 3 times each with 4 local Ollama models (qwen2.5 7B/14B, qwen2.5-coder 3B, gemma4 e4b), under 3 conditions: tool-calling mode with the default and the larger context, and text mode.
Commands ran in a network-less Docker container (`python:3.12-slim`).
Results are in `results.md`.

The Day 056 cloud Routine did not run, so I did everything from verification to writing up the results on the local PC.

## Reproduction steps

```bash
uv venv -p 3.12 .venv && uv pip install -p .venv mini-swe-agent==2.4.6
ollama pull qwen2.5:7b-instruct qwen2.5:14b-instruct gemma4:e4b qwen2.5-coder:3b-instruct-q4_K_M
docker pull python:3.12-slim

# Working copy with the bug injected (the buggy branch)
git clone <this repository> seed && cd seed && git checkout -b buggy
sed -i 's/last = nums\[-1\]/last = nums[0]/' experiments/day-055/regrade.py && git commit -qam "inject bug" && cd ..

# Docker Desktop + WSL2 could not bind-mount folders under /tmp, so put the working copies under home
export SEED=$PWD/seed MINI=$PWD/.venv/bin/mini WORKROOT=$HOME/.cache/day056-work
./run_batch.sh        # tool-calling mode (ctx16k x 4 models, ctx4096 for 14B)
./run_batch_text.sh   # text mode (text16k x 4 models)
python3 summarize.py
```

A single run is `NUM_CTX=16384 [TEXTBASED=1] ./run_trial.sh ollama_chat/gemma4:e4b <name>`.

## Files

- `task.txt`: the task text given to the agent
- `run_trial.sh`: reset the working copy → run `mini -y --exit-immediately` → grade
- `run_batch.sh` / `run_batch_text.sh`: run all trials
- `grade.py`: run the fixed `regrade.py` on a fresh JSON and check it prints the expected values `1/20, 19/20, 18/20, 11/20`
- `summarize.py`: aggregate `results.jsonl` by condition and model (output in `logs/summary.txt`)
- `show_traj.py`: list the commands in a trajectory with the start of each output
- `results.jsonl`: per-trial results (including the patch)
- `traj/*.traj.json`: mini-swe-agent trajectories; `traj/claude-1.result.json` is the Claude Code reference run
- `logs/*.log`: mini screen logs; `logs/ollama-journal-ctx.log`: Ollama context size and context-shift logs
