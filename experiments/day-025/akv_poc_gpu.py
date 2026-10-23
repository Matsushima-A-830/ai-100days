"""
Day 025: AKV (Cache Engineering for Agents) の縮小版概念実証 — ローカルGPU版。

論文: https://huggingface.co/papers/2610.28577 / https://github.com/thu-nics/AKV

akv_poc.py(CPU版、HuggingFaceTB/SmolLM2-135M-Instruct固定)の派生版。
人間のローカルPC(GPU搭載)で、より大きい・算術タスクを実際に解けるモデルで
再検証するために以下を追加した(CPU版の挙動・結果には一切影響しない)。

  - AKV_MODEL 環境変数でモデル名を差し替え可能(未指定時はCPU版と同じSmolLM2-135M)
  - CUDAが使えれば自動でGPU+bfloat16、無ければCPU+float32にフォールバック
  - AKV_ATTN 環境変数でattention実装を指定可能(既定は"eager"。SDPA/flash系の
    実装はメモリレイアウトに応じて浮動小数の丸め方が変わり、恒等変換のはずの
    delta=0回転ですら損失値がわずかに変化することを確認したため、再現性を
    優先してeagerを既定にした。詳細はresults.md参照)
  - AKV_OUT 環境変数で出力JSONのパスを指定可能

論文はA800 80GB x8・GPT-OSS-120B等の大規模サービング実験だが、CPU版同様、
"drop"(不要な履歴のKVキャッシュエントリを捨てる)と
"repos"(残したキーの位置エンコーディング=RoPEの回転角を付け替える)という
2つのアイデアの核だけを自作実装し、下記4方式を比較する。

  1. full      : 履歴を一切圧縮しない(ベースライン、キャッシュは伸び続ける)
  2. summarize : 既存のcontext engineering。古いtool応答をテキストで要約し、
                 要約+残りの履歴をゼロから再prefillする(キャッシュは全部作り直し)
  3. drop      : 古いtool応答に対応するKVキャッシュのエントリをテキストを書き換えずに
                 直接切り落とす(位置エンコーディングの補正はしない、naive drop)
  4. drop+repos: dropに加えて、残ったキーのRoPE回転角を「詰めた後の連番位置」に
                 付け替える(AKVのrepos操作に相当)

RoPEは2次元回転の合成則 R(a)R(b) = R(a+b) が成り立つので、位置pで既に回転済みの
キャッシュ済みキーに対し、追加のデルタ回転 R(delta) をそのまま乗せれば
位置 p+delta に相当するキーに変換できる(逆回転して作り直す必要がない)。
これが repos を「再計算ゼロの直接操作」として実装できる理由。

測定するもの:
  - 各ターン処理後のKVキャッシュに実際に乗っている トークン数
  - 各ターンの処理にかかった壁時計時間(prefillの再計算コストを含む)
  - 最終応答に対するモデルの損失 (cross entropy / perplexity) -- 品質の代理指標
    naive dropでrepos無しだと位置情報が歪んで損失が悪化するか、
    reposを当てると full/summarize に近い損失に戻るかを見る
"""

import copy
import json
import os
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = os.environ.get("AKV_MODEL", "HuggingFaceTB/SmolLM2-135M-Instruct")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.bfloat16 if DEVICE == "cuda" else torch.float32
OUT_PATH = os.environ.get("AKV_OUT", "experiments/day-025/results_raw.json")

torch.manual_seed(0)


def load():
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=DTYPE, attn_implementation=os.environ.get("AKV_ATTN", "eager"))
    model.to(DEVICE)
    model.eval()
    return tok, model


def build_transcript(tok):
    """
    エージェントが複数回ツールを呼ぶ会話を模したテキストブロックを作る。
    各ブロックはトークナイズして境界を記録し、あとでKVキャッシュを
    ブロック単位でスライスできるようにする。
    """
    system = (
        "<|im_start|>system\n"
        "You are a careful assistant that uses tools to answer questions about a "
        "small inventory database.<|im_end|>\n"
    )
    user_task = (
        "<|im_start|>user\n"
        "I'm auditing our warehouse. Walk through each shelf and tell me the final "
        "total count of working thermal printers at the end.<|im_end|>\n"
    )
    # 「古くなる」ツール応答ブロック。最終質問には直接関係しないノイズを多めに持つ。
    tool_blocks = [
        (
            "<|im_start|>assistant\ncalling tool: scan_shelf(shelf='A1')<|im_end|>\n"
            "<|im_start|>tool\nShelf A1 scan complete. Found 14 cardboard boxes, 3 pallets, "
            "2 empty bins, 1 broken label printer (unit #A1-07, out of service since last "
            "quarter), and 4 thermal printers in working condition. Ambient temperature "
            "18.2C, humidity 41%. No safety issues logged.<|im_end|>\n"
        ),
        (
            "<|im_start|>assistant\ncalling tool: scan_shelf(shelf='A2')<|im_end|>\n"
            "<|im_start|>tool\nShelf A2 scan complete. Found 9 cardboard boxes, 1 pallet, "
            "0 empty bins, 2 thermal printers in working condition, 1 thermal printer "
            "flagged as defective (paper jam sensor fault, unit #A2-13). Ambient temperature "
            "18.4C, humidity 40%. Forklift access path clear.<|im_end|>\n"
        ),
        (
            "<|im_start|>assistant\ncalling tool: scan_shelf(shelf='B1')<|im_end|>\n"
            "<|im_start|>tool\nShelf B1 scan complete. Found 20 cardboard boxes, 5 pallets, "
            "3 empty bins, 5 thermal printers in working condition, no defects logged. "
            "Ambient temperature 19.0C, humidity 39%. Routine shelf, nothing notable.<|im_end|>\n"
        ),
        (
            "<|im_start|>assistant\ncalling tool: scan_shelf(shelf='B2')<|im_end|>\n"
            "<|im_start|>tool\nShelf B2 scan complete. Found 6 cardboard boxes, 2 pallets, "
            "1 empty bin, 3 thermal printers in working condition, 1 thermal printer "
            "retired for parts (unit #B2-02). Ambient temperature 19.1C, humidity 38%.<|im_end|>\n"
        ),
    ]
    final_user = (
        "<|im_start|>user\nBased on all shelves scanned so far, what is the final total "
        "count of working thermal printers?<|im_end|>\n<|im_start|>assistant\n"
    )
    final_answer = "The final total count of working thermal printers is 14."
    # working printers: A1=4, A2=2, B1=5, B2=3 -> 合計14台(正解テキストとして固定する)

    def ids(text):
        return tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(DEVICE)

    blocks = {
        "system": ids(system),
        "user_task": ids(user_task),
        "tool_blocks": [ids(b) for b in tool_blocks],
        "final_user": ids(final_user),
        "final_answer": ids(final_answer),
    }
    return blocks


@torch.no_grad()
def prefill(model, input_ids, past_key_values=None, cache_position=None):
    out = model(
        input_ids=input_ids,
        past_key_values=past_key_values,
        use_cache=True,
        cache_position=cache_position,
    )
    return out.past_key_values


def cache_len(past_key_values):
    return past_key_values.get_seq_length()


def slice_out_span(past_key_values, start, end):
    """
    past_key_values から [start, end) のトークン位置に対応するKV列を直接切り落とす
    (= AKVの"drop"操作。テキストは一切書き換えず、キャッシュのテンソルだけを操作する)。
    transformers>=5のDynamicCacheは各層が .keys/.values テンソルを直接持つので、
    それぞれスライスして置き換える(in-place代入。レイヤーのリストは共有せず複製する)。
    """
    for layer in past_key_values.layers:
        layer.keys = torch.cat([layer.keys[:, :, :start, :], layer.keys[:, :, end:, :]], dim=2)
        layer.values = torch.cat([layer.values[:, :, :start, :], layer.values[:, :, end:, :]], dim=2)
    return past_key_values


def rotate_keys_by_delta(model, past_key_values, delta, start, end):
    """
    past_key_values 内、トークン位置 [start, end) に対応するキーだけに
    追加のRoPE回転 delta を適用する(= AKVの"repos"操作)。
    値(value)側は回転の対象外(RoPEはQ/Kのみに効く)。

    RoPEは2次元回転の合成則 R(a)R(b)=R(a+b) が成り立つため、位置pで既に回転済みの
    キャッシュ済みキーに追加のデルタ回転R(delta)をそのまま乗せれば、
    逆回転して作り直さずに位置p+deltaのキーへ変換できる。
    """
    from transformers.models.llama.modeling_llama import rotate_half

    rotary_emb = model.model.rotary_emb
    device = past_key_values.layers[0].keys.device
    span_len = end - start
    if span_len <= 0:
        return past_key_values
    delta_pos = torch.full((1, span_len), float(delta), device=device)
    dummy = torch.zeros(1, span_len, model.config.hidden_size, device=device, dtype=next(model.parameters()).dtype)
    cos, sin = rotary_emb(dummy, delta_pos)
    # cos/sin: (1, span_len, head_dim) -> (1, 1, span_len, head_dim) でヘッド次元にbroadcast
    cos = cos.unsqueeze(1)
    sin = sin.unsqueeze(1)

    for layer in past_key_values.layers:
        k = layer.keys
        k_span = k[:, :, start:end, :]
        k_rot = k_span * cos + rotate_half(k_span) * sin
        layer.keys = torch.cat([k[:, :, :start, :], k_rot, k[:, :, end:, :]], dim=2)
    return past_key_values


@torch.no_grad()
def answer_loss(model, past_key_values, cache_position_start, final_user_ids, answer_ids):
    """
    past_key_values のあとに final_user ブロック + 正解テキストを続けて流し、
    正解テキスト部分のcross entropy損失(token平均)を測る = 品質の代理指標。
    """
    full_new = torch.cat([final_user_ids, answer_ids], dim=1)
    n_new = full_new.shape[1]
    cache_position = torch.arange(
        cache_position_start, cache_position_start + n_new, device=full_new.device
    )
    out = model(
        input_ids=full_new,
        past_key_values=copy.deepcopy(past_key_values),
        use_cache=True,
        cache_position=cache_position,
    )
    logits = out.logits  # (1, n_new, vocab)
    n_answer = answer_ids.shape[1]
    # final_user部分の最後のトークンのロジットが answer[0] を予測する
    shift_logits = logits[:, n_new - n_answer - 1 : n_new - 1, :]
    shift_labels = answer_ids
    loss = torch.nn.functional.cross_entropy(
        shift_logits.reshape(-1, shift_logits.size(-1)), shift_labels.reshape(-1)
    )
    return loss.item()


def run_full(model, blocks):
    t0 = time.perf_counter()
    pkv = prefill(model, blocks["system"], cache_position=torch.arange(0, blocks["system"].shape[1], device=DEVICE))
    pos = blocks["system"].shape[1]
    pkv = prefill(model, blocks["user_task"], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["user_task"].shape[1], device=DEVICE))
    pos += blocks["user_task"].shape[1]
    for tb in blocks["tool_blocks"]:
        pkv = prefill(model, tb, past_key_values=pkv,
                      cache_position=torch.arange(pos, pos + tb.shape[1], device=DEVICE))
        pos += tb.shape[1]
    t1 = time.perf_counter()
    loss = answer_loss(model, pkv, pos, blocks["final_user"], blocks["final_answer"])
    t2 = time.perf_counter()
    return {
        "policy": "full",
        "final_cache_len": cache_len(pkv),
        "prefill_seconds": t1 - t0,
        "management_seconds": 0.0,
        "answer_seconds": t2 - t1,
        "answer_loss": loss,
    }


def run_summarize(model, tok, blocks):
    """
    古くなった最初の2ブロックのtool応答をテキストで要約し、
    system + 要約 + 残り2ブロックをゼロから再prefillする。
    """
    summary_text = (
        "<|im_start|>assistant\n(summary) Shelves A1 and A2 already scanned: "
        "working thermal printers so far = 4 + 2 = 6.<|im_end|>\n"
    )
    summary_ids = tok(summary_text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(DEVICE)

    t0 = time.perf_counter()
    merged = torch.cat(
        [blocks["system"], blocks["user_task"], summary_ids,
         blocks["tool_blocks"][2], blocks["tool_blocks"][3]],
        dim=1,
    )
    pkv = prefill(model, merged, cache_position=torch.arange(0, merged.shape[1], device=DEVICE))
    pos = merged.shape[1]
    t1 = time.perf_counter()
    loss = answer_loss(model, pkv, pos, blocks["final_user"], blocks["final_answer"])
    t2 = time.perf_counter()
    return {
        "policy": "summarize",
        "final_cache_len": cache_len(pkv),
        "prefill_seconds": 0.0,
        "management_seconds": t1 - t0,
        "answer_seconds": t2 - t1,
        "answer_loss": loss,
        "note": "summarizeは「要約テキスト生成+system/user/summary/残りtool応答の全体再prefill」が"
                "そのままmanagement操作になるため、再prefill全体をmanagement_secondsに計上",
    }


def run_drop(model, blocks, apply_repos):
    """
    full と全く同じ順・同じ位置IDで4つのtool_blocksすべてを先にprefillしてから
    (= tool_blocks[2],[3]は「A1・A2がまだ履歴に残っている」前提の絶対位置で
    すでにRoPE回転済みのキーとしてキャッシュされている)、
    あとからA1・A2ブロック分のKVエントリだけを直接切り落とす。

    これにより、残ったtool_blocks[2],[3]のキーは「切り落とし後の詰まった配列上の
    位置」と「キーに焼き込まれた回転=元の絶対位置」が食い違った状態になる
    (naive dropが抱える問題)。drop+reposではこの食い違いを、
    焼き込まれた回転をdropped_n分だけ巻き戻す追加回転で修正する。

    management_seconds として、drop(+repos)操作そのもの(スライス+回転)に
    かかった時間を、その前後のprefill時間と分離して計測する。
    """
    t0 = time.perf_counter()
    pkv = prefill(model, blocks["system"], cache_position=torch.arange(0, blocks["system"].shape[1], device=DEVICE))
    pos = blocks["system"].shape[1]
    pkv = prefill(model, blocks["user_task"], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["user_task"].shape[1], device=DEVICE))
    pos += blocks["user_task"].shape[1]

    drop_start = pos
    pkv = prefill(model, blocks["tool_blocks"][0], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["tool_blocks"][0].shape[1], device=DEVICE))
    pos += blocks["tool_blocks"][0].shape[1]
    pkv = prefill(model, blocks["tool_blocks"][1], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["tool_blocks"][1].shape[1], device=DEVICE))
    pos += blocks["tool_blocks"][1].shape[1]
    drop_end = pos

    pkv = prefill(model, blocks["tool_blocks"][2], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["tool_blocks"][2].shape[1], device=DEVICE))
    pos += blocks["tool_blocks"][2].shape[1]
    pkv = prefill(model, blocks["tool_blocks"][3], past_key_values=pkv,
                  cache_position=torch.arange(pos, pos + blocks["tool_blocks"][3].shape[1], device=DEVICE))
    pos += blocks["tool_blocks"][3].shape[1]
    t1 = time.perf_counter()

    before_drop_len = cache_len(pkv)
    dropped_n = drop_end - drop_start

    t_mgmt0 = time.perf_counter()
    pkv = slice_out_span(pkv, drop_start, drop_end)
    after_drop_len = cache_len(pkv)
    policy_name = "drop"
    if apply_repos:
        # tool_blocks[2],[3]に焼き込まれた回転(元の絶対位置)を dropped_n 分だけ
        # 巻き戻し、「詰めた後の連番位置」に付け替える。
        pkv = rotate_keys_by_delta(model, pkv, delta=-dropped_n, start=drop_start, end=after_drop_len)
        policy_name = "drop+repos"
    t_mgmt1 = time.perf_counter()

    loss = answer_loss(model, pkv, after_drop_len, blocks["final_user"], blocks["final_answer"])
    t2 = time.perf_counter()
    return {
        "policy": policy_name,
        "cache_len_before_drop": before_drop_len,
        "dropped_tokens": dropped_n,
        "final_cache_len": after_drop_len,
        "prefill_seconds": t1 - t0,
        "management_seconds": t_mgmt1 - t_mgmt0,
        "answer_seconds": t2 - t_mgmt1,
        "answer_loss": loss,
    }


N_REPS = 5


def repeat(fn, *args):
    """同じ測定をN_REPS回繰り返し、時間系の値は平均を、lossはそのまま(決定的)残す。"""
    runs = [fn(*args) for _ in range(N_REPS)]
    agg = dict(runs[0])
    for key in ("prefill_seconds", "management_seconds", "answer_seconds"):
        if key in agg:
            agg[key] = sum(r[key] for r in runs) / len(runs)
    agg["n_reps"] = N_REPS
    agg["answer_loss_all_reps"] = [r["answer_loss"] for r in runs]
    return agg


def main():
    tok, model = load()
    blocks = build_transcript(tok)

    results = []
    results.append(repeat(run_full, model, blocks))
    results.append(repeat(run_summarize, model, tok, blocks))
    results.append(repeat(run_drop, model, blocks, False))
    results.append(repeat(run_drop, model, blocks, True))

    print(json.dumps(results, ensure_ascii=False, indent=2))
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
