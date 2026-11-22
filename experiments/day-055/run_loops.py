"""Compare SenseNova-Loop-9B-AWQ with the looped block executed 1-4 times.

The checkpoint is trained/served with loop_settings.eval_count=2 (layers 4-27 run twice).
Here the same loaded weights are reused and only the execution plan is switched,
using the repository's own execution_plan() function.

Usage: python run_loops.py MODEL_DIR OUT_JSON [--emb-order awq|seq] [--head-order awq|seq]
"""
import argparse
import copy
import json
import random
import time

import torch

import awq_fix
from sensenova_loop.inference import LoopInference
from sensenova_loop.models.modeling_sensenova_loop import execution_plan

REFERENCE_TEXTS = {
    "en": (
        "The water cycle describes how water moves through the environment. Water evaporates "
        "from oceans, lakes and rivers, rises into the atmosphere as vapour, cools and condenses "
        "into clouds, and eventually falls back to the surface as rain or snow. Some of that water "
        "flows over the ground into streams, while some soaks into the soil and becomes groundwater."
    ),
    "ja": (
        "水の循環とは、水が地球上でどのように移動するかを表したものである。"
        "海や湖、川の水は蒸発して水蒸気となり、大気中で冷やされて雲になる。"
        "やがて雨や雪として地表に戻り、その一部は川に流れ込み、一部は土にしみ込んで地下水になる。"
    ),
}

PROMPTS = [
    ("mul_example", "What is 13 times 7? Reply with the number only."),
    ("bat_ball", "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. "
                 "How much does the ball cost? Answer in one or two sentences."),
    ("widgets", "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take "
                "100 machines to make 100 widgets? Answer in one or two sentences."),
    ("sally", "Sally has 3 brothers. Each of her brothers has 2 sisters. How many sisters does "
              "Sally have? Answer in one or two sentences."),
    ("ja_capital", "日本の首都はどこですか?一文で答えてください。"),
    ("fib_code", "Write a short Python function fib(n) that returns the n-th Fibonacci number "
                 "iteratively. Output only the code."),
]


def mul_problems(n=20, seed=0):
    rng = random.Random(seed)
    return [(rng.randint(100, 999), rng.randint(10, 99)) for _ in range(n)]


def set_loops(model, count):
    text = model.model.language_model
    raw = model.config.to_dict()
    raw["loop_settings"] = dict(raw["loop_settings"], counts=[count], eval_count=count)
    plan = execution_plan(raw)
    text._loop_plan = plan
    text._loop_cache_config = copy.deepcopy(text.config)
    text._loop_cache_config.num_hidden_layers = len(plan)
    text._loop_cache_config.layer_types = [text.config.layer_types[i] for i in plan]
    return len(plan)


@torch.inference_mode()
def nll(engine, text):
    ids = engine.processor.tokenizer(text, return_tensors="pt").input_ids.to(engine.device)
    out = engine.model(input_ids=ids, use_cache=False)
    logits = out.logits[0, :-1].float()
    loss = torch.nn.functional.cross_entropy(logits, ids[0, 1:])
    return loss.item(), ids.shape[1]


def ask(engine, prompt, max_new_tokens):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    r = engine.generate_result([{"role": "user", "content": prompt}], max_new_tokens=max_new_tokens)
    torch.cuda.synchronize()
    dt = time.perf_counter() - t0
    return {"text": r.text, "output_tokens": r.output_tokens, "seconds": round(dt, 3),
            "tokens_per_second": round(r.output_tokens / dt, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("out")
    ap.add_argument("--emb-order", default="awq")
    ap.add_argument("--head-order", default="awq")
    ap.add_argument("--loops", default="1,2,3,4")
    ap.add_argument("--order-search", action="store_true")
    args = ap.parse_args()

    t0 = time.perf_counter()
    engine = LoopInference(args.model, local_files_only=True)
    print(f"loaded in {time.perf_counter() - t0:.1f}s", flush=True)
    results = {"model": args.model, "loops": {}}

    if args.order_search:
        set_loops(engine.model, 2)
        search = {}
        for eo in ("awq", "seq"):
            for ho in ("awq", "seq"):
                awq_fix.apply(engine.model, args.model, eo, ho)
                loss, n = nll(engine, REFERENCE_TEXTS["en"])
                search[f"emb={eo},head={ho}"] = loss
                print(f"order emb={eo} head={ho}: en NLL={loss:.4f} ({n} tokens)", flush=True)
        results["order_search"] = search
        best = min(search, key=search.get)
        args.emb_order, args.head_order = (p.split("=")[1] for p in best.split(","))
        print("chosen:", best, flush=True)

    awq_fix.apply(engine.model, args.model, args.emb_order, args.head_order)
    results["emb_order"], results["head_order"] = args.emb_order, args.head_order
    torch.cuda.reset_peak_memory_stats()

    problems = mul_problems()
    for count in [int(c) for c in args.loops.split(",")]:
        layers = set_loops(engine.model, count)
        print(f"\n===== loops={count} (decoder layer executions per token: {layers}) =====", flush=True)
        entry = {"layer_executions": layers, "nll": {}, "prompts": {}, "mul": []}
        for lang, text in REFERENCE_TEXTS.items():
            loss, n = nll(engine, text)
            entry["nll"][lang] = {"loss": round(loss, 4), "ppl": round(float(torch.tensor(loss).exp()), 3), "tokens": n}
            print(f"[nll {lang}] loss={loss:.4f} ppl={entry['nll'][lang]['ppl']}", flush=True)
        for key, prompt in PROMPTS:
            r = ask(engine, prompt, 200)
            entry["prompts"][key] = r
            print(f"[{key}] {r['output_tokens']} tok, {r['tokens_per_second']} tok/s\n{r['text']}\n", flush=True)
        correct = 0
        for a, b in problems:
            r = ask(engine, f"What is {a} times {b}? Reply with the number only.", 16)
            digits = "".join(ch for ch in r["text"] if ch.isdigit())
            ok = digits == str(a * b)
            correct += ok
            entry["mul"].append({"q": f"{a}x{b}", "answer": a * b, "text": r["text"], "ok": ok})
        entry["mul_correct"] = correct
        print(f"[mul] {correct}/{len(problems)} correct", flush=True)
        results["loops"][str(count)] = entry

    results["peak_gpu_memory_gib"] = round(torch.cuda.max_memory_allocated() / 1024**3, 2)
    print(f"\npeak GPU memory allocated: {results['peak_gpu_memory_gib']} GiB", flush=True)
    json.dump(results, open(args.out, "w"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
