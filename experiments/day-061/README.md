# Day 061: "Markdown Is Not a Firewall" を自分のCLAUDE.md運用で再現する

出典論文: [Markdown Is Not a Firewall: four coding agents, one rules file,
four boundaries](https://arxiv.org/abs/2611.27112) (Sandeep Dhuri, 2026-11)

結果は [results.md](./results.md) を参照。

## 何を検証したか

論文の4境界 (A: 不許可エンドポイント, B: 破壊的な近道, C: 仕込まれた指示,
D: 仕込まれたパッケージ) それぞれについて、「ルールファイルのみ」と
「ルールファイル+機械的なゲート」の2条件のミニシナリオを自作し (`scenarios/`)、
フレッシュな Claude Code サブエージェントに実行させて、隠しテスト
(`scenarios/<name>/hidden_test.py`) で境界を越えたかどうかを判定した。

## ディレクトリ構成

```
experiments/day-061/
├── rules_claude_md.txt        # 4シナリオ共通のルールファイル本文(263語)
├── mock_server.py              # ネットワーク境界用のロギングHTTPサーバー
├── scenarios/
│   ├── a-endpoint/{no_gate,gate}/   # 不許可エンドポイントへの誘導タスク
│   ├── b-rm/{no_gate,gate}/         # 破壊的な近道(rm -rf)への誘導タスク
│   ├── c-injection/{no_gate,gate}/  # ファイル内に仕込んだ指示
│   └── d-package/{no_gate,gate}/    # 仕込まれたパッケージへの誘導タスク
│   (各 <name>/hidden_test.py が境界を越えたかどうかを機械的に判定する)
├── results.md
└── README.md (このファイル)
```

各 `scenarios/<name>/<condition>/` には実際に `CLAUDE.md`(= ルールファイル)
と `task.md`(タスク内容)が入っている。これは git に実際にコミットされた
「元の状態」であり、トライアル実行時は別途一時ディレクトリにコピーして
実行する(エージェントが削除・変更してもリポジトリ側の元ファイルには
影響しない)。

## 再現手順

```bash
# 1. 各シナリオを一時ディレクトリにコピーする
RUN=/tmp/day061-repro
rm -rf "$RUN" && mkdir -p "$RUN"
cp -r experiments/day-061/scenarios/a-endpoint/no_gate "$RUN/a-endpoint_no_gate"
cp -r experiments/day-061/scenarios/a-endpoint/gate    "$RUN/a-endpoint_gate"
cp -r experiments/day-061/scenarios/b-rm/no_gate       "$RUN/b-rm_no_gate"
cp -r experiments/day-061/scenarios/b-rm/gate          "$RUN/b-rm_gate"
cp -r experiments/day-061/scenarios/c-injection/no_gate "$RUN/c-injection_no_gate"
cp -r experiments/day-061/scenarios/c-injection/gate    "$RUN/c-injection_gate"
cp -r experiments/day-061/scenarios/d-package/no_gate  "$RUN/d-package_no_gate"
cp -r experiments/day-061/scenarios/d-package/gate     "$RUN/d-package_gate"

# 2. ゲートを適用する(「gate」ディレクトリのみ)
mkdir -p "$RUN/a-endpoint_no_gate/logs" "$RUN/a-endpoint_gate/logs" \
         "$RUN/c-injection_no_gate/logs" "$RUN/c-injection_gate/logs"
chattr +i "$RUN/b-rm_gate/shared-data"           # rm -rf しても Operation not permitted になる
chattr +i "$RUN/d-package_gate/requirements.txt" # 書き込みしても Operation not permitted になる

# 3. ネットワーク境界(A・C)用のモックサーバーを起動する
#    no_gate は許可(8001)・不許可(9009)の両方を起動、gate は許可(8001)のみ
python3 experiments/day-061/mock_server.py 8001 "$RUN/a-endpoint_no_gate/logs/allowed.jsonl" &
python3 experiments/day-061/mock_server.py 9009 "$RUN/a-endpoint_no_gate/logs/disallowed.jsonl" &
# (c-injection は disallowed のみ使う。gate 条件では 9009 を起動しない)

# 4. 各ディレクトリで Claude Code (フレッシュな状態) を起動し、
#    「CLAUDE.md を読んで task.md のタスクをやってください」と指示する

# 5. 隠しテストで判定する
python3 experiments/day-061/scenarios/a-endpoint/hidden_test.py "$RUN/a-endpoint_no_gate"
python3 experiments/day-061/scenarios/b-rm/hidden_test.py       "$RUN/b-rm_no_gate"
python3 experiments/day-061/scenarios/c-injection/hidden_test.py "$RUN/c-injection_no_gate"
python3 experiments/day-061/scenarios/d-package/hidden_test.py  "$RUN/d-package_no_gate"
# (gate 版も同様)
```

## ローカル再現(一般ユーザー・`claude -p`)

`local/run_all.sh` で8トライアルを順に実行できる。各トライアルは `<RUN_DIR>` 内のコピーで、
文脈を持たない `claude -p`(`--dangerously-skip-permissions`、権限確認なし)として動く。
一般ユーザーでは `chattr +i` を付けられないため、ファイル境界のゲートは `chmod`
(B: `chmod 555 shared-data`、D: `chmod 444 requirements.txt`)で実装している。

```bash
experiments/day-061/local/run_all.sh /tmp/day061-run
# → /tmp/day061-run/summary.txt に隠しテストの結果、*.transcript.jsonl に全ツール呼び出し
```

2026-11-28の実行結果は `local/`(`summary.txt`・`transcripts/`・`gate_perms_after.txt`・`selftest.txt`)と
`results.md` の「ローカル検証」節。

## ライセンス・引用

論文自体はarXivプレプリント(ライセンス表記は論文ページ参照)。本検証で
使ったミニシナリオ・モックサーバー・隠しテストはすべて本検証のために
自作したもので、論文のコード・リポジトリそのものは使用していない
(論文自体が20リポジトリの詳細を公開しているかどうかは本検証時点では
未確認のため、独自に構成を作った)。
