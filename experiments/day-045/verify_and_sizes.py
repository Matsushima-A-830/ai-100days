import json
import os

import torch
import transformers

BASE = "/tmp/claude-0/-home-user-ai-100days/0e7e5006-75af-513a-9114-d619a5310071/scratchpad/day045-src/qwen0.5b-base"
MASKED = "/tmp/claude-0/-home-user-ai-100days/0e7e5006-75af-513a-9114-d619a5310071/scratchpad/day045-work/qwen0.5b-masked"
MASK_DIR = "/tmp/claude-0/-home-user-ai-100days/0e7e5006-75af-513a-9114-d619a5310071/scratchpad/day045-src/mask_qwen0.5b"

base = transformers.AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16)
masked = transformers.AutoModelForCausalLM.from_pretrained(MASKED, dtype=torch.bfloat16)

name = "model.layers.0.mlp.gate_proj.weight"
b = dict(base.named_parameters())[name]
m = dict(masked.named_parameters())[name]
zeroed_in_masked_only = int(((b != 0) & (m == 0)).sum())
total = b.numel()
print(f"{name}: shape={tuple(b.shape)}, total={total}, zeroed_in_masked_but_nonzero_in_base={zeroed_in_masked_only}")
print(f"base all-zero count: {int((b == 0).sum())}, masked all-zero count: {int((m == 0).sum())}")

diffs = 0
for (n1, p1), (n2, p2) in zip(base.named_parameters(), masked.named_parameters()):
    assert n1 == n2
    if not torch.equal(p1, p2):
        diffs += 1
print(f"parameter tensors that differ between base and masked: {diffs} / {sum(1 for _ in base.named_parameters())}")

with open(os.path.join(MASK_DIR, "config.json")) as f:
    mask_cfg = json.load(f)
print("mask config.json:", mask_cfg)

base_bytes = os.path.getsize(os.path.join(BASE, "model.safetensors"))
masked_bytes = os.path.getsize(os.path.join(MASKED, "model.safetensors"))
mask_file_bytes = os.path.getsize(os.path.join(MASK_DIR, "model.safetensors"))
print(f"base model.safetensors: {base_bytes:,} bytes ({base_bytes/1024/1024:.1f} MB)")
print(f"masked (dense) model.safetensors: {masked_bytes:,} bytes ({masked_bytes/1024/1024:.1f} MB)")
print(f"released mask file (model.safetensors): {mask_file_bytes:,} bytes ({mask_file_bytes/1024/1024:.4f} MB)")
print(f"dense-checkpoint / mask-file size ratio: {masked_bytes / mask_file_bytes:.1f}x")

total_model_params = sum(p.numel() for p in base.parameters())
print(f"total base model parameters: {total_model_params:,}")
print(f"zero_params (deleted) / total model params = {mask_cfg['zero_params'] / total_model_params * 100:.4f}%")
