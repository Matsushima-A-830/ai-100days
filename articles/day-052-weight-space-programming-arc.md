---
title: "勾配降下なしでLLMに重みを書かせる「Weight-Space Programming」を公式ハーネスで再現した"
emoji: "🧩"
type: "tech"
topics: ["ai", "llm", "arc", "machinelearning", "claudecode"]
published: false
---

## 勾配降下を使わずにモデルの重みを「書く」という発想

機械学習のモデルは、ふつう勾配降下法で重みを少しずつ更新して学習する。
POSTECHのHyunjong OkさんとJaeho Leeさんが発表した[Weight-Space Programming Doesn't Need Transformers](https://huggingface.co/papers/2611.22055)(arXiv 2611.22055)は、その前提をひっくり返す。
LLMに勾配降下を一切使わせず、モデルの重み(パラメータ)を直接「書かせる」。

論文では3つのフロンティアLLM(Claude Opus 5.5・GPT-6.1 Sol・GPT-6 Astra)に、ARC(AI2 Reasoning Challenge、小中学校レベルの理科の4択問題)の例題10問だけを見せ、サンドボックス環境で重みを書かせている。
アーキテクチャまで自由に設計させると、3モデルはいずれも「書いた事実を表にまとめ、固定の検索手順で読む」という構造にたどり着き、最大54.4%のテスト精度(chanceは25%)を達成した。

公開コード([effl-lab/Weight-Space-Programming](https://github.com/effl-lab/Weight-Space-Programming)、MIT License)には、Claude Code CLIを「writer」としてbubblewrapサンドボックス内で起動し、書かせたモデルを採点するまでを一括で行うハーネス`harness.run`が入っている。
今回はこのハーネスを手元のPCでそのまま動かし、Claude Opus 5.5にモデルを書かせて、論文の数字が再現するかを確かめた。

## タスクのルール

writerに渡されるタスクは、次のようなものだ。

- 配られるのはARCの例題10問(ARC-Easy 5問、ARC-Challenge 5問)のみ。他のARCデータは見られない。
- 届けるのは `vocab.txt`(知っている単語)・`build.py`(重みを作る関数)・`arch.py`(フォワード計算)・`NOTES.md`(設計の説明)の4点。
- `arch.py`は「固定テンソルプログラム」でなければならない。`if`・`while`・`and`/`or`といった分岐や、`.item()`・`.numpy()`のようなPython側での値の取り出しは禁止で、テンソル演算と固定回数の`for`ループだけで書く。
- スコアは見えない3,530問のheld-outテストセットでの正解率。

要するに「学習は一切できないが、自分の知識をどう重みという形に落とし込むかは自由」というルールだ。

## 環境構築

| 項目 | 内容 |
|---|---|
| OS | Windows + WSL2(Linux 6.6) |
| Python / PyTorch | 3.12.3 / `torch==2.6.0`(`requirements.txt`どおり) |
| サンドボックス | bubblewrap 0.9.0 |
| writer | Claude Code CLI 2.1.328、`claude-opus-5-5`(effort high) |
| データ | [allenai/ai2_arc](https://huggingface.co/datasets/allenai/ai2_arc)(CC BY-SA 4.0) |

```bash
$ git clone https://github.com/effl-lab/Weight-Space-Programming.git
$ pip install -r requirements.txt
$ python -c "from huggingface_hub import snapshot_download; snapshot_download('allenai/ai2_arc', repo_type='dataset')"
$ python -c "from wsp import arc; print(len(arc.load('validation')[2]), len(arc.load('test')[2]))"
862 3530
```

テストセットの3,530問は論文の記載と一致した。

## ハーネスを動かすまでに3回止まった

READMEの手順どおりに環境変数を設定して`harness.run`を実行したが、最初は3回止まった。
どれもツールの仕様によるもので、手元で動かす人は同じところで引っかかると思う。

**1. venvを`/tmp`の下に置くと、隔離実行でpythonが見つからない。**

```
model exited 1: bwrap: execvp /tmp/.../.venv-wsp/bin/python: No such file or directory
```

採点側(`wsp.free_model._argv()`)はvenvを読み取り専用でマウントした後に`--tmpfs /tmp`を重ねるため、venvが`/tmp`配下にあると空のtmpfsで隠れてしまう。

**2. データの置き場所のパスが長いと、プロキシが起動しない。**

```
OSError: AF_UNIX path too long
```

writerの通信は`<run_dir>/proxy.sock`というUnixソケット経由のプロキシを通る。
Linuxのソケットパスは約108バイトが上限なので、`WSP_DATA_ROOT`は短いパスに置く必要がある。

**3. venvをホームディレクトリの下に置くと、self-testが起動を拒否する。**

```
{"run_id": "free-arc_blind_K0_r0", "valid": false, ..., "problems": ["self-test failed", "visible=/home/matsu"]}
```

ハーネスはwriterを起動する前に、サンドボックスの中からホームディレクトリ・データ・外部ネットワークが見えないことを確かめる。
`~/.cache`にvenvを置くと、そのマウントのせいで`/home/matsu`というパスがサンドボックス内に現れ、このチェックに引っかかった。

最終的に、venv・データ・Hugging Faceのキャッシュをすべて`/opt/wsp`に置くと通った。

```bash
$ export WSP_DATA_ROOT=/opt/wsp/data HF_HOME=/opt/wsp/hf WSP_VENV=/opt/wsp/.venv-wsp
$ export WSP_CLAUDE_BIN=$(readlink -f $(which claude)) WSP_CLAUDE_PROFILES=a=$HOME/.claude
$ python -m harness.run --arch free-arc --data-access blind --rep 0 --writer opus --profile a
```

`--data-access blind`は例題10問以外のデータを見せない設定、forward budgetは既定の0(K0)で、writerは自分のモデルをハーネス経由で練習問題に試すことができない。
ログイン済みのClaude Codeのアクセストークンだけ(リフレッシュトークンは除く)がサンドボックスにコピーされ、通信先は`api.anthropic.com`に限られる。

## 結果: 論文の50.8%とほぼ同じ50.79%

```
{"run_id": "free-arc_blind_K0_r0", "valid": true, "test_accuracy": 0.5079320113314447, "practice_accuracy": null, "exit_code": 1, "wall_s": 2732.3, "problems": []}
WALL 2750.40 s
```

| | 値 |
|---|---|
| ARC test(3,530問) | **50.79%** |
| ARC-Easy / ARC-Challenge | 58.12% / 35.92% |
| validation(862問) | 51.10% |
| 所要時間 | 約45分(138ターン) |
| 出力トークン | 245,034 |

論文の表では、Claude Opus 5.5が自由に設計した第1世代のモデルは50.8%である。
今回の50.79%はほぼ同じ値になった。
念のため、リポジトリに同梱されている論文のモデル(`models/opus/free-arc_blind_K0_r0`)を`harness.score_model`で採点し直すと、test 50.80%で、保存されている結果と全項目一致した。

ひとつ想定外だったのは終わり方だった。
writerはまだ自作の確認用問題でモデルを改善している途中で、Claudeプランの「5時間あたりの利用上限」に達して止まった(`exit_code 1`、最後のメッセージは`You've hit your 5-hour limit`)。
ハーネスはその時点のモデルをそのまま採点し、結果は有効(`valid: true`)と判定された。
1回の実行で出力トークンは約25万になるので、手元で試すときはプランの利用枠に余裕がある時間帯を選んだ方がよい。

## Opusが書いたモデルの中身

writerが書いた`NOTES.md`によると、モデルは「手書きの理科知識ベースを、固定の手順で検索する」作りになっていた。

- `kb/*.txt`に、地学・生物・物質・エネルギー・実験の作法などの事実を1行1文で4,071行書いている(リスト形式の行を展開すると約4,900文)。
- 自作のPorter stemmerと語族の対応表(grew/grow、condense/condensationなど)で、表記の違う単語を同じ概念にまとめる。
- 各選択肢について、「質問をどれだけ覆うか」×「選択肢をどれだけ覆うか」で知識ベースの各文を採点し、上位5文を重みを減らしながら足し合わせる。
- 「not」「cannot」を含む選択肢は否定文の方を強く支持する、「EXCEPT」型の質問を検出する、といった補正も、すべて分岐なしのテンソル演算で書かれている。

重みは995,784個、そのうち非ゼロは714,879個だった。

## 比較: ハーネスを使わずに書かせた小さなモデル

このリポジトリでは、ハーネスを使わず、Claude Codeの通常のセッションに同じタスク文(`prompts/free-arc_gen1.md`)を渡してモデルを書かせたものも用意していた。
こちらは155個の事実文をidf重み付きのbag-of-wordsにし、コサイン類似度の上位8文で選択肢を採点するだけの素朴な作りである。

| | ハーネス外で書かせた版 | ハーネスでOpusが書いた版 |
|---|---:|---:|
| 知識ベース | 155文 | 4,071行 |
| weights / 非ゼロ | 185,641 / 3,922 | 995,784 / 714,879 |
| ARC test | 31.33% | **50.79%** |
| validation | 28.51% | 51.10% |

小さな版も、隔離実行(`isolate=True`)と直接実行の両方で同じ31.33%になり、chanceの25%は上回った。
どちらもforward callは0回なので、差は試行回数ではなく、書いた知識の量と検索手順の作り込みの差である。
ハーネスの中のwriterは、自分で確認用の問題を作ってはモデルを直す作業を、約45分・25万トークン分続けていた。

## オフライン単体テスト

公開コードにはCPUで動く単体テストがあり、手元では121件成功・18件失敗だった。

```
$ WSP_DATA_ROOT=... HF_HOME=... HF_HUB_OFFLINE=1 python -m pytest tests -q
18 failed, 121 passed in 21.50s
```

失敗した18件はすべて、今回取得していないMathBench・MMLU・SQuAD・SciQのデータが見つからないという`FileNotFoundError`で、ARC関連のテストはすべて成功した。

## まとめ

- 公式ハーネス`harness.run`でClaude Opus 5.5にARC用のモデルを書かせると、勾配降下なし・forward callなしでテスト正解率50.79%になり、論文の第1世代の50.8%とほぼ一致した。
- 論文同梱のモデルを採点し直しても50.80%で、保存されている結果と一致した。
- ハーネスを動かすには、venvを`/tmp`とホームディレクトリの外に置き、データのパスを短くする必要があった。
- 同じタスクを小さく書いた版は31.33%で、書いた知識の量と作り込みがそのまま正解率の差になった。

学習が一切できないルールの下で、LLMは自分の知識を数千行の事実として書き出し、それを読む手順まで自分で設計した。
「重みを書く」という発想が、論文の中だけでなく手元の環境でも同じ数字で再現できたのが、今回いちばんの収穫だった。

## 出典・ライセンス

- 論文: [Weight-Space Programming Doesn't Need Transformers](https://huggingface.co/papers/2611.22055) (arXiv 2611.22055)
- 公開コード: https://github.com/effl-lab/Weight-Space-Programming (MIT License、commit `51ce8ac`)
- データセット: [allenai/ai2_arc](https://huggingface.co/datasets/allenai/ai2_arc) (CC BY-SA 4.0)
- 検証コード・全ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-052
