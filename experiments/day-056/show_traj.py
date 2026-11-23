"""Print the bash commands an agent ran in a trajectory, with the first lines of each output."""
import json, sys
t = json.load(open(sys.argv[1])); n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
step = 0
for m in t["messages"]:
    ex = m.get("extra", {})
    if m.get("role") == "assistant":
        step += 1
        acts = ex.get("actions", [])
        print(f"--- step {step}: " + (" | ".join(a.get("command", "")[:300].replace("\n", "\\n") for a in acts) or "(no action) " + str(m.get("content"))[:200]))
    elif m.get("role") in ("tool", "user") and step:
        c = m.get("content")
        c = c if isinstance(c, str) else json.dumps(c)
        print("    " + "\n    ".join(c.strip().splitlines()[:n]))
    elif m.get("role") == "exit":
        print("=== exit:", ex.get("exit_status"))
