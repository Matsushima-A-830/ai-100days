import json, subprocess, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
CHUNK_DIR = os.path.join(BASE, "scratch-run")
WORKDIR = os.path.join(BASE, "direct-run")
RESUME_ID = sys.argv[1]

def run(prompt_text, resume_id):
    cmd = ["claude", "-p", prompt_text, "--output-format", "json", "--resume", resume_id]
    proc = subprocess.run(cmd, cwd=WORKDIR, capture_output=True, text=True, timeout=180)
    lines = [l for l in proc.stdout.strip().split("\n") if l.strip()]
    j = None
    for l in reversed(lines):
        try:
            j = json.loads(l); break
        except Exception:
            continue
    return j, proc.stdout, proc.stderr, proc.returncode

results = []
resume_id = RESUME_ID
for part in [5, 6]:
    fname = os.path.join(CHUNK_DIR, f"chunk_part_a{chr(ord('a')+part-1)}")
    with open(fname) as f:
        content = f.read()
    prompt = f"This is log segment {part} of 6. Just acknowledge with OK, nothing else.\n\n----LOG SEGMENT {part}----\n{content}\n----END SEGMENT----"
    j, out, err, rc = run(prompt, resume_id)
    if j is None:
        print("FAILED", rc, out[-2000:], err[-2000:], file=sys.stderr)
        break
    resume_id = j.get("session_id", resume_id)
    entry = {"turn": part, "cost_usd": j.get("total_cost_usd"), "usage": j.get("usage"), "result": j.get("result")}
    results.append(entry)
    print(json.dumps(entry, ensure_ascii=False))

with open(os.path.join(WORKDIR, "summary2.json"), "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
