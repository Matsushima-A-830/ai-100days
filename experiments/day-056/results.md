# Day 056 results: mini-swe-agent with local Ollama models fixing a one-line bug in this repository

Source: https://github.com/SWE-agent/mini-swe-agent (MIT). Tested version: `mini-swe-agent==2.4.6` from PyPI (litellm 1.110.2).

Day 056's cloud Routine did not run (PR #192 was merged late), so everything from verification to the deliverables was done on the local PC.

## 0. Environment

| Item | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 5060 Ti (16GB) |
| OS | Windows + WSL2 (Ubuntu 24.04) |
| LLM server | Ollama 0.35.1 (`http://localhost:11434`) |
| Agent | mini-swe-agent 2.4.6, `mini -y --exit-immediately` (yolo mode) |
| Execution environment | mini-swe-agent's `docker` environment. `python:3.12-slim`, `--network none`, run as my own UID, working copy mounted at `/repo` |

Models (all Q4_K_M from Ollama):

| Model | Parameters | License (`ollama show --license`) |
|---|---|---|
| qwen2.5:7b-instruct | 7.6B | Apache-2.0 |
| qwen2.5:14b-instruct | 14.8B | Apache-2.0 |
| gemma4:e4b | 7.5B (shown as `parameters 7.5B` by Ollama; the name means effective 4B) | Apache-2.0 |
| qwen2.5-coder:3b-instruct-q4_K_M | 3.1B | Qwen RESEARCH LICENSE |

Claude Code CLI (`claude -p`, model `claude-opus-5-5`) was also run once on the same task as a reference.

No Anthropic/OpenAI API keys were set (`env | grep -iE '^(ANTHROPIC|OPENAI|LITELLM)'` returned nothing), so mini-swe-agent was connected only to local models.
Reusing Claude Code's login credentials with litellm was not attempted.

## 1. Task

In a clone of this repository, I injected one bug into `experiments/day-055/regrade.py` (commit `inject bug` on the `buggy` branch).

```diff
-        last = nums[-1].replace(",", "") if nums else ""
+        last = nums[0].replace(",", "") if nums else ""
```

With the bug, grading uses the first number in the reply instead of the last, and the output changes as follows.

```
$ python3 regrade.py <copy of out_loops.json>    # with the bug
loops=1: digits-concat 1/20, last-number 1/20
loops=2: digits-concat 19/20, last-number 19/20
loops=3: digits-concat 17/20, last-number 17/20
loops=4: digits-concat 10/20, last-number 10/20
```

The correct values are `1/20, 19/20, 18/20, 11/20`.
The task given to the agent is in `task.txt` (it includes the expected values and the instruction "run it on a copy and do not modify out_loops.json itself").

Grading (`grade.py`): after the run, the working copy's `regrade.py` is run on a fresh copy of `out_loops.json` from the `buggy` branch. It passes only if the result matches `1/20, 19/20, 18/20, 11/20` exactly.
I also checked with `git status` whether the original `out_loops.json` had been modified.

Limits: `step_limit: 30`, `wall_time_limit_seconds: 900`, command timeout 60 seconds.

## 2. Results (aggregated with `summarize.py` → `logs/summary.txt`)

```
condition    model                                    fixed  submitted  json_overwritten  median_s
ctx4096      ollama_chat/qwen2.5:14b-instruct         0/3    0/3        0/3               104
ctx16k       ollama_chat/qwen2.5:14b-instruct         0/3    0/3        0/3               557
ctx16k       ollama_chat/qwen2.5:7b-instruct          0/3    0/3        0/3               56
ctx16k       ollama_chat/gemma4:e4b                   2/3    2/3        0/3               31
ctx16k       ollama_chat/qwen2.5-coder:3b-instruct-q4_K_M 0/3    0/3        0/3               13
text16k      ollama_chat/qwen2.5:7b-instruct          0/3    1/3        3/3               113
text16k      ollama_chat/qwen2.5:14b-instruct         0/3    0/3        0/3               242
text16k      ollama_chat/gemma4:e4b                   2/3    3/3        0/3               24
text16k      ollama_chat/qwen2.5-coder:3b-instruct-q4_K_M 0/3    1/3        1/3               34
claude-code  claude-code                              1/1    0/1        0/1               15
submitted but not fixed: ['ctx16k-gemma4e4b-3', 'textprobe', 'text16k-7b-2', 'text16k-gemma4e4b-2', 'text16k-coder3b-1']
```

- `ctx4096`: default config (`mini.yaml`, tool calling). Ollama's context left at its default.
- `ctx16k`: same, plus `num_ctx: 16384` added to `model_kwargs`.
- `text16k`: `mini_textbased.yaml` + `--model-class litellm_textbased`. No tool calling; the command is extracted from a ```` ```mswea_bash_command ```` block in the reply text. `num_ctx: 16384`.
- `claude-code`: `claude -p "<task.txt>" --allowedTools "Bash,Read,Edit,Glob,Grep" --max-turns 30` (run on the host, not in a container). The `submitted` column is a mini-swe-agent field, so it shows 0 for this row.
- The claude-code row's median_s includes clone time; `duration_ms` was 13,949.

Per-trial details are in `results.jsonl` (including the patch), with trajectories in `traj/*.traj.json` and screen logs in `logs/*.log`.
`textprobe` is the first run that checked text mode works (7B; same conditions as `text16k`). It is excluded from the aggregate. Result: wrong fix, and it overwrote the original JSON.

The local models fixed the bug in 4 of 27 runs, all of them by gemma4:e4b (4/6).
The Qwen2.5 family (3B/7B/14B) fixed it 0 times in 21 runs.
Claude Code fixed it with the same one-line change in 4 turns and about 14 seconds (`traj/claude-1.result.json`).

## 3. Failure 1: with Ollama's default context, the front of the conversation is truncated

`ollama ps` during the first run (default settings):

```
NAME                    ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen2.5:14b-instruct    7cdf5a0187d5    9.5 GB    100% GPU     4096       4 minutes from now
```

Ollama's log (journalctl, `logs/ollama-journal-ctx.log`):

```
11:41:38 slot   operator(): id  0 | task 3457 | new prompt, n_ctx_slot = 4096, n_keep = 4, task.n_tokens = 3996
11:41:41 slot   operator(): id  0 | task 3457 | slot context shift, n_keep = 4, n_left = 4091, n_discard = 2045
```

mini.yaml's system prompt and task message (the workflow and command rules) alone are fairly long, and `cat` of `out_loops.json` (22,658 bytes) pushes it past 4,096 tokens at once.
Context shift then discards the first 2,045 tokens, including the system prompt that has the instructions.
In all three ctx4096 runs, the model stopped issuing tool calls right after this and ended with `RepeatedFormatError` (3 consecutive format errors), after 5, 6 and 14 API calls.

With `num_ctx: 16384`, `ollama ps` showed `CONTEXT 16384` (11 GB, 100% GPU).
In the 16k runs, context shift happened once, at 12:11:49 during ctx16k-14b-3, while generating a long response (`n_left = 16379`).

## 4. Failure 2: the Qwen2.5 family drops out of the tool-calling format

In tool-calling mode (`ctx16k`), qwen2.5-coder:3b ended with `RepeatedFormatError` within 3 API calls in all 3 runs. None of the 3 executed a single command.
qwen2.5:7b also ended with `RepeatedFormatError` in all 3 runs (after 8, 4 and 30 API calls).
In the screen log, the model writes the command in a ```` ``` ```` block in the reply text, and mini-swe-agent responds with `No tool calls found in the response. Every response MUST include at least one tool call.` (`logs/ctx16k-7b-2.log`).

Text mode (`text16k`) got rid of most of the format errors, but no Qwen run fixed the bug.

## 5. Failure 3: each command runs in a new subshell, so `cd` doesn't persist

mini-swe-agent runs every command in a separate subprocess (`subprocess.run` / `docker exec`), so `cd` does not carry over to the next command. mini.yaml says so as well.
qwen2.5:14b (ctx16k-14b-1) ran the script fine with `cd` and then lost track of where it was in later commands.

```
[4] $ python3 regrade.py out_loops_copy.json
   -> python3: can't open file '/repo/regrade.py': [Errno 2] No such file or directory
[5] $ cd experiments/day-055 && python3 regrade.py out_loops_copy.json
   -> loops=1: ... loops=3: digits-concat 17/20, last-number 17/20 ...
[13] $ cp experiments/day-055/regrade.py .
[15] $ python3 regrade.py out_loops_copy.json
   -> FileNotFoundError: [Errno 2] No such file or directory: 'out_loops_copy.json'
```

It then copied `regrade.py` to the repository root and kept editing that copy, and hit the 30-step limit (`LimitsExceeded`). The original `experiments/day-055/regrade.py` was never changed.

## 6. Failure 4: unescaped `[0]` in sed silently did nothing

Every run that tried to rewrite `nums[0]` to `nums[-1]` with sed was counted, by whether the pattern escaped `[ ]` (checked in the trajectories).

- gemma4:e4b's 4 successful runs all used `nums\[0\]` (escaped).
- gemma4:e4b's 2 failed runs (ctx16k-3, text16k-2) both used `nums[0]` (unescaped).
- qwen2.5 also wrote the unescaped form in ctx16k-14b-2, ctx16k-7b-1 and text16k-14b-1.

In a regular expression, `[0]` is a bracket expression meaning "the single character 0", so `nums[0]` matches the string `nums0` and not `nums[0]`.
sed exits 0 even when nothing matches, so the agent sees no error. I confirmed this on the host. Both the host and the container have `sed (GNU sed) 4.9`.

```
$ printf 'last = nums[0].replace(",", "") if nums else ""\n' > t.py
$ sed -i 's/last = nums[0].replace(",", "") if nums else ""/last = nums[-1].replace(",", "") if nums else ""/' t.py; echo "rc=$?"; cat t.py
rc=0
last = nums[0].replace(",", "") if nums else ""
$ sed -i 's/last = nums\[0\].replace(",", "") if nums else ""/last = nums[-1].replace(",", "") if nums else ""/' t.py; echo "rc=$?"; cat t.py
rc=0
last = nums[-1].replace(",", "") if nums else ""
```

ctx16k-gemma4e4b-3 ran this no-op sed twice and submitted with `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` without re-running the script.
text16k-gemma4e4b-2 ran the script after the no-op sed and saw `last-number 17/20`, but still submitted.

## 7. Failure 5: overwriting the original JSON despite being told not to

`regrade.py` overwrites the JSON file it is given, and the task says "run it on a copy and do not modify out_loops.json itself".
qwen2.5:7b in text mode ran it on the original `out_loops.json` in all 3 runs (text16k-7b-1..3, plus textprobe).
qwen2.5-coder:3b (text16k-coder3b-1) also ran it on the original as its first command and submitted on the second.

```
[1] $ python experiments/day-055/regrade.py experiments/day-055/out_loops.json
   -> loops=1: ... loops=3: digits-concat 17/20, last-number 17/20 ...
[2] $ echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
```

text16k-7b-2 judged `ok += m["ok_lastnum"]` to be the problem and changed it to `ok += int(m["ok_lastnum"])`, but sed did not match because `[ ]` was not escaped. It submitted after 11 commands.

There were 5 runs that submitted (`exit_status: Submitted`) without fixing the bug: `ctx16k-gemma4e4b-3`, `textprobe`, `text16k-7b-2`, `text16k-gemma4e4b-2`, `text16k-coder3b-1`.

## 8. Successful example (ctx16k-gemma4e4b-2, 4 API calls, 31 seconds)

```
[1] $ cat experiments/day-055/regrade.py
[2] $ sed -i 's/last = nums\[0\].replace(\",\", \"\") if nums else \"\"/last = nums\[-1\].replace(\",\", \"\") if nums else \"\"/' experiments/day-055/regrade.py
[3] $ cp experiments/day-055/out_loops.json experiments/day-055/out_loops_copy.json && python experiments/day-055/regrade.py experiments/day-055/out_loops_copy.json
   -> loops=1: digits-concat 1/20, last-number 1/20
      loops=2: digits-concat 19/20, last-number 19/20
      loops=3: digits-concat 17/20, last-number 18/20
      loops=4: digits-concat 10/20, last-number 11/20
[4] $ echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
```

The resulting patch was the same one-line change as Claude Code's (`nums[0]` → `nums[-1]`).
In the 4 successful runs, `out_loops.json` was left unmodified and only the copy `out_loops_copy.json` remained (untracked).
Times for the successful runs: 77s / 31s / 24s / 15s (17 / 4 / 5 / 5 API calls).

## 9. About the agent implementation

`minisweagent/agents/default.py` in v2.4.6 is 190 lines, or 151 lines of code excluding docstrings, comments and blank lines. `environments/local.py` is 92 lines (76 lines of code).
The README says "Just some 100 lines of python for the agent class".
The loop is just "query the LLM → run the commands in its reply → append the output to the message list", and it ends when the output's first line is `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.

## 10. Problems in my own setup (not related to the agent; excluded from results)

- On the first launch, mini went into the interactive global config wizard and stopped with `Aborted.` because stdin was not a TTY. I avoided this with `MSWEA_CONFIGURED=true` and `MSWEA_GLOBAL_CONFIG_DIR=<working dir>`.
- When the working copy was in a folder under `/tmp`, Docker's bind mount gave an empty `/repo` (Docker Desktop + WSL2). I discarded that one run and moved the working copy under `~/.cache/day056-work/`.
- `grade.py`'s check for "was the original JSON modified" was initially a substring match, so it also matched `out_loops.json.test`. I fixed it to an exact path match and re-aggregated `results.jsonl`.

## 11. Not done

- SWE-bench Verified (README: >74%) was not reproduced.
- Each model was run only 3 times per condition. Ollama's default sampling settings were used and no seed was fixed.
- mini-swe-agent itself was not tried with Claude, because no API key was available.
