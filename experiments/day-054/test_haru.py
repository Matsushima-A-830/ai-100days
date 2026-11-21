"""Call the public Haru-4B Gradio Space ("offline duplex demo") and record
real responses + latency for the day-054 verification.

Space: https://huggingface.co/spaces/hugging-apps/haru-4b
API endpoint: "/converse" (api_name set in the Space's app.py)
"""
import json
import time

from gradio_client import Client, handle_file

SPACE = "hugging-apps/haru-4b"
OUT_DIR = "."

def run_case(label, user_audio_url, reference_audio_url, language, persona=""):
    client = Client(SPACE)
    t0 = time.perf_counter()
    result = client.predict(
        user_audio=handle_file(user_audio_url),
        reference_audio=handle_file(reference_audio_url) if reference_audio_url else None,
        language=language,
        persona=persona,
        guidance_scale=1.5,
        temperature=0.7,
        top_k=25,
        seed=-1,
        speak_first=False,
        api_name="/converse",
    )
    elapsed = time.perf_counter() - t0
    reply_audio, transcript = result
    print(f"=== {label} ===")
    print(f"wall-clock request time: {elapsed:.2f}s")
    print(f"reply_audio: {reply_audio}")
    print(f"transcript: {transcript!r}")
    print()
    return {
        "label": label,
        "elapsed_sec": elapsed,
        "reply_audio": reply_audio,
        "transcript": transcript,
    }


if __name__ == "__main__":
    base = f"https://{SPACE.replace('/', '-')}.hf.space/gradio_api/file="
    cases = [
        ("english example (en_seg.wav / en_ref.wav)", "assets/en_seg.wav", "assets/en_ref.wav", "en"),
        ("japanese example (ja_seg.wav / ja_ref.wav)", "assets/ja_seg.wav", "assets/ja_ref.wav", "ja"),
    ]
    results = []
    for label, user_path, ref_path, lang in cases:
        try:
            r = run_case(label, base + user_path, base + ref_path, lang)
            results.append(r)
        except Exception as e:
            print(f"=== {label} FAILED ===")
            print(repr(e))
            results.append({"label": label, "error": repr(e)})
            print()

    with open("raw_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
