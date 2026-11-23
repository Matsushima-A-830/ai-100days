"""Grade one trial: run the (possibly fixed) regrade.py on a fresh copy of out_loops.json and compare."""
import json, os, shutil, subprocess, sys, tempfile
w, traj, secs, rc = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
expected = ["1/20", "19/20", "18/20", "11/20"]
tmp = tempfile.mkdtemp()
src = subprocess.run(["git", "-C", w, "show", "buggy:experiments/day-055/out_loops.json"], capture_output=True, text=True).stdout
open(f"{tmp}/o.json", "w").write(src)
r = subprocess.run([sys.executable, "-I", f"{w}/experiments/day-055/regrade.py", f"{tmp}/o.json"], capture_output=True, text=True, timeout=60)
got = [l.split("last-number ")[-1] for l in r.stdout.splitlines() if "last-number" in l]
diff = subprocess.run(["git", "-C", w, "status", "--porcelain"], capture_output=True, text=True).stdout.split("\n")
patch = subprocess.run(["git", "-C", w, "diff", "--", "experiments/day-055/regrade.py"], capture_output=True, text=True).stdout
t = json.load(open(traj)) if os.path.exists(traj) else {"info": {}, "messages": []}
info = t.get("info", {})
print(json.dumps({
    "trial": os.path.basename(w), "model": info.get("config", {}).get("model", {}).get("model_name"),
    "exit_status": info.get("exit_status"), "api_calls": info.get("model_stats", {}).get("api_calls"),
    "seconds": secs, "mini_rc": rc, "fixed": got == expected, "regrade_output": got or r.stderr[-300:],
    "json_untouched": not any(l[3:] == "experiments/day-055/out_loops.json" for l in diff), "changed_files": [l for l in diff if l],
    "patch": patch,
}, ensure_ascii=False))
shutil.rmtree(tmp)
