import json
import subprocess
import sys
import os

MODE = sys.argv[1]  # "direct" or "bili"
WORKDIR = sys.argv[2]
BASE = os.path.dirname(os.path.abspath(__file__))
BILI_BIN = os.path.join(BASE, "node_modules", ".bin", "bili")
CHUNK_DIR = os.path.join(BASE, "scratch-run")

os.makedirs(WORKDIR, exist_ok=True)

def build_prompt(part_num, total, chunk_file, extra_question):
    with open(chunk_file) as f:
        content = f.read()
    header = f"This is log segment {part_num} of {total}. Just acknowledge with OK, nothing else."
    if extra_question:
        header = extra_question
    return f"{header}\n\n----LOG SEGMENT {part_num}----\n{content}\n----END SEGMENT----"

def run_turn(prompt_text, resume_id, allowed_tools=None):
    prompt_path = os.path.join(WORKDIR, "prompt_tmp.txt")
    with open(prompt_path, "w") as f:
        f.write(prompt_text)

    if MODE == "bili":
        cmd = [BILI_BIN, "claude", "--", "-p", prompt_text, "--output-format", "json"]
        if allowed_tools:
            cmd += ["--allowedTools", allowed_tools]
    else:
        cmd = ["claude", "-p", prompt_text, "--output-format", "json"]
    if resume_id:
        cmd += ["--resume", resume_id]

    proc = subprocess.run(cmd, cwd=WORKDIR, capture_output=True, text=True, timeout=150)
    stdout = proc.stdout
    stderr = proc.stderr
    lines = [l for l in stdout.strip().split("\n") if l.strip()]
    json_line = None
    for l in reversed(lines):
        try:
            json_line = json.loads(l)
            break
        except Exception:
            continue
    return json_line, stdout, stderr, proc.returncode

def main():
    total_segments = 4
    results = []
    resume_id = None
    for i in range(1, total_segments + 1):
        chunk_file = os.path.join(CHUNK_DIR, f"chunk_part_a{chr(ord('a') + i - 1)}")
        extra = None
        if i == total_segments:
            extra = "This is the final log segment. Now answer: what is the numeric value= on the line starting with LOG-00001 (from the very first segment)? Reply with just the number, nothing else."
        prompt_text = build_prompt(i, total_segments, chunk_file, extra)
        j, out, err, rc = run_turn(prompt_text, resume_id, allowed_tools="mcp__bili__acp_status" if MODE == "bili" else None)
        if j is None:
            print(f"TURN {i} FAILED rc={rc}", file=sys.stderr)
            print("STDOUT:", out[-2000:], file=sys.stderr)
            print("STDERR:", err[-2000:], file=sys.stderr)
            results.append({"turn": i, "error": True, "stdout_tail": out[-1000:], "stderr_tail": err[-1000:]})
            break
        resume_id = j.get("session_id", resume_id)
        usage = j.get("usage", {})
        entry = {
            "turn": i,
            "session_id": resume_id,
            "cost_usd": j.get("total_cost_usd"),
            "input_tokens": usage.get("input_tokens"),
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "result": j.get("result"),
        }
        results.append(entry)
        print(json.dumps(entry, ensure_ascii=False))

    # final: bili-only acp_status call
    if MODE == "bili" and resume_id and not any(r.get("error") for r in results):
        j, out, err, rc = run_turn(
            "Call the acp_status tool and report its complete raw output verbatim, nothing else added.",
            resume_id,
            allowed_tools="mcp__bili__acp_status",
        )
        if j:
            entry = {
                "turn": "acp_status",
                "session_id": resume_id,
                "cost_usd": j.get("total_cost_usd"),
                "usage": j.get("usage"),
                "result": j.get("result"),
            }
            results.append(entry)
            print(json.dumps(entry, ensure_ascii=False))
        else:
            print("acp_status call failed", out[-1000:], err[-1000:], file=sys.stderr)

    with open(os.path.join(WORKDIR, "summary.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total_cost = sum(r.get("cost_usd", 0) or 0 for r in results)
    print(f"TOTAL COST: {total_cost}")

if __name__ == "__main__":
    main()
