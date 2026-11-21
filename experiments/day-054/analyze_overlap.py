"""Overlay the model's per-frame transcript with the user audio's RMS, to check
whether Haru-4B actually speaks while the user is still talking (full-duplex)
rather than waiting for a pause. Used for results.md section 3.
"""
import json

import numpy as np
import soundfile as sf

data, sr = sf.read("assets/en_seg.wav")
frame = int(sr * 0.133)

with open("transcript_en_cpu_card.jsonl") as f:
    frames = [json.loads(line) for line in f if line.strip()]

for i, fr in enumerate(frames):
    seg = data[i * frame : (i + 1) * frame]
    rms = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2))) if len(seg) else 0.0
    text = fr["text"]
    if text.strip():
        state = "user talking" if rms > 0.01 else "user quiet"
        print(f"t={fr['time']:5.2f}s  user_rms={rms:.4f} ({state})  model_text={text!r}")
