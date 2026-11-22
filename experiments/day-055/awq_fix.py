"""Dequantize the AWQ-packed embedding and lm_head of SenseNova-Loop-9B-AWQ.

Transformers + gptqmodel load the decoder layers of the AWQ checkpoint, but the
checkpoint also stores `model.language_model.embed_tokens` and `lm_head` as
4-bit AWQ tensors (quantization_config.lm_head=True, embedding.layout=row_major).
Those are reported as UNEXPECTED (qweight/qzeros/scales) / MISSING (weight) and
left randomly initialised, so generation is garbage. This module rebuilds the
BF16 weights from the packed tensors.
"""
import json
import os

import torch
from safetensors import safe_open

AWQ_ORDER = [0, 2, 4, 6, 1, 3, 5, 7]  # nibble i holds column AWQ_ORDER[i] of each 8-group
SHIFTS = torch.arange(0, 32, 4, dtype=torch.int32)


def _unpack(q, order):
    """int32 [..., n] -> int [..., n*8] (4-bit values), columns restored to logical order."""
    vals = (q.unsqueeze(-1) >> SHIFTS.to(q.device)) & 0xF  # [..., n, 8] in nibble order
    if order == "awq":
        inv = torch.empty(8, dtype=torch.long)
        inv[torch.tensor(AWQ_ORDER)] = torch.arange(8)
        vals = vals[..., inv]
    return vals.flatten(-2)


def _tensor(path, name):
    idx = json.load(open(os.path.join(path, "model.safetensors.index.json")))["weight_map"]
    with safe_open(os.path.join(path, idx[name]), "pt") as f:
        return f.get_tensor(name)


def dequant_lm_head(path, order="awq", group=128):
    q = _tensor(path, "lm_head.qweight")          # [in, out/8]
    z = _tensor(path, "lm_head.qzeros")           # [in/g, out/8]
    s = _tensor(path, "lm_head.scales").float()   # [in/g, out]
    w = _unpack(q, order).float()                 # [in, out]
    zz = _unpack(z, order).float()                # [in/g, out]
    w = (w - zz.repeat_interleave(group, 0)) * s.repeat_interleave(group, 0)
    return w.t().contiguous()                     # [out, in] for nn.Linear


def dequant_embedding(path, order="awq", group=128):
    p = "model.language_model.embed_tokens."
    q = _tensor(path, p + "qweight")              # [vocab, hidden/8]
    z = _tensor(path, p + "qzeros")               # [vocab, (hidden/g)/8]
    s = _tensor(path, p + "scales").float()       # [vocab, hidden/g]
    w = _unpack(q, order).float()                 # [vocab, hidden]
    zz = _unpack(z, order).float()                # [vocab, hidden/g]
    return (w - zz.repeat_interleave(group, 1)) * s.repeat_interleave(group, 1)


def apply(model, path, emb_order="awq", head_order="awq"):
    text = model.model.language_model
    dev = text.embed_tokens.weight.device
    dtype = text.embed_tokens.weight.dtype  # the AWQ load casts the model to float16
    with torch.no_grad():
        text.embed_tokens.weight.data = dequant_embedding(path, emb_order).to(dev, dtype)
        model.lm_head.weight.data = dequant_lm_head(path, head_order).to(dev, dtype)
