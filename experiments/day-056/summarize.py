"""Aggregate results.jsonl by condition (prefix of the trial name) and model."""
import json, collections
rows = [json.loads(l) for l in open("results.jsonl")]
g = collections.defaultdict(list)
for d in rows:
    if d["trial"] == "textprobe":
        continue
    cond = d["trial"].rsplit("-", 2)[0] if d["trial"] != "claude-1" else "claude-code"
    g[(cond, d["model"])].append(d)
print(f"{'condition':12} {'model':40} fixed  submitted  json_overwritten  median_s")
for (c, m), v in g.items():
    secs = sorted(x["seconds"] for x in v)
    print(f"{c:12} {m:40} {sum(x['fixed'] for x in v)}/{len(v)}    {sum(x['exit_status']=='Submitted' for x in v)}/{len(v)}        "
          f"{sum(not x['json_untouched'] for x in v)}/{len(v)}               {secs[len(secs)//2]}")
print("submitted but not fixed:", [d["trial"] for d in rows if d["exit_status"] == "Submitted" and not d["fixed"]])
