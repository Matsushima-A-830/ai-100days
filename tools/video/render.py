#!/usr/bin/env python3
"""Render the ~1 minute architecture explainer video for a day.

Input : posts/video/day-NNN.json (scene spec, see tools/video/README.md)
Output: posts/video/day-NNN.mp4 (1080x1920, H.264 + AAC) and posts/video/day-NNN.srt

The look (colors, fonts, layout, scene order) is fixed here so every day has the same format.
Only the spec JSON changes from day to day.

Usage:
    python tools/video/render.py posts/video/day-048.json            # full render with narration
    python tools/video/render.py posts/video/day-048.json --no-tts   # silent preview (no voice download)
    python tools/video/render.py posts/video/day-048.json --check    # validate spec + print timing only
    python tools/video/render.py posts/video/day-048.json --stills DIR  # one PNG per segment (for review)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"

W, H, FPS = 1080, 1920, 30
VOICE = os.environ.get("AI100_VOICE", "en_US-ljspeech-high")  # public domain dataset
VOICE_DIR = Path(os.environ.get("AI100_VOICE_DIR", Path.home() / ".cache" / "ai100days" / "piper"))
GAP = 0.45            # silence after each narration segment (s)
FADE = 0.30           # scene fade-in (s)
WPS_ESTIMATE = 2.6    # words/sec used for --no-tts timing
MIN_TOTAL, MAX_TOTAL = 45.0, 75.0
SCENE_ORDER = ["title", "overview", "architecture", "finding", "outro"]

# Dark palette = the dark-mode tokens of tools/card-template.html
C = {
    "bg": (14, 18, 24), "surface": (22, 27, 36), "ink": (232, 235, 240), "muted": (151, 161, 178),
    "faint": (98, 109, 128), "border": (38, 46, 59), "accent": (226, 121, 63), "blue": (79, 147, 234),
    "good": (76, 194, 131), "bad": (239, 106, 99), "term": (9, 11, 16), "term_ink": (221, 227, 236),
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)


F = {
    "eyebrow": font("IBMPlexMono-Regular", 30),
    "title": font("Fraunces-SemiBold", 132),
    "h": font("Fraunces-SemiBold", 78),
    "sub": font("IBMPlexSans-Regular", 50),
    "body": font("IBMPlexSans-Regular", 52),
    "bodyb": font("IBMPlexSans-SemiBold", 48),
    "node": font("IBMPlexSans-SemiBold", 42),
    "nodesub": font("IBMPlexMono-Regular", 28),
    "edge": font("IBMPlexMono-Regular", 27),
    "mono": font("IBMPlexMono-Regular", 34),
    "monob": font("IBMPlexMono-Medium", 34),
    "stat": font("Fraunces-SemiBold", 230),
    "cap": font("IBMPlexSans-SemiBold", 46),
    "small": font("IBMPlexMono-Regular", 28),
}


# ---------------------------------------------------------------- spec / validation

class SpecError(Exception):
    pass


def load_spec(path: Path) -> dict:
    spec = json.loads(path.read_text(encoding="utf-8"))
    for k in ["day", "project", "tagline", "source_url", "license", "scenes"]:
        if k not in spec:
            raise SpecError(f"missing top-level key: {k}")
    types = [s.get("type") for s in spec["scenes"]]
    if types != SCENE_ORDER:
        raise SpecError(f"scenes must be exactly {SCENE_ORDER} in this order, got {types}")
    sc = {s["type"]: s for s in spec["scenes"]}
    for t in ["title", "overview", "finding", "outro"]:
        if not sc[t].get("narration"):
            raise SpecError(f"scene '{t}' needs narration")
    ov = sc["overview"]
    if not 2 <= len(ov.get("bullets", [])) <= 4:
        raise SpecError("overview.bullets must have 2-4 items")
    arch = sc["architecture"]
    nodes = arch.get("nodes", [])
    if not 3 <= len(nodes) <= 8:
        raise SpecError("architecture.nodes must have 3-8 items")
    ids = {n["id"] for n in nodes}
    for n in nodes:
        col, row = n.get("pos", [None, None])
        if col not in (0, 1, 2) or not isinstance(row, int) or not 0 <= row <= 5:
            raise SpecError(f"node {n['id']}: pos must be [col 0-2, row 0-5]")
    for e in arch.get("edges", []):
        if e["from"] not in ids or e["to"] not in ids:
            raise SpecError(f"edge {e} refers to unknown node")
    steps = arch.get("steps", [])
    if not 2 <= len(steps) <= 4:
        raise SpecError("architecture.steps must have 2-4 items")
    for s in steps:
        if not s.get("narration"):
            raise SpecError("each architecture step needs narration")
        for nid in s.get("focus", []):
            if nid not in ids:
                raise SpecError(f"step focus refers to unknown node {nid}")
    fd = sc["finding"]
    if not fd.get("stat") or not fd.get("caption"):
        raise SpecError("finding needs stat and caption")
    return spec


# ---------------------------------------------------------------- timeline

@dataclass
class Segment:
    scene: dict
    step: int            # architecture step index, else 0
    narration: str
    wav: Path | None = None
    dur: float = 0.0     # audio length
    start: float = 0.0
    captions: list[tuple[float, float, str]] = field(default_factory=list)

    @property
    def length(self) -> float:
        return self.dur + GAP


def build_segments(spec: dict) -> list[Segment]:
    segs = []
    for s in spec["scenes"]:
        if s["type"] == "architecture":
            for i, st in enumerate(s["steps"]):
                segs.append(Segment(s, i, st["narration"]))
        else:
            segs.append(Segment(s, 0, s["narration"]))
    return segs


# Spoken forms for the voice only; captions/SRT keep the original text.
SAY = {r"\bAI\b": "A I", r"\bAPI\b": "A P I", r"\bAPIs\b": "A P Is", r"\bLLM\b": "L L M",
       r"\bLLMs\b": "L L Ms", r"\bGPU\b": "G P U", r"\bCLI\b": "C L I", r"\bSQL\b": "S Q L",
       r"\bOSS\b": "O S S", r"\bJSON\b": "Jason", r"\bUI\b": "U I", r"\bvs\.?": "versus",
       r"(\d+)B\b": r"\1 B", r"\bDay 0*(\d+)\b": r"Day \1"}


def spoken(text: str) -> str:
    for pat, rep in SAY.items():
        text = re.sub(pat, rep, text)
    return text


def ensure_voice() -> Path:
    onnx = VOICE_DIR / f"{VOICE}.onnx"
    if not onnx.exists():
        VOICE_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir", str(VOICE_DIR), VOICE],
                       check=True)
    return onnx


def synth(segs: list[Segment], tmp: Path, tts: bool) -> None:
    voice = None
    if tts:
        from piper import PiperVoice  # imported lazily so --no-tts/--check need no piper
        voice = PiperVoice.load(str(ensure_voice()))
    for i, seg in enumerate(segs):
        if voice:
            seg.wav = tmp / f"seg{i:02d}.wav"
            with wave.open(str(seg.wav), "wb") as w:
                voice.synthesize_wav(spoken(seg.narration), w)
            with wave.open(str(seg.wav)) as w:
                seg.dur = w.getnframes() / w.getframerate()
        else:
            seg.dur = len(seg.narration.split()) / WPS_ESTIMATE
    t = 0.0
    for seg in segs:
        seg.start = t
        seg.captions = caption_chunks(seg.narration, t, seg.dur)
        t += seg.length


def caption_chunks(text: str, start: float, dur: float, max_chars: int = 62) -> list[tuple[float, float, str]]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    for s in sentences:
        while len(s) > max_chars:
            cut = max((m.end() for m in re.finditer(r"[,;:]\s|\s(?:and|but|then|so|which|while)\s", s[: max_chars + 1])),
                      default=0)
            if cut < max_chars * 0.4:
                cut = s.rfind(" ", 0, max_chars + 1)
            chunks.append(s[:cut].strip())
            s = s[cut:].strip()
        if s:
            chunks.append(s)
    total = sum(len(c) for c in chunks) or 1
    out, t = [], start
    for c in chunks:
        d = dur * len(c) / total
        out.append((t, t + d, c))
        t += d
    return out


def concat_audio(segs: list[Segment], out: Path, rate: int = 22050) -> None:
    with wave.open(str(out), "wb") as o:
        o.setnchannels(1)
        o.setsampwidth(2)
        o.setframerate(rate)
        for seg in segs:
            with wave.open(str(seg.wav)) as w:
                assert w.getframerate() == rate and w.getnchannels() == 1
                o.writeframes(w.readframes(w.getnframes()))
            o.writeframes(b"\x00\x00" * int(GAP * rate))


def write_srt(segs: list[Segment], out: Path) -> None:
    def ts(x: float) -> str:
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    lines, n = [], 1
    for seg in segs:
        for a, b, c in seg.captions:
            lines += [str(n), f"{ts(a)} --> {ts(b)}", c, ""]
            n += 1
    out.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- drawing helpers

def wrap(d: ImageDraw.ImageDraw, text: str, f, width: int) -> list[str]:
    out = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=f) <= width or not cur:
                cur = t
            else:
                out.append(cur)
                cur = word
        out.append(cur)
    return out


def text_block(d, xy, text, f, fill, width, spacing=1.25) -> int:
    x, y = xy
    lh = int(f.size * spacing)
    for line in wrap(d, text, f, width):
        d.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def arrow(d, p0, p1, color, width=5, head=22):
    d.line([p0, p1], fill=color, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = [p1,
           (p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)),
           (p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45))]
    d.polygon(pts, fill=color)


def clip_to_box(c, other, box):
    """Point where the segment c->other leaves the rectangle box (centered at c)."""
    x0, y0, x1, y1 = box
    dx, dy = other[0] - c[0], other[1] - c[1]
    hw, hh = (x1 - x0) / 2 + 6, (y1 - y0) / 2 + 6
    s = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return (c[0] + dx * s, c[1] + dy * s)


# ---------------------------------------------------------------- scenes

TOP, CAP_Y = 250, 1540
X0, CW = 90, W - 180


def chrome(img, d, spec, t, total):
    day = f"{int(spec['day']):03d}"
    x = X0
    for txt, col in [(f"$ day-{day}", C["muted"]), ("  /  ", C["faint"]),
                     (spec.get("slug", spec["project"].lower()), C["accent"]), ("  /  ", C["faint"]),
                     ("100 days of AI", C["muted"])]:
        d.text((x, 110), txt, font=F["eyebrow"], fill=col)
        x += d.textlength(txt, font=F["eyebrow"])
    # progress bar + day counter
    y = 1830
    d.rounded_rectangle([X0, y, W - X0 - 170, y + 8], 4, fill=C["border"])
    frac = min(1.0, t / total) if total else 0
    d.rounded_rectangle([X0, y, X0 + int((W - 2 * X0 - 170) * frac), y + 8], 4, fill=C["accent"])
    d.text((W - X0 - 140, y - 14), f"{day} / 100", font=F["small"], fill=C["faint"])


def caption(d, text):
    if not text:
        return
    lines = wrap(d, text, F["cap"], CW - 60)[:3]
    lh = 62
    h = lh * len(lines) + 44
    y0 = CAP_Y + (230 - h) // 2
    d.rounded_rectangle([X0 - 10, y0, W - X0 + 10, y0 + h], 22, fill=(0, 0, 0))
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=F["cap"])
        d.text(((W - tw) / 2, y0 + 22 + i * lh), ln, font=F["cap"], fill=(255, 255, 255))


def heading(d, text, y=TOP):
    return text_block(d, (X0, y), text, F["h"], C["ink"], CW, 1.15) + 30


def scene_title(d, spec, sc, prog):
    y = 420
    d.text((X0, y), f"DAY {int(spec['day']):03d}", font=F["monob"], fill=C["accent"])
    y = text_block(d, (X0, y + 70), spec["project"], F["title"], C["ink"], CW, 1.08) + 30
    y = text_block(d, (X0, y), spec["tagline"], F["sub"], C["muted"], CW, 1.35) + 60
    x = X0
    for chip in [f"License: {spec['license']}", "Tested hands-on"]:
        tw = d.textlength(chip, font=F["small"])
        d.rounded_rectangle([x, y, x + tw + 44, y + 64], 32, outline=C["border"], width=3)
        d.text((x + 22, y + 14), chip, font=F["small"], fill=C["muted"])
        x += tw + 70


def scene_overview(d, spec, sc, prog):
    y = heading(d, sc.get("heading", "What is it?"))
    n = len(sc["bullets"])
    shown = min(n, 1 + int(prog * n * 1.15))
    for i, b in enumerate(sc["bullets"][:shown]):
        d.rounded_rectangle([X0, y + 18, X0 + 18, y + 36], 4, fill=C["accent"])
        y = text_block(d, (X0 + 50, y), b, F["body"], C["ink"], CW - 50, 1.3) + 34


def node_geometry(nodes):
    cols = sorted({n["pos"][0] for n in nodes})
    rows = max(n["pos"][1] for n in nodes) + 1
    ncol = max(cols) + 1
    gap_x = 120
    bw = (CW - gap_x * (ncol - 1)) / ncol
    area_top, area_h = TOP + 150, CAP_Y - 70 - (TOP + 150)
    bh = min(170, area_h / rows - 70)
    pitch = area_h / rows
    geo = {}
    for n in nodes:
        c, r = n["pos"]
        span = n.get("span", 1)
        x0 = X0 + c * (bw + gap_x)
        x1 = x0 + bw * span + gap_x * (span - 1)
        y0 = area_top + r * pitch + (pitch - bh) / 2
        geo[n["id"]] = (x0, y0, x1, y0 + bh)
    return geo


def scene_architecture(d, spec, sc, prog, step):
    heading(d, sc.get("heading", "How it works"))
    nodes, edges = sc["nodes"], sc.get("edges", [])
    geo = node_geometry(nodes)
    st = sc["steps"][step]
    focus = set(st.get("focus", []))
    center = {k: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for k, b in geo.items()}
    for e in edges:
        hot = e["from"] in focus and e["to"] in focus
        col = C["accent"] if hot else C["faint"]
        a, b = center[e["from"]], center[e["to"]]
        p0, p1 = clip_to_box(a, b, geo[e["from"]]), clip_to_box(b, a, geo[e["to"]])
        arrow(d, p0, p1, col, 6 if hot else 4)
        if e.get("label"):
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            if abs(p1[1] - p0[1]) < 1:   # horizontal edge: label goes above the boxes (the gap is narrow)
                my = min(geo[e["from"]][1], geo[e["to"]][1]) - 30
            tw = d.textlength(e["label"], font=F["edge"])
            d.rounded_rectangle([mx - tw / 2 - 12, my - 22, mx + tw / 2 + 12, my + 22], 10, fill=C["bg"])
            d.text((mx - tw / 2, my - 17), e["label"], font=F["edge"], fill=C["accent"] if hot else C["muted"])
    for n in nodes:
        x0, y0, x1, y1 = geo[n["id"]]
        hot = n["id"] in focus
        d.rounded_rectangle([x0, y0, x1, y1], 22, fill=C["surface"],
                            outline=C["accent"] if hot else C["border"], width=6 if hot else 3)
        label_col = C["ink"] if hot or not focus else C["muted"]
        lines = wrap(d, n["label"], F["node"], x1 - x0 - 40)[:2]
        sub = n.get("sub")
        th = len(lines) * 52 + (40 if sub else 0)
        ty = (y0 + y1) / 2 - th / 2
        for ln in lines:
            tw = d.textlength(ln, font=F["node"])
            d.text(((x0 + x1) / 2 - tw / 2, ty), ln, font=F["node"], fill=label_col)
            ty += 52
        if sub:
            size = 28
            while size > 20 and d.textlength(sub, font=font("IBMPlexMono-Regular", size)) > x1 - x0 - 30:
                size -= 1
            fs = font("IBMPlexMono-Regular", size)
            tw = d.textlength(sub, font=fs)
            d.text(((x0 + x1) / 2 - tw / 2, ty + 4), sub, font=fs, fill=C["accent"] if hot else C["faint"])
    # step dots
    for i in range(len(sc["steps"])):
        x = W - X0 - (len(sc["steps"]) - i) * 34
        d.ellipse([x, TOP + 100, x + 16, TOP + 116], fill=C["accent"] if i <= step else C["border"])


def draw_stat(d, xy, stat):
    """Big number. '->' or the arrow character is drawn as a shape (Fraunces has no arrow glyph)."""
    x, y = xy
    parts = re.split(r"\s*(?:->|→)\s*", stat)
    for i, part in enumerate(parts):
        if i:
            cy = y + 150
            arrow(d, (x + 25, cy), (x + 135, cy), C["accent"], 14, 46)
            x += 175
        d.text((x, y), part, font=F["stat"], fill=C["accent"])
        x += d.textlength(part, font=F["stat"]) + 10


def scene_finding(d, spec, sc, prog):
    y = heading(d, sc.get("heading", "What we found"))
    draw_stat(d, (X0 - 8, y), sc["stat"])
    y += 260
    y = text_block(d, (X0, y), sc["caption"], F["body"], C["ink"], CW, 1.32) + 40
    lines = sc.get("lines", [])
    if lines:
        lh = 50
        h = lh * len(lines) + 50
        d.rounded_rectangle([X0, y, W - X0, y + h], 18, fill=C["term"], outline=C["border"], width=2)
        for i, ln in enumerate(lines):
            d.text((X0 + 30, y + 25 + i * lh), ln, font=F["mono"], fill=C["term_ink"])


def scene_outro(d, spec, sc, prog):
    y = 470
    d.text((X0, y), f"DAY {int(spec['day']):03d} / 100", font=F["monob"], fill=C["accent"])
    y = text_block(d, (X0, y + 80), sc.get("heading", "Full write-up on Zenn (Japanese)"), F["h"], C["ink"], CW, 1.15) + 60
    for k, v in [("Source", spec["source_url"]), ("License", spec["license"]),
                 ("Code & logs", "github.com/Matsushima-A-830/ai-100days")]:
        d.text((X0, y), k.upper(), font=F["small"], fill=C["faint"])
        y = text_block(d, (X0, y + 42), v, F["mono"], C["ink"], CW, 1.3) + 36


SCENES = {"title": scene_title, "overview": scene_overview, "finding": scene_finding, "outro": scene_outro}


def render_frame(spec, segs, i_seg, t, total, cap_text) -> Image.Image:
    seg = segs[i_seg]
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)
    prog = (t - seg.start) / seg.length if seg.length else 1
    if seg.scene["type"] == "architecture":
        scene_architecture(d, spec, seg.scene, prog, seg.step)
    else:
        SCENES[seg.scene["type"]](d, spec, seg.scene, prog)
    # fade in at the first segment of each scene
    first = i_seg == 0 or segs[i_seg - 1].scene is not seg.scene
    if first and t - seg.start < FADE:
        a = 1 - (t - seg.start) / FADE
        img = Image.blend(img, Image.new("RGB", (W, H), C["bg"]), a)
        d = ImageDraw.Draw(img)
    chrome(img, d, spec, t, total)
    caption(d, cap_text)
    return img


def frame_state(segs, t):
    i = max(k for k, s in enumerate(segs) if s.start <= t + 1e-9)
    seg = segs[i]
    cap = next((c for a, b, c in seg.captions if a <= t < b), "")
    return i, cap


def ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", type=Path)
    ap.add_argument("--no-tts", action="store_true", help="silent video, timing estimated from word count")
    ap.add_argument("--check", action="store_true", help="validate and print timing only")
    ap.add_argument("--stills", type=Path, help="write one PNG per segment to this dir and exit")
    ap.add_argument("--out", type=Path, help="output mp4 (default: next to the spec)")
    args = ap.parse_args()

    try:
        spec = load_spec(args.spec)
    except SpecError as e:
        sys.exit(f"spec error: {e}")
    segs = build_segments(spec)
    tmp = Path(tempfile.mkdtemp(prefix="ai100video-"))
    tts = not (args.no_tts or args.check or args.stills)
    synth(segs, tmp, tts)
    total = segs[-1].start + segs[-1].length
    words = sum(len(s.narration.split()) for s in segs)
    for s in segs:
        print(f"  {s.start:5.1f}s  {s.scene['type']:<12} {s.length:4.1f}s  {s.narration[:60]}")
    print(f"total {total:.1f}s, {words} words ({'measured' if tts else 'estimated'})")
    if not MIN_TOTAL <= total <= MAX_TOTAL:
        msg = f"total {total:.1f}s is outside {MIN_TOTAL:.0f}-{MAX_TOTAL:.0f}s: adjust narration length"
        if tts:
            sys.exit(msg)
        print("WARNING: " + msg)
    if args.check:
        return

    if args.stills:
        args.stills.mkdir(parents=True, exist_ok=True)
        for i, s in enumerate(segs):
            t = s.start + s.length * 0.7
            render_frame(spec, segs, i, t, total, frame_state(segs, t)[1]).save(args.stills / f"seg{i:02d}.png")
        print(f"stills -> {args.stills}")
        return

    out = args.out or args.spec.with_suffix(".mp4")
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if tts:
        wav = tmp / "narration.wav"
        concat_audio(segs, wav)
        cmd += ["-i", str(wav), "-c:a", "aac", "-b:a", "96k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "28", "-tune", "stillimage",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{total:.2f}", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    last_key, last_bytes = None, None
    for f in range(int(math.ceil(total * FPS))):
        t = f / FPS
        i, cap = frame_state(segs, t)
        seg = segs[i]
        fading = (i == 0 or segs[i - 1].scene is not seg.scene) and t - seg.start < FADE
        prog = (t - seg.start) / seg.length
        key = (i, cap, round(t, 2) if fading else None, int(prog * 20) if seg.scene["type"] == "overview" else 0,
               int(t * 2))  # progress bar moves every 0.5s
        if key != last_key:
            last_bytes = render_frame(spec, segs, i, t, total, cap).tobytes()
            last_key = key
        proc.stdin.write(last_bytes)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    if tts:
        write_srt(segs, out.with_suffix(".srt"))
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
