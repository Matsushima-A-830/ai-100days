"""
akv_poc_gpu.py(GPU版)の4方式それぞれについて、lossだけでなく実際に自由生成
(greedy)させて最終応答がどうなるかを目で見て確認する補助スクリプト。
AKV_MODEL環境変数でモデルを差し替えられる(akv_poc_gpu.py参照)。
結果は experiments/day-025/results.md に手で転記する。
"""

import torch

from akv_poc_gpu import (
    DEVICE,
    DTYPE,
    build_transcript,
    cache_len,
    load,
    prefill,
    rotate_keys_by_delta,
    slice_out_span,
)


@torch.no_grad()
def generate(model, tok, past_key_values, pos, prompt_ids, max_new_tokens=140):
    input_ids = prompt_ids
    cache_position = torch.arange(pos, pos + input_ids.shape[1], device=DEVICE)
    generated = []
    pkv = past_key_values
    for _ in range(max_new_tokens):
        out = model(
            input_ids=input_ids,
            past_key_values=pkv,
            use_cache=True,
            cache_position=cache_position,
        )
        pkv = out.past_key_values
        next_id = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
        generated.append(next_id.item())
        if next_id.item() == tok.eos_token_id:
            break
        pos = cache_position[-1].item() + 1
        input_ids = next_id
        cache_position = torch.arange(pos, pos + 1, device=DEVICE)
    return tok.decode(generated, skip_special_tokens=True)


def build_full_cache(model, blocks):
    pkv = prefill(model, blocks["system"], cache_position=torch.arange(0, blocks["system"].shape[1], device=DEVICE))
    pos = blocks["system"].shape[1]
    pkv = prefill(model, blocks["user_task"], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["user_task"].shape[1], device=DEVICE))
    pos += blocks["user_task"].shape[1]
    drop_start = pos
    for tb in blocks["tool_blocks"][:2]:
        pkv = prefill(model, tb, past_key_values=pkv, cache_position=torch.arange(pos, pos + tb.shape[1], device=DEVICE))
        pos += tb.shape[1]
    drop_end = pos
    for tb in blocks["tool_blocks"][2:]:
        pkv = prefill(model, tb, past_key_values=pkv, cache_position=torch.arange(pos, pos + tb.shape[1], device=DEVICE))
        pos += tb.shape[1]
    return pkv, pos, drop_start, drop_end


def main():
    tok, model = load()
    blocks = build_transcript(tok)

    pkv_full, pos_full, drop_start, drop_end = build_full_cache(model, blocks)
    txt_full = generate(model, tok, pkv_full, pos_full, blocks["final_user"])
    print("=== full ===")
    print(repr(txt_full))

    pkv2, pos2, drop_start2, drop_end2 = build_full_cache(model, blocks)
    dropped_n = drop_end2 - drop_start2
    pkv2 = slice_out_span(pkv2, drop_start2, drop_end2)
    after_len2 = cache_len(pkv2)
    txt_drop = generate(model, tok, pkv2, after_len2, blocks["final_user"])
    print("=== drop (naive, no repos) ===")
    print(repr(txt_drop))

    pkv3, pos3, drop_start3, drop_end3 = build_full_cache(model, blocks)
    dropped_n3 = drop_end3 - drop_start3
    pkv3 = slice_out_span(pkv3, drop_start3, drop_end3)
    after_len3 = cache_len(pkv3)
    pkv3 = rotate_keys_by_delta(model, pkv3, delta=-dropped_n3, start=drop_start3, end=after_len3)
    txt_repos = generate(model, tok, pkv3, after_len3, blocks["final_user"])
    print("=== drop+repos ===")
    print(repr(txt_repos))

    # summarize
    from akv_poc import run_summarize  # noqa: F401 (reuse text-building logic manually below)

    summary_text = (
        "<|im_start|>assistant\n(summary) Shelves A1 and A2 already scanned: "
        "working thermal printers so far = 4 + 2 = 6.<|im_end|>\n"
    )
    summary_ids = tok(summary_text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(DEVICE)
    merged = torch.cat(
        [blocks["system"], blocks["user_task"], summary_ids,
         blocks["tool_blocks"][2], blocks["tool_blocks"][3]],
        dim=1,
    )
    pkv4 = prefill(model, merged, cache_position=torch.arange(0, merged.shape[1], device=DEVICE))
    pos4 = merged.shape[1]
    txt_sum = generate(model, tok, pkv4, pos4, blocks["final_user"])
    print("=== summarize ===")
    print(repr(txt_sum))


if __name__ == "__main__":
    main()
