"""Day 006 v2: results.md記載の改善案を反映した再実験。

v1(`run_prediction_loop.py`)で判明した2つの問題への対応:

1. v1の予測ルールは `context_string()` が出す短い要約文字列だけを見ていたため、
   頻度情報が見えず「最上位(スコア最高)のエントリ」を機械的に選ぶしかなかった。
   v2では `retrieve_hints()` が返す実際のメモリエントリ(頻度 f を含む)を
   自前で整形してプロンプトに出す。予測ルールも「現在状態をprevとする
   エントリのうち最も頻度の高いnextを予測する」という頻度ベースに変更する。
2. v1はグラフ24ノード・35ステップと小さすぎて、観測されるユニーク状態が
   8個程度にしか増えず、CTWMのtail圧縮効果(プロンプト予算の差)が実測に
   現れなかった。v2ではグラフとステップ数を拡大し、テールが実際に育つ
   状況を作る。

CTWMメモリ本体(vendor/backends_ctwm.py)・合成グラフ世界生成コード
(vendor/synthetic_graph_world.py)はv1と同じく無改変で再利用する。
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent / "vendor"))

from synthetic_graph_world import build_graph, build_state_payloads, run_random_walk  # noqa: E402
from backends_ctwm import B8_CTWM  # noqa: E402

HERE = Path(__file__).parent
LOGS = HERE / "logs_v2"
STATE_PATH = HERE / "state_v2.pkl"

N_NODES = 60
GRAPH_TYPE = "scale_free"
SEED = 42
OBS_STEPS = 45
PRED_STEPS = 15
N_STEPS = OBS_STEPS + PRED_STEPS + 1

MEM_CONFIGS = {
    "baseline": dict(tau=0.0, core_pct=0.30, core_slots=3, tail_slots=999, capacity=300, seed=SEED, seed_offset=8),
    "ctwm": dict(tau=1.0, core_pct=0.30, core_slots=3, tail_slots=2, capacity=300, seed=SEED, seed_offset=8),
}
LABELS = ["baseline", "ctwm"]


@dataclass
class RunState:
    states: List[int]
    transitions: List[Any]
    tail_freq_threshold: int
    memories: Dict[str, Any]
    cursor: Dict[str, int]
    pending: Optional[Dict[str, Any]]
    logs: Dict[str, List[Dict[str, Any]]]
    done_labels: List[str]
    obs_state_freq: Dict[int, int]


def build_action_menu(payloads, current_state: int) -> str:
    actions = payloads[current_state].actions
    ents = payloads[current_state].entities[:3]
    cons = payloads[current_state].constraints[:2]
    return "\n".join([
        f"現在の状態: v_{current_state:03d}",
        f"この状態のペイロード: entities={ents}, constraints={cons}",
        f"利用可能な行動({len(actions)}個): {actions}",
        "注意: どの行動がどの状態へ繋がるかはここには示されません。",
        f"下の『メモリから取得したヒント』に v_{current_state:03d} からの遷移が含まれていれば、",
        "その中で最も頻度(f)の高いnextを予測してください(頻度が同率なら先に書かれている方)。",
        "手がかりが無ければ unknown と答えてください。",
    ])


def annotate_hints(memory, current_state: int) -> str:
    """v1と違い、頻度(f)付きでcore/tailの実際のエントリをそのまま見せる。"""
    core_tids = list(getattr(memory, "_last_core", []) or [])
    tail_tids = list(getattr(memory, "_last_tail", []) or [])

    def fmt(tid: str) -> str:
        e = memory.entries[tid]
        return f"{e['prev']}->{e['action']}->{e['next']} (f={e['f']})"

    core_str = "core: " + ("; ".join(fmt(t) for t in core_tids) if core_tids else "(empty)")
    tail_str = "tail: " + ("; ".join(fmt(t) for t in tail_tids) if tail_tids else "(empty)")
    return core_str + "\n" + tail_str


def make_prompt_text(label: str, step: int, payloads, current_state: int, memory) -> str:
    menu = build_action_menu(payloads, current_state)
    hints = annotate_hints(memory, current_state)
    return (
        f"[config={label} step={step}]\n\n"
        f"{menu}\n\n"
        f"メモリから取得したヒント(core/tail、頻度f付き):\n{hints}\n\n"
        "回答形式: 次の状態のノード番号のみを整数で答えてください(例: 7)。"
        "根拠が無い場合は unknown と答えてください。\n"
    )


def init_run() -> RunState:
    g = build_graph(GRAPH_TYPE, N_NODES, seed=SEED)
    payloads = build_state_payloads(g, seed=SEED)
    states, transitions = run_random_walk(g, payloads, N_STEPS, seed=SEED)

    obs_state_freq: Dict[int, int] = {}
    for s in states[: OBS_STEPS + 1]:
        obs_state_freq[s] = obs_state_freq.get(s, 0) + 1

    memories = {label: B8_CTWM(**cfg) for label, cfg in MEM_CONFIGS.items()}
    for label, mem in memories.items():
        for step in range(OBS_STEPS):
            prev, action, nxt = transitions[step]
            mem.write_transition(prev, action, nxt, step)

    rs = RunState(
        states=states,
        transitions=transitions,
        tail_freq_threshold=1,
        memories=memories,
        cursor={label: OBS_STEPS for label in LABELS},
        pending=None,
        logs={label: [] for label in LABELS},
        done_labels=[],
        obs_state_freq=obs_state_freq,
    )

    rs_bundle = {"rs": rs, "g": g, "payloads": payloads}
    with open(STATE_PATH, "wb") as f:
        pickle.dump(rs_bundle, f)

    LOGS.mkdir(parents=True, exist_ok=True)
    meta = {
        "version": "v2",
        "n_nodes": N_NODES,
        "graph_type": GRAPH_TYPE,
        "seed": SEED,
        "obs_steps": OBS_STEPS,
        "pred_steps": PRED_STEPS,
        "n_steps": N_STEPS,
        "mem_configs": MEM_CONFIGS,
        "graph_edge_count": g.number_of_edges(),
        "obs_unique_states": len(obs_state_freq),
        "obs_state_freq": obs_state_freq,
        "improvements_over_v1": [
            "予測ルールを「最上位1件」から「頻度(f)最大のnext」に変更し、プロンプトにも頻度を明示",
            "グラフ/ステップ数を24ノード・35ステップから60ノード・61ステップに拡大し、テールの成長を狙う",
        ],
    }
    with open(HERE / "run_meta_v2.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    emit_next_prompt(rs_bundle)
    with open(STATE_PATH, "wb") as f:
        pickle.dump(rs_bundle, f)
    return rs


def emit_next_prompt(bundle) -> Optional[Dict[str, Any]]:
    rs: RunState = bundle["rs"]
    payloads = bundle["payloads"]
    for label in LABELS:
        if label in rs.done_labels:
            continue
        step = rs.cursor[label]
        if step >= OBS_STEPS + PRED_STEPS:
            rs.done_labels.append(label)
            continue
        current_state = rs.states[step]
        mem = rs.memories[label]
        mem.retrieve_hints(current_state, step)
        prompt_text = make_prompt_text(label, step, payloads, current_state, mem)
        prompt_path = LOGS / f"{label}_step{step:02d}_prompt.txt"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        rs.pending = {
            "label": label, "step": step, "prompt_path": str(prompt_path),
            "prompt_chars": len(prompt_text),
            "hints_chars": len(annotate_hints(mem, current_state)),
            "n_core_shown": len(getattr(mem, "_last_core", []) or []),
            "n_tail_shown": len(getattr(mem, "_last_tail", []) or []),
        }
        return rs.pending
    rs.pending = None
    finalize(bundle)
    return None


def finalize(bundle) -> None:
    rs: RunState = bundle["rs"]
    summary = {}
    for label in LABELS:
        entries = rs.logs[label]
        n = len(entries)
        n_correct = sum(1 for e in entries if e["correct"])
        tail_entries = [e for e in entries if e["is_tail"]]
        n_tail = len(tail_entries)
        n_tail_correct = sum(1 for e in tail_entries if e["correct"])
        avg_prompt_chars = sum(e["prompt_chars"] for e in entries) / n if n else 0.0
        avg_hints_chars = sum(e["hints_chars"] for e in entries) / n if n else 0.0
        avg_n_tail_shown = sum(e["n_tail_shown"] for e in entries) / n if n else 0.0
        summary[label] = {
            "n_pred_steps": n,
            "n_correct": n_correct,
            "accuracy": n_correct / n if n else None,
            "n_tail_steps": n_tail,
            "n_tail_correct": n_tail_correct,
            "tail_accuracy": (n_tail_correct / n_tail) if n_tail else None,
            "avg_prompt_chars": avg_prompt_chars,
            "avg_hints_chars": avg_hints_chars,
            "avg_n_tail_shown": avg_n_tail_shown,
        }
    with open(HERE / "prediction_results_v2.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "per_step": rs.logs}, f, ensure_ascii=False, indent=2)
    print("[DONE] wrote prediction_results_v2.json")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cmd_init(_args):
    if STATE_PATH.exists():
        STATE_PATH.unlink()
    rs = init_run()
    print(f"[init] built graph n_nodes={N_NODES} obs_steps={OBS_STEPS} pred_steps={PRED_STEPS}")
    print(f"[init] pending: {rs.pending}")
    print(f"Read prompt at: {rs.pending['prompt_path']}")


def cmd_answer(args):
    with open(STATE_PATH, "rb") as f:
        bundle = pickle.load(f)
    rs: RunState = bundle["rs"]
    pending = rs.pending
    if pending is None:
        print("[answer] no pending prediction; run is already finished.")
        return
    if pending["label"] != args.label or pending["step"] != args.step:
        print(f"[answer] mismatch: pending={pending}, got label={args.label} step={args.step}")
        return

    label, step = args.label, args.step
    actual_prev, actual_action, actual_next = rs.transitions[step]
    assert actual_prev == rs.states[step]

    pred_raw = args.prediction.strip().lower()
    predicted = None if pred_raw in ("unknown", "?", "na", "n/a") else int(pred_raw)
    correct = (predicted == actual_next)
    is_tail = rs.obs_state_freq.get(actual_prev, 0) <= rs.tail_freq_threshold

    rs.logs[label].append({
        "step": step,
        "current_state": actual_prev,
        "actual_action": actual_action,
        "actual_next": actual_next,
        "predicted": predicted,
        "correct": correct,
        "is_tail": is_tail,
        "obs_freq_of_current_state": rs.obs_state_freq.get(actual_prev, 0),
        "prompt_chars": pending["prompt_chars"],
        "hints_chars": pending["hints_chars"],
        "n_core_shown": pending["n_core_shown"],
        "n_tail_shown": pending["n_tail_shown"],
    })

    mem = rs.memories[label]
    mem.write_transition(actual_prev, actual_action, actual_next, step)
    rs.cursor[label] = step + 1

    print(f"[answer] label={label} step={step} predicted={predicted} actual={actual_next} "
          f"correct={correct} is_tail={is_tail}")

    nxt = emit_next_prompt(bundle)
    with open(STATE_PATH, "wb") as f:
        pickle.dump(bundle, f)
    if nxt:
        print(f"[next] pending: {nxt}")
        print(f"Read prompt at: {nxt['prompt_path']}")
    else:
        print("[run] all configs finished.")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.set_defaults(func=cmd_init)

    p_answer = sub.add_parser("answer")
    p_answer.add_argument("--label", required=True, choices=LABELS)
    p_answer.add_argument("--step", required=True, type=int)
    p_answer.add_argument("--prediction", required=True)
    p_answer.set_defaults(func=cmd_answer)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
