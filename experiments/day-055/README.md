# Day 055: SenseNova-Loop-9B のループ回数を1〜4回に変えて比べる

出典: https://huggingface.co/sensenova/SenseNova-Loop-9B (Apache-2.0)
AWQ版: https://huggingface.co/sensenova/SenseNova-Loop-9B-AWQ (Apache-2.0)
Code: https://github.com/OpenSenseNova/SenseNova-Loop (Apache-2.0)

層4〜27を同じ重みで2回実行する「ループ型デコーダ」の公式AWQ 4bit版を、ローカルPC(RTX 5060 Ti 16GB)で動かした。
推論時のループ回数だけを1・2・3・4回に切り替え、perplexity・3桁×2桁の掛け算20問・文章題・コード生成・生成速度を比べた。
結果は `results.md`。

Day 055はクラウドの実装Routineが実行されなかったため、検証から成果物の作成までをローカルPCで行った。

## 再現手順

```bash
git clone https://github.com/OpenSenseNova/SenseNova-Loop
uv venv -p 3.12 .venv
uv pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu130
uv pip install -e ./SenseNova-Loop
# gptqmodel(AWQ読み込みに必要)と flash-linear-attention。torch / transformers が上がらないよう固定する
uv pip install --index-url https://download.pytorch.org/whl/cu130 --extra-index-url https://pypi.org/simple \
  --index-strategy unsafe-best-match -c constraints.txt gptqmodel flash-linear-attention
hf download sensenova/SenseNova-Loop-9B-AWQ --local-dir models/SenseNova-Loop-9B-AWQ --exclude "assets/*"

# 埋め込み・lm_headの逆量子化の並び順を探し、2ループで試す
python run_loops.py models/SenseNova-Loop-9B-AWQ out_ordertest.json --order-search --loops 2
# ループ1〜4回の比較(RTX 5060 Ti で約20分)
python run_loops.py models/SenseNova-Loop-9B-AWQ out_loops.json --emb-order seq --head-order awq --loops 1,2,3,4
python regrade.py out_loops.json
```

## ファイル

- `awq_fix.py` — AWQ版の埋め込み層・lm_head(4bitで保存されているがTransformers + gptqmodelでは読み込まれない)を逆量子化して差し込む。
- `run_loops.py` — 一度読み込んだモデルの実行計画を `execution_plan()` で作り直し、ループ回数ごとにperplexity・プロンプト・掛け算を測る。
- `regrade.py` — 掛け算を回答の最後の数値で採点し直す。
- `constraints.txt` — torch / torchvision / transformers の固定。
- `out_ordertest.json` / `out_loops.json` — 実行結果(全出力テキスト・時間・採点)。
- `logs/01`〜`05` — 各実行のログ(進捗バーは除去)。
