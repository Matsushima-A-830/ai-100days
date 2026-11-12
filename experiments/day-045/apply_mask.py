"""Apply a Deletion Tuning mask (packbits+zstd bitmap) to a base model's gate_proj weights.

Reimplementation of the logic in agentic-learning-ai-lab/deleting-weights' src/apply_mask.py
(MIT licensed), written independently so it can run outside that untrusted checkout: load the
boolean keep-mask per parameter name, zero every parameter entry where keep==False, save the
result. No other change is made to the model.
"""

import argparse
import json
import os

import numpy as np
import torch
import transformers
import zstandard
from safetensors.torch import load_file


def load_mask(mask_dir: str) -> dict[str, torch.Tensor]:
    with open(os.path.join(mask_dir, "config.json")) as f:
        fmt = json.load(f)["format"]
    assert fmt == "packbits_zstd", f"unsupported mask format {fmt!r}"
    tensors = load_file(os.path.join(mask_dir, "model.safetensors"), device="cpu")
    dctx = zstandard.ZstdDecompressor()
    masks = {}
    for key in tensors:
        if not key.endswith(".shape"):
            continue
        name = key[: -len(".shape")]
        shape = tuple(tensors[key].tolist())
        numel = int(np.prod(shape))
        packed = np.frombuffer(dctx.decompress(tensors[f"{name}.packed"].numpy().tobytes()), dtype=np.uint8)
        masks[name] = torch.from_numpy(np.unpackbits(packed)[:numel].astype(bool)).reshape(shape)
    return masks


@torch.no_grad()
def apply_mask(model: torch.nn.Module, masks: dict[str, torch.Tensor]) -> int:
    params = dict(model.named_parameters())
    missing = sorted(set(masks) - set(params))
    assert not missing, f"mask entries not found in the model: {missing[:3]}"
    deleted = 0
    for name, keep in masks.items():
        weight = params[name]
        assert keep.shape == weight.shape, f"{name}: mask {tuple(keep.shape)} vs weight {tuple(weight.shape)}"
        weight.mul_(keep.to(device=weight.device, dtype=weight.dtype))
        deleted += int((~keep).sum())
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", required=True)
    parser.add_argument("--mask_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    model = transformers.AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype=torch.bfloat16)
    deleted = apply_mask(model=model, masks=load_mask(mask_dir=args.mask_dir))
    model.save_pretrained(args.output_dir)
    transformers.AutoTokenizer.from_pretrained(args.base_model).save_pretrained(args.output_dir)
    print(f"deleted {deleted:,} weights; saved to {args.output_dir}")


if __name__ == "__main__":
    main()
