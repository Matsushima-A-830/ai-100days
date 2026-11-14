#!/bin/bash
B='{"model":"MODEL","temperature":0,"max_tokens":32,"messages":[{"role":"user","content":"Count from 1 to 100 separated by commas."}]}'
for i in 1 2 3; do
  d=$(curl -s -o /tmp/claude-1000/d.json -w "%{time_total}" -X POST localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d "${B/MODEL/qwen2.5:32b-instruct}")
  p=$(curl -s -o /tmp/claude-1000/p.json -w "%{time_total}" -X POST localhost:10100/v1/chat/completions -H "Content-Type: application/json" -d "${B/MODEL/my-ollama/qwen2.5:32b-instruct}")
  dt=$(python3 -c "import json;print(json.load(open('/tmp/claude-1000/d.json'))['usage']['completion_tokens'])")
  pt=$(python3 -c "import json;print(json.load(open('/tmp/claude-1000/p.json'))['usage']['completion_tokens'])")
  echo "run$i  direct ${d}s (${dt} tok)   via-opencodex ${p}s (${pt} tok)"
done
echo "--- ollama native eval rate (32B)"
curl -s localhost:11434/api/generate -d '{"model":"qwen2.5:32b-instruct","prompt":"Count from 1 to 100 separated by commas.","stream":false,"options":{"temperature":0,"num_predict":64}}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('eval %d tok in %.2fs = %.1f tok/s'%(d['eval_count'], d['eval_duration']/1e9, d['eval_count']/(d['eval_duration']/1e9)))"
ollama ps
