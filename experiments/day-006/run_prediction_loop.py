"""Day 006: CTWM(tau)の縮小版オンライン次状態予測ループ。

外部LLM API(本家が前提とするOpenAI互換エンドポイント)を使わず、
「次の遷移を予測する」部分だけをClaude Code自身が手動ループで代替するための
オーケストレータ。各ステップで:

  1. このスクリプトが「現在の状態」と「メモリから取得したヒント」だけを
     書いたプロンプトファイルを出力して停止する。
  2. Claude Code(人間ではなく実装Routine自身)がそのファイルだけを読み、
     正解(実際の次状態)を見ずに予測を書き戻す。
  3. このスクリプトが正解と照合してスコアを記録し、実際の遷移をメモリに
     書き込んでから次のステップのプロンプトを出す。

これを tau=0.0 (baseline, 均等配分) と tau=1.0 (CTWM推奨値) の2つの
メモリ設定それぞれについて繰り返す。グラフ生成・ランダムウォーク・CTWMメモリ本体は
vendor/ 配下にコピーした本家コード(MIT License, 無改変)をそのまま使う。
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent / "vendor"))

from synthetic_graph_world import build_graph, build_state_payloads, run_random_walk  # noqa: E402
from backends_ctwm import B8_CTWM  # noqa: E402

HERE = Path(__file__).parent
LOGS = HERE / "logs"
STATE_PATH = HERE / "state.pkl"

N_NODES = 24
GRAPH_TYPE = "scale_free"
SEED = 42
OBS_STEPS = 24
PRED_STEPS = 10
N_STEPS = OBS_STEPS + PRED_STEPS + 1  # len(states); len(transitions) == N_STEPS - 1

MEM_CONFIGS = {
    "baseline": dict(tau=0.0, core_pct=0.30, core_slots=3, tail_slots=999, capacity=200, seed=SEED, seed_offset=8),
    "ctwm": dict(tau=1.0, core_pct=0.30, core_slots=3, tail_slots=2, capacity=200, seed=SEED, seed_offset=8),
}
LABELS = ["baseline", "ctwm"]


@dataclass
class RunState:
    states: List[int]
    transitions: List[Any]
    tail_freq_threshold: int
    memories: Dict[str, Any]
    cursor: Dict[str, int]  # label -> next prediction step index (global index into states/transitions)
    pending: Optional[Dict[str, Any]]  # {"label":..., "step":...} awaiting an answer
    logs: Dict[str, List[Dict[str, Any]]]
    done_labels: List[str]
    obs_state_freq: Dict[int, int]


def build_action_menu(payloads, current_state: int) -> str:
    actions = payloads[current_state].actions
    ents = payloads[current_state].entities[:3]
    cons = payloads[current_state].constraints[:2]
    lines = [
        f"現在の状態: v_{current_state:03d}",
        f"この状態のペイロード: entities={ents}, constraints={cons}",
        f"利用可能な行動({len(actions)}個): {actions}",
        "注意: どの行動がどの状態へ繋がるかはここには示されません。",
        "下の『メモリから取得したヒント』に v_{:03d} からの遷移が含まれていれば、".format(current_state),
        "それを根拠に次の状態を予測してください。手がかりが無ければ unknown と答えてください。",
    ]
    return "\n".join(lines)


def make_prompt_text(label: str, step: int, payloads, current_state: int, memory) -> str:
    menu = build_action_menu(payloads, current_state)
    ctx = memory.context_string(current_state)
    return (
        f"[config={label} step={step}]\n\n"
        f"{menu}\n\n"
        f"メモリから取得したヒント(core/tail):\n{ctx}\n\n"
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

    # persist payloads/graph alongside (not part of dataclass to keep pickle simple)
    rs_bundle = {"rs": rs, "g": g, "payloads": payloads}
    with open(STATE_PATH, "wb") as f:
        pickle.dump(rs_bundle, f)

    LOGS.mkdir(parents=True, exist_ok=True)
    meta = {
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
    }
    with open(HERE / "run_meta.json", "w", encoding="utf-8") as f:
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
        rs.pending = {"label": label, "step": step, "prompt_path": str(prompt_path),
                      "context_chars": len(mem.context_string(current_state)),
                      "prompt_chars": len(prompt_text)}
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
        avg_context_chars = sum(e["context_chars"] for e in entries) / n if n else 0.0
        summary[label] = {
            "n_pred_steps": n,
            "n_correct": n_correct,
            "accuracy": n_correct / n if n else None,
            "n_tail_steps": n_tail,
            "n_tail_correct": n_tail_correct,
            "tail_accuracy": (n_tail_correct / n_tail) if n_tail else None,
            "avg_prompt_chars": avg_prompt_chars,
            "avg_context_chars": avg_context_chars,
        }
    with open(HERE / "prediction_results.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "per_step": rs.logs}, f, ensure_ascii=False, indent=2)
    print("[DONE] wrote prediction_results.json")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cmd_init(_args):
    if STATE_PATH.exists():
        STATE_PATH.unlink()
    rs = init_run()
    print(f"[init] built graph n_nodes={N_NODES} edges={rs.memories['baseline'].write_events} obs_steps={OBS_STEPS}")
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
    if pred_raw in ("unknown", "?", "na", "n/a"):
        predicted = None
    else:
        predicted = int(pred_raw)
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
        "context_chars": pending["context_chars"],
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
