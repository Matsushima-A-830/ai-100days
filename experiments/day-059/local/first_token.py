"""Show Qwen3-0.6B's first-token distribution on harmless prompts, with and without the closed <think></think> prefix."""
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
m = "Qwen/Qwen3-0.6B"
tok = AutoTokenizer.from_pretrained(m)
model = AutoModelForCausalLM.from_pretrained(m, dtype=torch.float32)
prompts = load_dataset("mlabonne/harmless_alpaca", split="test[:20]")["text"]
for prefix in ["", "<think>\n\n</think>\n\n"]:
    tops = []
    for p in prompts:
        chat = tok.apply_chat_template([{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": p}], add_generation_prompt=True, tokenize=False) + prefix
        ids = tok(chat, return_tensors="pt")
        with torch.no_grad():
            pr = model(**ids).logits[0, -1].softmax(-1)
        v, i = pr.max(-1)
        tops.append((tok.decode(i), round(v.item(), 4)))
    print(repr(prefix), "top1 tokens:", sorted(set(t for t, _ in tops)), "min top1 prob:", min(p for _, p in tops), "mean:", round(sum(p for _, p in tops)/len(tops), 4))
print("template tail:", repr(tok.apply_chat_template([{"role": "user", "content": "hi"}], add_generation_prompt=True, tokenize=False)[-40:]))
