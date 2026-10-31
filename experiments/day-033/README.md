# Day 033: Broken on Arrival — Ollama公式タグの「機能しない」量子化を自分のデータ再集計で確かめる

## 出典

- 論文: Aditi Patodiya, "Broken on Arrival: Non-Functional Quantized LLM Artifacts
  in Public Model Registries and How to Catch Them", arXiv:2609.05881
  https://arxiv.org/abs/2609.05881
- コード・監査データセット: https://github.com/aditi-p31/quantcheck (v3.4,
  commit `129b6c46994143855d5bb1a7b2de0cf79aabcfc0`)
  - コード: MIT License
  - 監査データセット(JSON/JSONLのトップレベルファイル群): CC BY 4.0
- 関連issue: https://github.com/ollama/ollama/issues/18252 (phi3.5の欠陥主張が
  2026-09-10付で撤回された経緯)

## 今回やったこと/やらなかったこと(正直な範囲)

**やったこと**: `quantcheck` リポジトリをクローンし、著者が実際に実行して公開している
生の評価ログ(`rerun-2026-10/serial/census_smoke_serial.jsonl`,
`census_full164_serial.jsonl`、および `results/transcripts/*.jsonl` の生成テキスト)を
自分で書いたスクリプトで読み込み、タグごとのHumanEval+通過数を**独自に再集計**し、
論文中の統計(Wilson 95%信頼区間)も自分で再計算して一致を確認した。

**やらなかったこと**: Ollamaを自分でインストールして`ollama pull`で実際に
モデルを取得・推論することは、本Routineの実行環境のネットワークポリシーにより
`ollama.com` / `registry.ollama.ai` への接続がプロキシに拒否されたため実行できなかった
(`github.com`・`pypi.org`・`huggingface.co`は到達可能だったが、Ollamaのモデルレジストリは
到達不可だった)。したがって「自分でOllamaを動かしてq2_Kタグの生成を確認した」とは書かない。
あくまで**著者が公開した生ログを自分で集計・検算した**という範囲の検証である。

## 手順(今回実際に実行したこと)

1. `add_repo`でread-only access取得後、
   `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/aditi-p31/quantcheck`
2. `scripts/extract_progression.py` / `scripts/extract_qwen3b_progression.py` を書き、
   `rerun-2026-10/serial/census_smoke_serial.jsonl`(15タスクのスモーク screen)と
   `census_full164_serial.jsonl`(164タスクのフル実行、7つの疑惑タグのみ)から、
   `qwen2.5-coder:3b-instruct` / `llama3.2:1b-instruct` / `phi3.5:3.8b-mini-instruct` の
   各量子化レベルのHumanEval+通過数を抜き出した。
3. `scripts/show_transcript.py` で `results/transcripts/qwen2.5-coder_3b-instruct-q2_K.full164.jsonl`
   (機能しないとされるタグ)と `...-q4_K_M.jsonl`(健全なタグ)の、同じHumanEval+タスクへの
   実際の生成テキストを取り出して比較した。
4. Wilson 95%信頼区間を自分でPythonで実装し、7/305と3/35について論文の数字(1.1–4.7%、3.0–22.4%)
   と一致するか検算した。
5. ライセンス(LICENSE, README.mdの`## License`節)を確認した。

## 再現手順

```bash
# 1. quantcheckをクローン(公開リポジトリ、認証不要)
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/aditi-p31/quantcheck /tmp/quantcheck

# 2. 量子化レベルごとの通過数を再集計する(本リポジトリに同梱のスクリプト)
python3 -I experiments/day-033/scripts/extract_qwen3b_progression.py /tmp/quantcheck
python3 -I experiments/day-033/scripts/extract_progression.py /tmp/quantcheck "llama3.2:1b-instruct"
python3 -I experiments/day-033/scripts/extract_progression.py /tmp/quantcheck "phi3.5:3.8b-mini-instruct"

# 3. 生成テキストの比較(機能しないタグ vs 健全なタグ、同じタスク)
python3 -I experiments/day-033/scripts/show_transcript.py \
  /tmp/quantcheck/results/transcripts/qwen2.5-coder_3b-instruct-q2_K.full164.jsonl HumanEval/3
python3 -I experiments/day-033/scripts/show_transcript.py \
  /tmp/quantcheck/results/transcripts/qwen2.5-coder_3b-instruct-q4_K_M.jsonl HumanEval/3
```

### ローカル検証(実施済み、2026-10-31)

人間(matsu)のローカルPC(WSL2、Ollama v0.35.1)で`ollama pull`・実際の推論による再現を実施した。
`qwen2.5-coder:3b-instruct-q2_K`/`-q4_K_M`の両タグをpullし、`harness/audit.py`と同じ
プロンプト形式・パラメータで`HumanEval/3`に対して推論させたところ、q2_Kはquantcheckの
生ログと同種の"program"繰り返しに崩壊し、q4_K_Mは正しいコードを一発で生成した。
論文・quantcheckが報告した崖現象を、独立した環境・実際のOllama推論で再現できた。
詳細な実行ログは`results.md`の「6. ローカル検証」節を参照。
