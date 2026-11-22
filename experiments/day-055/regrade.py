"""Re-grade the multiplication answers in out_loops.json using the last number in each reply.

run_loops.py concatenated every digit in the reply, so a reply such as
"438 × 70 = 30,660" was scored as wrong. Commas are thousands separators.
"""
import json, re, sys
d = json.load(open(sys.argv[1]))
for k, v in d["loops"].items():
    ok = 0
    for m in v["mul"]:
        nums = re.findall(r"\d[\d,]*", m["text"])
        last = nums[-1].replace(",", "") if nums else ""
        m["ok_lastnum"] = last == str(m["answer"])
        ok += m["ok_lastnum"]
    v["mul_correct_lastnum"] = ok
    print(f"loops={k}: digits-concat {v['mul_correct']}/20, last-number {ok}/20")
json.dump(d, open(sys.argv[1], "w"), ensure_ascii=False, indent=2)
