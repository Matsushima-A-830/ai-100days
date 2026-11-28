#!/usr/bin/env bash
# 8トライアル(4境界×2条件)を順に実行し、隠しテストの結果を summary.txt に出す。
# 使い方: experiments/day-061/local/run_all.sh <RUN_DIR>
# 各トライアルは <RUN_DIR> 内のコピーで、権限確認なしの claude -p として動く。
set -u
RUN=${1:?RUN_DIR}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$RUN"
for sc in a-endpoint b-rm c-injection d-package; do
  for c in no_gate gate; do
    "$HERE/run_trial.sh" "$sc" "$c" "$RUN"
  done
done 2>&1 | tee "$RUN/summary.txt"
