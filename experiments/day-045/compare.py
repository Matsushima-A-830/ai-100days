"""Greedy-generate from the base and mask-applied Qwen2.5-0.5B on a few GSM8K-style prompts.

Raw-text prompting (no chat template), matching how the released grpo/qwen2.5-0.5b-simplerl-zoo
mask was trained (train with --skip_chat_template per the paper's scripts/evaluate_grpo.sh).
"""

import argparse
import time

import torch
import transformers

PROMPTS = [
    (
        "gsm8k_1",
        "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. "
        "How many clips did Natalia sell altogether in April and May?\n"
        "Let's think step by step and then give the final numeric answer after '#### '.\n",
        72,
    ),
    (
        "gsm8k_2",
        "A robe takes 2 bolts of blue fiber and half that much white fiber. "
        "How many bolts in total does it take?\n"
        "Let's think step by step and then give the final numeric answer after '#### '.\n",
        3,
    ),
    (
        "gsm8k_3",
        "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. "
        "How much did she earn?\n"
        "Let's think step by step and then give the final numeric answer after '#### '.\n",
        10,
    ),
]


def generate(model_path: str, max_new_tokens: int = 256) -> dict:
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_path)
    model = transformers.AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16)
    model.eval()
    results = {}
    for name, prompt, _ in PROMPTS:
        ids = tokenizer(prompt, return_tensors="pt")
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(
                **ids, max_new_tokens=max_new_tokens, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        dt = time.time() - t0
        text = tokenizer.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
        results[name] = {"text": text, "seconds": dt}
        print(f"=== {name} ({dt:.1f}s) ===")
        print(text)
        print()
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    args = parser.parse_args()
    generate(args.model_path, args.max_new_tokens)


if __name__ == "__main__":
    main()
