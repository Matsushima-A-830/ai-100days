"""
adapter_model.safetensorsが空になる原因を、小型モデル(SmolLM2-135M)で高速に再現・診断する。
学習後、(1) model.state_dict()に直接lora_A/lora_Bが実在し非ゼロか、
(2) PEFTのget_peft_model_state_dict()が何を返すか、の2点を切り分ける。
"""
import json
from pathlib import Path

import torch

TOPICS = [
    ("streaming", "Only a couple of decoder layers are resident at any moment."),
    ("NF4", "Four-bit weights make the host-side store about four times smaller."),
]
rows = [
    {"messages": [
        {"role": "user", "content": f"Question {i}: tell me about {topic}."},
        {"role": "assistant", "content": answer},
    ]}
    for i in range(4)
    for topic, answer in TOPICS
]
Path("train_small.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

config = """
base: HuggingFaceTB/SmolLM2-135M-Instruct
task: sft
data:
  train: train_small.jsonl
  max_length: 128
training:
  epochs: 1
  batch_size: 1
  lr: 0.0002
  logging_steps: 1
  quantization: none
  stream_layers: true
  stream_buffers: 2
  stream_vram_override: 4000000000
  lora:
    r: 8
    alpha: 16
output: ./out-debug
"""
Path("soup_debug.yaml").write_text(config, encoding="utf-8")

from soup_cli.config.loader import load_config_from_string
from soup_cli.data.loader import load_dataset
from soup_cli.trainer.sft import SFTTrainerWrapper

cfg = load_config_from_string(config)
dataset = load_dataset(cfg.data)

wrapper = SFTTrainerWrapper(cfg)
wrapper.setup(dataset)
result = wrapper.train()
print(f"steps: {result['total_steps']}  loss: {result['initial_loss']:.3f} -> {result['final_loss']:.3f}")

model = wrapper.model
print("\n=== model.state_dict() direct inspection ===")
sd = model.state_dict()
lora_keys = [k for k in sd if "lora_" in k]
print(f"total keys: {len(sd)}, lora_ keys: {len(lora_keys)}")
for k in lora_keys[:6]:
    t = sd[k]
    print(f"  {k}: shape={tuple(t.shape)} is_meta={t.is_meta} max_abs={'meta' if t.is_meta else t.abs().max().item()}")

print("\n=== peft.get_peft_model_state_dict() ===")
from peft import get_peft_model_state_dict
peft_sd = get_peft_model_state_dict(model)
print(f"get_peft_model_state_dict returned {len(peft_sd)} keys")
for k in list(peft_sd.keys())[:6]:
    t = peft_sd[k]
    print(f"  {k}: shape={tuple(t.shape)} is_meta={t.is_meta} max_abs={'meta' if t.is_meta else t.abs().max().item()}")

print("\n=== named_parameters() with requires_grad=True ===")
trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
print(f"trainable param count: {len(trainable)}")
for n, p in trainable[:6]:
    print(f"  {n}: shape={tuple(p.shape)} is_meta={p.is_meta}")
