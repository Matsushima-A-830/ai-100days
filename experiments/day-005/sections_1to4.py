"""
Soup (https://github.com/MakazhanAlpamys/Soup, Apache-2.0) notebooks/proof-4gb.ipynb
の section 1-4 を、Colab T4ではなくローカルのRTX 5060 Ti(16GB VRAM)上で再現するスクリプト。
元ノートブックのコード・コメントの意図をそのまま保持し、GPU固有のprintのみ実環境の値に追従する。
"""
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

import tempfile
from pathlib import Path

import torch
import soup_cli
import soup_cli.utils.gpu
from soup_cli.utils.gpu import bf16_fp16_flags

print("=== section 1: versions ===")
import bitsandbytes, peft, transformers
print("torch       ", torch.__version__)
print("transformers", transformers.__version__)
print("peft        ", peft.__version__)
print("bitsandbytes", bitsandbytes.__version__)
print("soup_cli    ", soup_cli.__version__)

print("\n=== section 2: GPU / bf16 ===")
assert torch.cuda.is_available(), "No GPU."
name = torch.cuda.get_device_name(0)
major, minor = torch.cuda.get_device_capability(0)
total = torch.cuda.get_device_properties(0).total_memory

print(f"GPU                   {name}  (sm_{major}{minor})")
print(f"VRAM                  {total / 1e9:.1f} GB")
print(f"bf16, incl. emulation {torch.cuda.is_bf16_supported()}")
print(f"bf16 IN HARDWARE      {torch.cuda.is_bf16_supported(including_emulation=False)}")

bf16, fp16 = bf16_fp16_flags("cuda")
print(f"Soup will train in    {'bf16' if bf16 else 'fp16' if fp16 else 'fp32'}")

print("\n=== section 3: cap this process to 4 GB ===")
BUDGET_BYTES = 4 * 1000**3
fraction = BUDGET_BYTES / total
torch.cuda.set_per_process_memory_fraction(fraction)
print(f"capped at {BUDGET_BYTES / 1e9:.2f} GB  (fraction {fraction:.3f} of this card)")

try:
    _ = torch.empty(int(BUDGET_BYTES * 1.15), dtype=torch.uint8, device="cuda")
    print("WARNING: the allocation succeeded - the cap is NOT in force")
except RuntimeError as exc:
    print("refused, as it should be:", str(exc).splitlines()[0][:90])

print("\n=== section 4: streamed == resident, bit for bit ===")
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM

from soup_cli.utils.layer_shard import shard_checkpoint
from soup_cli.utils.layer_stream import resolve_stream_dtype
from soup_cli.utils.layer_stream_runtime import build_streamed_model
from soup_cli.utils.spectrum_scan import resolve_model_weights

MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
DTYPE = resolve_stream_dtype("cuda")
LORA = LoraConfig(
    r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
    target_modules=["q_proj", "v_proj"], task_type=TaskType.CAUSAL_LM,
)

workdir = Path(tempfile.mkdtemp())
weights = resolve_model_weights(MODEL)
index = shard_checkpoint(weights, str(workdir / "shards"), dtype=DTYPE, arch="llama")
streamed, runtime = build_streamed_model(
    model_id=weights, shard_dir=str(workdir / "shards"), index=index,
    lora_config=LORA, device="cuda", dtype=DTYPE, buffers=2, pin=True, seed=0,
)
print(f"streamed: {index.n_layers} layers, dtype={DTYPE}")

# streamed.state_dict()のbase層weightはmetaテンソル(フォワード時に層ごとに
# ディスクから動的ロードされる設計のため実体を持たない)。load_state_dictでは
# 比較できないので、同じHFの重みを素直にGPUへ乗せたresidentモデルを別途構築し、
# 同一入力に対するフォワード出力(=凍結ベースのみ、LoRAはB=0初期化で無効)を比較する。
resident_base = AutoModelForCausalLM.from_pretrained(MODEL, dtype=DTYPE).to("cuda")
resident = get_peft_model(resident_base, LORA)

torch.manual_seed(0)
input_ids = torch.randint(0, 1000, (1, 16), device="cuda")

with torch.no_grad():
    out_streamed = streamed(input_ids=input_ids).logits
    out_resident = resident(input_ids=input_ids).logits

bit_exact = torch.equal(out_streamed, out_resident)
max_abs_diff = (out_streamed - out_resident).abs().max().item()
print(f"bit-exact (torch.equal): {bit_exact}")
print(f"max abs diff:            {max_abs_diff}")
