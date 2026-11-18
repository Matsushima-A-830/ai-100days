"""Before/After generation comparison for MiniMind weights (non-interactive).

Same model loading / generation settings as the official eval_llm.py
(fp16, do_sample, top_p=0.95, temperature=0.85, repetition_penalty=1), but with
fixed prompts and a fixed seed per prompt so runs are reproducible.

Run from the minimind repository root:
    python /path/to/gen_compare.py --weight_path out/pretrain_768.pth --is_pretrain 1
    python /path/to/gen_compare.py --weight_path out/full_sft_768.pth --is_pretrain 0
"""
import argparse
import sys
import time
import warnings

import torch
from transformers import AutoTokenizer

sys.path.insert(0, ".")
from model.model_minimind import MiniMindConfig, MiniMindForCausalLM  # noqa: E402
from trainer.trainer_utils import setup_seed  # noqa: E402

warnings.filterwarnings("ignore")

PROMPTS = [
    "你有什么特长？",
    "为什么天空是蓝色的",
    '解释一下"光合作用"的基本过程',
    "推荐一些中国的美食",
]

p = argparse.ArgumentParser()
p.add_argument("--weight_path", required=True)
p.add_argument("--is_pretrain", type=int, default=0)
p.add_argument("--tokenizer_path", default="./model")
p.add_argument("--seed", type=int, default=42)
p.add_argument("--max_new_tokens", type=int, default=80)
p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
args = p.parse_args()

tok = AutoTokenizer.from_pretrained(args.tokenizer_path)
model = MiniMindForCausalLM(MiniMindConfig(hidden_size=768, num_hidden_layers=8))
model.load_state_dict(torch.load(args.weight_path, map_location=args.device), strict=True)
model = model.half().eval().to(args.device)

print(f"weight={args.weight_path} is_pretrain={args.is_pretrain} seed={args.seed} device={args.device}")
for prompt in PROMPTS:
    setup_seed(args.seed)
    if args.is_pretrain:
        text = tok.bos_token + prompt
    else:
        text = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                       tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt", truncation=True).to(args.device)
    t0 = time.time()
    out = model.generate(
        inputs=inputs["input_ids"], attention_mask=inputs["attention_mask"],
        max_new_tokens=args.max_new_tokens, do_sample=True,
        pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id,
        top_p=0.95, temperature=0.85, repetition_penalty=1,
    )
    dt = time.time() - t0
    n = len(out[0]) - len(inputs["input_ids"][0])
    resp = tok.decode(out[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
    print("=" * 60)
    print(f"PROMPT: {prompt}")
    print(f"RESPONSE: {resp}")
    print(f"[{n} tokens in {dt:.2f}s, {n / dt:.2f} tok/s]")
