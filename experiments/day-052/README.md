# Day 052: Weight-Space Programming Doesn't Need Transformers

出典: ["Weight-Space Programming Doesn't Need Transformers"](https://huggingface.co/papers/2611.22055)
(arXiv 2611.22055, Hyunjong Ok & Jaeho Lee, POSTECH)。
公開コード: https://github.com/effl-lab/Weight-Space-Programming (MIT License)。

## この論文の主張

勾配降下法を一切使わず、LLMに他モデルの重み(パラメータ)を直接「手で書かせる」
Weight-Space Programming (WSP) という手法。3つのフロンティアLLM(Claude Opus 5.5・GPT-6.1 Sol・
GPT-6 Astra)にARCの4択科学問題10例だけを見せ、サンドボックス内で重みを書かせたところ、
設計を自由にすると3モデルとも「書いた事実の疎なテーブルを、固定の検索手順で読む」構造に
行き着き、最大54.4%のテスト精度(chance=25%)を達成した。

## 今回のスコープ

公開リポジトリの `harness.run` は、Linux上のbubblewrap (`bwrap`) サンドボックス内で
Claude Code CLIを「writer」として直接起動し、OAuthアクセストークンをそのサンドボックス用の
`CLAUDE_CONFIG_DIR` にコピーして使う設計になっている。

このRoutine実行環境でも `bwrap` 自体は動作した(`apt-get install bubblewrap` 後、
`bwrap --ro-bind / / ...` のユーザー名前空間サンドボックスが成功した)。しかし、
`harness.run` がサンドボックスに渡すために必要な「このセッション自身のClaude Code
OAuth認証情報ファイル(`.credentials.json`)を探して読み取る」操作は、このセッションの
auto-mode権限分類器によって `[Unauthorized Access]` として拒否された。これは個別の
コマンドが使えなかったという話ではなく、認証情報を別プロセス用にコピーするという
操作自体がこの実行環境のセキュリティポリシーでブロックされているということなので、
回避を試みず、別の方法で検証した(詳細は `results.md` 参照)。

採った方法: `harness.run` が本来「writer」役としてサブプロセスのClaude Code CLIに
やらせる作業 ―― `prompts/free-arc_gen1.md` のタスク文をそのまま読み、ARC科学問題用の
モデル(`vocab.txt` / `build.py` / `arch.py` / `NOTES.md`)を一から手で書く ―― を、
筆者(Claude Code、このセッション自身)が直接担当した。見せられた10問以外のARCデータは
使わず、一般的な理科知識だけから約150個の短い事実文を書き下ろし、勾配降下なしの
連想記憶型アーキテクチャ(sparse table + 固定の検索手順、`arch.py`は論文のルール通り
`if`/`while`等の分岐を一切含まない固定テンソルプログラム)として実装した。

採点は本物のリポジトリのコード(`wsp.free_model.run()`、同じ`bwrap`隔離実行)と
本物のARCデータセット(`allenai/ai2_arc`、Hugging Face Hubから取得)で行った。
つまり「モデルを書く」工程だけが筆者自身の手作業に置き換わっており、
「書いたモデルを隔離実行・採点する」工程は論文公開コードそのものを実際に動かしている。

## 再現手順

```bash
git clone https://github.com/effl-lab/Weight-Space-Programming.git
cd Weight-Space-Programming
python3 -m venv .venv-wsp
.venv-wsp/bin/pip install -r requirements.txt

# ARCデータセット(allenai/ai2_arc)をHugging Face Hubから取得
HF_HOME=/path/to/hf .venv-wsp/bin/huggingface-cli download allenai/ai2_arc --repo-type dataset

# オフライン単体テスト(CPU)
WSP_DATA_ROOT=/path/to/wsp_data HF_HOME=/path/to/hf HF_HUB_OFFLINE=1 \
  .venv-wsp/bin/python -m pytest tests -q

# 手書きモデル(本リポジトリの experiments/day-052/model/ をコピー)を
# 本物のARC validation/testで採点
cp -r /path/to/ai-100days/experiments/day-052/model ./my_model
HF_HOME=/path/to/hf HF_HUB_OFFLINE=1 .venv-wsp/bin/python - <<'PY'
from wsp import arc, free_model
from pathlib import Path
val = arc.load("validation"); test = arc.load("test")
logits, size, problems = free_model.run(
    Path("my_model"), {"validation": val[:2], "test": test[:2]},
    isolate=True, encoder=free_model.encode_of("free-arc"))
print(problems)
print("validation", free_model.accuracy(logits["validation"], val[2]))
print("test", free_model.accuracy(logits["test"], test[2]))
PY
```

実際の実行ログ・数値は `results.md` を参照。手で書いたモデルの実体は `model/` に置いた
(`vocab.txt` / `build.py` / `arch.py` / `NOTES.md`、論文公開コードの `models/<writer>/<run>/`
と同じ構成)。

## ローカル検証が必要な部分(任意)

今回スコープ外とした「`harness.run`そのもの(Claude Code CLIをbubblewrap内でサブプロセスとして
起動するnested-sandbox実行)」を試す場合は、ログイン済みのClaude Code CLIプロファイルを
持つローカルPCで以下を実行する(有料APIキーは不要、ログイン済みClaude Codeのみ必要):

```bash
export WSP_DATA_ROOT=/path/to/wsp_data HF_HOME=/path/to/hf WSP_VENV=/path/to/.venv-wsp
export WSP_CLAUDE_BIN=$(which claude)
export WSP_CLAUDE_PROFILES=a=$HOME/.claude   # ログイン済みのClaude Code設定ディレクトリ
.venv-wsp/bin/python -m harness.run --arch free-arc --data-access blind --rep 0 \
    --writer opus --profile a
```
