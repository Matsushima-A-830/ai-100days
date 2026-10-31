"""quantcheckリポジトリ同梱の生成テキスト(transcript)から、指定タスクの出力を表示するだけのスクリプト。
使い方: python3 -I show_transcript.py <jsonl_path> <task_id> [max_chars]
"""
import json
import sys
from pathlib import Path


def main() -> None:
    path = Path(sys.argv[1])
    task_id = sys.argv[2]
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    with path.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("task_id") == task_id:
                print(rec["solution"][:max_chars])
                return
    print("not found", file=sys.stderr)


if __name__ == "__main__":
    main()
