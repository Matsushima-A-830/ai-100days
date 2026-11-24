"""Run one of the day-057 scripts unchanged, but on a chosen device / dtype.

Usage: python run_device.py <script.py> <cpu|cuda> <bf16|fp32>

The original scripts load models on CPU in BF16. This wrapper patches
`AutoModelForCausalLM.from_pretrained` (to override dtype and move the model to the
device) and `GenerationMixin.generate` (to move input tensors to the model's device),
then executes the script with runpy. Prompts, decoding (greedy) and post-processing
are untouched, so any difference in output comes from device / precision only.
"""
import runpy
import sys

import torch
import transformers
from transformers.generation.utils import GenerationMixin

script, device, dtype_name = sys.argv[1], sys.argv[2], sys.argv[3]
dtype = {"bf16": torch.bfloat16, "fp32": torch.float32}[dtype_name]

_orig_fp = transformers.AutoModelForCausalLM.from_pretrained.__func__


def _from_pretrained(cls, *args, **kwargs):
    kwargs.pop("torch_dtype", None)
    kwargs["dtype"] = dtype
    return _orig_fp(cls, *args, **kwargs).to(device)


transformers.AutoModelForCausalLM.from_pretrained = classmethod(_from_pretrained)

_orig_gen = GenerationMixin.generate


def _generate(self, *args, **kwargs):
    for k, v in list(kwargs.items()):
        if torch.is_tensor(v):
            kwargs[k] = v.to(self.device)
    return _orig_gen(self, *args, **kwargs)


GenerationMixin.generate = _generate

print(f"[run_device] script={script} device={device} dtype={dtype_name} "
      f"torch={torch.__version__} transformers={transformers.__version__}"
      + (f" gpu={torch.cuda.get_device_name(0)}" if device == "cuda" else ""), flush=True)
sys.argv = [script]
runpy.run_path(script, run_name="__main__")
