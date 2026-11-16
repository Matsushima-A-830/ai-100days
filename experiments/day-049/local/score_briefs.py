"""Score each brief.md against the 7 facts in notes1.md/notes2.md (keyword match) and list where the run stopped."""
import json, re, sys
from pathlib import Path

W = Path(sys.argv[1])  # /home/matsu/work-day049
FACTS = {
    "decision: delay redesign to Q1": [r"redesign", r"Q1"],
    "decision: idempotency keys": [r"idempotenc"],
    "open: dedicated QA hire": [r"QA"],
    "open: public postmortem": [r"postmortem|post-mortem"],
    "next: Daichi migration plan": [r"Daichi", r"migration"],
    "next: Priya customer survey": [r"Priya", r"survey"],
    "next: Kenji refund 40": [r"Kenji", r"refund", r"40"],
}
rows = []
for out in sorted((W / "out").glob("readme-*")):
    name = out.name
    brief = W / "ws" / name / "brief.md"
    s = json.loads((out / "summary.json").read_text())
    msgs = json.loads((out / "messages.json").read_text())
    msgs = msgs.get("messages", msgs) if isinstance(msgs, dict) else msgs
    calls = [c.get("function", c).get("name") for m in msgs for c in (m.get("tool_calls") or [])]
    text = brief.read_text() if brief.exists() else ""
    hit = [k for k, pats in FACTS.items() if text and all(re.search(p, text, re.I) for p in pats)]
    rows.append(dict(run=name, outcome=s.get("outcome"), wall=s.get("wall_seconds"), calls=calls,
                     brief=brief.exists(), facts=f"{len(hit)}/7"))
    print(f"{name:14} outcome={s.get('outcome'):9} wall={s.get('wall_seconds'):6.1f}s brief={'yes' if brief.exists() else 'no ':3} facts={len(hit)}/7 calls={','.join(calls) or '-'}")
json.dump(rows, open(Path(__file__).with_name("scores.json"), "w"), indent=1)
