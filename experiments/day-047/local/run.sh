#!/bin/bash
# usage: run.sh <ollama-model>
M="$1"; P="my-ollama/$M"; B=http://localhost:10100
H=(-H "Content-Type: application/json")
A=(-H "x-api-key: dummy" -H "anthropic-version: 2023-06-01")
t(){ /usr/bin/time -f "  [time %e s]" "$@"; }

echo "### 0. warm-up (direct Ollama, load model)"
t curl -s localhost:11434/api/generate -d "{\"model\":\"$M\",\"prompt\":\"hi\",\"stream\":false,\"options\":{\"num_predict\":1}}" -o /dev/null
ollama ps | grep -F "$M"

Q='日本の首都はどこですか?理由を1文で添えて、日本語で答えてください。'
echo; echo "### 1a. Anthropic Messages  POST /v1/messages"
t curl -s -X POST $B/v1/messages "${H[@]}" "${A[@]}" -d "{\"model\":\"$P\",\"max_tokens\":128,\"messages\":[{\"role\":\"user\",\"content\":\"$Q\"}]}" -w "\nHTTP_STATUS:%{http_code}\n"
echo; echo "### 1b. OpenAI Chat Completions  POST /v1/chat/completions"
t curl -s -X POST $B/v1/chat/completions "${H[@]}" -d "{\"model\":\"$P\",\"messages\":[{\"role\":\"user\",\"content\":\"$Q\"}]}" -w "\nHTTP_STATUS:%{http_code}\n"
echo; echo "### 1c. OpenAI Responses  POST /v1/responses"
t curl -s -X POST $B/v1/responses "${H[@]}" -d "{\"model\":\"$P\",\"input\":\"$Q\"}" -w "\nHTTP_STATUS:%{http_code}\n"
echo; echo "### 1d. direct Ollama /v1/chat/completions (no proxy, baseline)"
t curl -s -X POST localhost:11434/v1/chat/completions "${H[@]}" -d "{\"model\":\"$M\",\"messages\":[{\"role\":\"user\",\"content\":\"$Q\"}]}" -w "\nHTTP_STATUS:%{http_code}\n"

echo; echo "### 2. Anthropic streaming (stream:true) — event types"
curl -s -N -X POST $B/v1/messages "${H[@]}" "${A[@]}" -d "{\"model\":\"$P\",\"max_tokens\":64,\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"1から5まで数字だけをカンマ区切りで。\"}]}" > /tmp/claude-1000/stream.txt
grep '^event:' /tmp/claude-1000/stream.txt | sort | uniq -c
grep -o '"text":"[^"]*"' /tmp/claude-1000/stream.txt | sed 's/"text"://; s/"//g' | tr -d '\n'; echo
grep 'message_delta' /tmp/claude-1000/stream.txt | head -1

TOOLS='[{"name":"get_weather","description":"Get the current weather for a city","input_schema":{"type":"object","properties":{"city":{"type":"string","description":"City name in English"}},"required":["city"]}}]'
echo; echo "### 3a. Anthropic tool use: tools -> tool_use block"
R=$(curl -s -X POST $B/v1/messages "${H[@]}" "${A[@]}" -d "{\"model\":\"$P\",\"max_tokens\":256,\"tools\":$TOOLS,\"messages\":[{\"role\":\"user\",\"content\":\"東京の今の天気を調べて。\"}]}")
echo "$R"
ID=$(echo "$R" | python3 -c "import json,sys; d=json.load(sys.stdin); print(next((c['id'] for c in d.get('content',[]) if c.get('type')=='tool_use'),''))")
echo "tool_use id: $ID"
if [ -n "$ID" ]; then
  echo; echo "### 3b. Anthropic tool_result round trip"
  ASSIST=$(echo "$R" | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['content'], ensure_ascii=False))")
  curl -s -X POST $B/v1/messages "${H[@]}" "${A[@]}" -d "{\"model\":\"$P\",\"max_tokens\":256,\"tools\":$TOOLS,\"messages\":[{\"role\":\"user\",\"content\":\"東京の今の天気を調べて。\"},{\"role\":\"assistant\",\"content\":$ASSIST},{\"role\":\"user\",\"content\":[{\"type\":\"tool_result\",\"tool_use_id\":\"$ID\",\"content\":\"{\\\"city\\\":\\\"Tokyo\\\",\\\"condition\\\":\\\"rain\\\",\\\"temp_c\\\":14}\"}]}]}" -w "\nHTTP_STATUS:%{http_code}\n"
fi
echo; echo "### 3c. Responses API tool call (function tools)"
curl -s -X POST $B/v1/responses "${H[@]}" -d "{\"model\":\"$P\",\"input\":\"東京の今の天気を調べて。\",\"tools\":[{\"type\":\"function\",\"name\":\"get_weather\",\"description\":\"Get the current weather for a city\",\"parameters\":{\"type\":\"object\",\"properties\":{\"city\":{\"type\":\"string\"}},\"required\":[\"city\"]}}]}" -w "\nHTTP_STATUS:%{http_code}\n"
