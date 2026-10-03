"""
Soup notebooks/proof-4gb.ipynb section 5相当: プロセスを4GBに制限した状態で
Llama-3.1-8B-InstructをNF4量子化+LoRA+layer streamingで実際に学習し、
measured peak VRAMがREADMEの主張(8Bモデルを4GB未満で学習可能)を満たすか確認する。
"""
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

import json
import torch
from pathlib import Path

BUDGET_BYTES = 4 * 1000**3
total = torch.cuda.get_device_properties(0).total_memory
fraction = BUDGET_BYTES / total
torch.cuda.set_per_process_memory_fraction(fraction)
print(f"capped at {BUDGET_BYTES / 1e9:.2f} GB (fraction {fraction:.3f} of {total/1e9:.1f} GB card)")

TOPICS = [
    ("streaming", "Only a couple of decoder layers are resident at any moment."),
    ("NF4", "Four-bit weights make the host-side store about four times smaller."),
    ("LoRA", "The base is frozen, so it is read and never written."),
    ("VRAM", "Peak memory is bounded by one layer instead of by the model."),
]
rows = [
    {"messages": [
        {"role": "user", "content": f"Question {i}: tell me about {topic}."},
        {"role": "assistant", "content": answer},
    ]}
    for i in range(8)
    for topic, answer in TOPICS
]
Path("train.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

config = """
base: NousResearch/Meta-Llama-3.1-8B-Instruct
task: sft
data:
  train: train.jsonl
  max_length: 256
training:
  epochs: 1
  batch_size: 1
  lr: 0.0002
  logging_steps: 1
  quantization: 4bit
  stream_layers: true
  stream_buffers: 2
  stream_vram_override: 4000000000
  lora:
    r: 8
    alpha: 16
output: ./out-8b
"""
Path("soup.yaml").write_text(config, encoding="utf-8")
print(config)

from soup_cli.config.loader import load_config_from_string
from soup_cli.data.loader import load_dataset
from soup_cli.trainer.sft import SFTTrainerWrapper

cfg = load_config_from_string(config)
dataset = load_dataset(cfg.data)

torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()

wrapper = SFTTrainerWrapper(cfg)
wrapper.setup(dataset)
result = wrapper.train()

print(f"\nsteps: {result['total_steps']}  loss: {result['initial_loss']:.3f} -> {result['final_loss']:.3f}")

peak = torch.cuda.max_memory_allocated()
print(f"peak VRAM allocated by this process: {peak / 1e9:.2f} GB")
print(f"budget this process was capped to:   {BUDGET_BYTES / 1e9:.2f} GB")

adapter = Path("out-8b/adapter_model.safetensors")
print(f"\nadapter written: {adapter.exists()}")
if adapter.exists():
    from safetensors.torch import load_file
    tensors = load_file(str(adapter))
    live = sum(1 for v in tensors.values() if v.abs().max().item() > 0)
    print(f"adapter tensors: {len(tensors)}, non-zero: {live}")

with open("section5_result.json", "w") as f:
    json.dump({
        "peak_vram_bytes": peak,
        "peak_vram_gb": peak / 1e9,
        "budget_gb": BUDGET_BYTES / 1e9,
        "steps": result["total_steps"],
        "initial_loss": result["initial_loss"],
        "final_loss": result["final_loss"],
        "adapter_written": adapter.exists(),
    }, f, indent=2)
