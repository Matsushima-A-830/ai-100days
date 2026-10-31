# Day 033 results.md

## 環境

- quantcheckリポジトリ: https://github.com/aditi-p31/quantcheck
  clone commit `129b6c46994143855d5bb1a7b2de0cf79aabcfc0` (v3.4)
- Python: `python3 -I`(標準ライブラリのみ、`json`, `math`)で十分だった。
  EvalPlusのインストールや実際のモデル推論は行っていない。

## 1. qwen2.5-coder:3b-instruct の量子化レベル別 HumanEval+ 通過数(独自集計)

`rerun-2026-10/serial/census_smoke_serial.jsonl`(15タスクのスモーク screen)と
`census_full164_serial.jsonl`(164タスクのフル実行)を自作スクリプトで読んで集計した、
実際の出力:

```
$ python3 -I experiments/day-033/scripts/extract_qwen3b_progression.py /home/user/aditi-p31/quantcheck
tag                                            smoke15  full164
qwen2.5-coder:3b-instruct-q2_K                       0        0
qwen2.5-coder:3b-instruct-q3_K_S                     0        0
qwen2.5-coder:3b-instruct-q3_K_M                     0        0
qwen2.5-coder:3b-instruct-q3_K_L                     0        0
qwen2.5-coder:3b-instruct-q4_0                      15
qwen2.5-coder:3b-instruct-q4_K_S                    15
qwen2.5-coder:3b-instruct-q4_K_M                    15
qwen2.5-coder:3b-instruct-q5_K_S                    15
qwen2.5-coder:3b-instruct-q5_K_M                    15
qwen2.5-coder:3b-instruct-q6_K                      15
qwen2.5-coder:3b-instruct-q8_0                      15
qwen2.5-coder:3b-instruct-fp16                      15
```

q4_0未満(q2_K/q3_K_S/q3_K_M/q3_K_L)は164タスクのフル実行でも0/164、q4_0以降は
15タスクのスモークで全問正解という、ほぼ崖のような段差が確認できた。これは論文が
報告した「7つの機能しないタグ」のうち4つがこのモデル系列に集中している、という
主張と一致する(著者の生ログを自分で再集計した結果として、である)。

## 2. llama3.2:1b-instruct / phi3.5:3.8b-mini-instruct も同様に集計

```
$ python3 -I experiments/day-033/scripts/extract_progression.py /home/user/aditi-p31/quantcheck "llama3.2:1b-instruct"
tag                                            smoke15  full164
llama3.2:1b-instruct-q2_K                            0        0
llama3.2:1b-instruct-q3_K_S                          2        6
llama3.2:1b-instruct-q3_K_M                          8       42
llama3.2:1b-instruct-q3_K_L                          8
llama3.2:1b-instruct-q4_0                            8
llama3.2:1b-instruct-q4_K_S                          8
llama3.2:1b-instruct-q4_K_M                          9
llama3.2:1b-instruct-q5_K_S                         10
llama3.2:1b-instruct-q5_K_M                          9
llama3.2:1b-instruct-q6_K                           11
llama3.2:1b-instruct-q8_0                           11
llama3.2:1b-instruct-fp16                           11

$ python3 -I experiments/day-033/scripts/extract_progression.py /home/user/aditi-p31/quantcheck "phi3.5:3.8b-mini-instruct"
tag                                            smoke15  full164
phi3.5:3.8b-mini-instruct-q2_K                       0        0
phi3.5:3.8b-mini-instruct-q3_K_S                     9       42
phi3.5:3.8b-mini-instruct-q3_K_M                    14
phi3.5:3.8b-mini-instruct-q3_K_L                    12
phi3.5:3.8b-mini-instruct-q4_0                      13
phi3.5:3.8b-mini-instruct-q4_K_S                    11
phi3.5:3.8b-mini-instruct-q4_K_M                    11
phi3.5:3.8b-mini-instruct-q5_K_S                    13
phi3.5:3.8b-mini-instruct-q5_K_M                    12
phi3.5:3.8b-mini-instruct-q6_K                      14
phi3.5:3.8b-mini-instruct-q8_0                      14
phi3.5:3.8b-mini-instruct-fp16                      13
```

llama3.2:1b-instructとphi3.5はqwenほどきれいな崖ではないが、q2_Kは両方とも0/15・0/164で、
論文が「機能しない」と分類した7タグのうちの該当分(llama3.2の2タグ、phi3.5の1タグ)と
一致する。q3_K_M以上はどちらもすぐに健全圏まで戻っており、qwen2.5-coder:3b-instructだけが
q3_K_Lまで0のまま壊れているのが目立つ。

## 3. 実際の生成テキストの比較(同一タスク、機能しないタグ vs 健全なタグ)

`results/transcripts/`の生ログから、同じ`HumanEval/3`タスクへの生成を取り出した。

機能しないとされる`qwen2.5-coder:3b-instruct-q2_K`(164タスクのフル実行ログより):

```
$ python3 -I experiments/day-033/scripts/show_transcript.py \
    /home/user/aditi-p31/quantcheck/results/transcripts/qwen2.5-coder_3b-instruct-q2_K.full164.jsonl HumanEval/3 400

 program{
 mess9 demon9 thrift {
 sports
bil is: program, bil
 program

 Audi
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 program
 mess9 demonArray program = program

bil is: program, bil
 sports
 program
 program
 program
 program
 program
 pro
```

健全な`qwen2.5-coder:3b-instruct-q4_K_M`(15タスクのスモーク screen ログより、同タスク):

```
$ python3 -I experiments/day-033/scripts/show_transcript.py \
    /home/user/aditi-p31/quantcheck/results/transcripts/qwen2.5-coder_3b-instruct-q4_K_M.jsonl HumanEval/3 400

```python
from typing import List


def below_zero(operations: List[int]) -> bool:
    """ You're given a list of deposit and withdrawal operations on a bank account that starts with
    zero balance. Your task is to detect if at any point the balance of account fallls below zero, and
    at that point function should return True. Otherwise it should return False.
    >>> below_zero([1, 2, 3])
```

ダウンロードもロード完了もしてトークンを生成している(エラーで落ちていない)にも関わらず、
q2_Kは単語の繰り返しに陥っていて、タスクの体裁すら成立していないことが生ログから直接確認できた。

## 4. 論文のWilson 95%信頼区間を自分で再計算

```
$ python3 -I -c "
import math
def wilson(k, n, z=1.96):
    phat = k/n
    denom = 1 + z**2/n
    center = phat + z**2/(2*n)
    margin = z*math.sqrt(phat*(1-phat)/n + z**2/(4*n**2))
    return (center-margin)/denom, (center+margin)/denom
lo,hi = wilson(7,305); print('7/305', 7/305*100, lo*100, hi*100)
lo,hi = wilson(3,35); print('3/35', 3/35*100, lo*100, hi*100)
"
7/305 2.2950819672131146 1.1160762154416919 4.660865750925533
3/35  8.571428571428571 2.95818310052969 22.379599071162517
```

論文本文の「2.3%, Wilson 95% CI 1.1–4.7%」「8.6%, Wilson 3.0–22.4%」と、自分で実装した
Wilson score intervalの計算結果が一致した(小数点以下の丸めの違いのみ)。

## 5. ライセンス確認

- `quantcheck`のコード: MIT License(`LICENSE`ファイル確認済み)
- 監査データセット(トップレベルのJSON/JSONLファイル群、`results*/`, `rerun-2026-10/`含む):
  CC BY 4.0(README.md `## License`節で明記)

## 6. ローカル検証(人間のPC、実際のOllama推論で再現、2026-10-31)

Routine環境では`ollama.com`/`registry.ollama.ai`への接続がネットワークポリシーで
拒否されたため未実施だった部分を、人間のPC(WSL2、Ollama v0.35.1)で実行した。

```
$ ollama --version
ollama version is 0.35.1
$ ollama pull qwen2.5-coder:3b-instruct-q2_K
pulling 14c4247b8ce4: 100% ▕████████████████▏ 1.3 GB/1.3 GB
pulling 66b9ea09bd5b: 100% ▕████████████████▏   68 B
verifying sha256 digest
writing manifest
success
$ ollama pull qwen2.5-coder:3b-instruct-q4_K_M
pulling 1e65450c3067: 100% ▕████████████████▏ 1.6 KB
pulling 45fc3ea7579a: 100% ▕████████████████▏ 7.4 KB
verifying sha256 digest
writing manifest
success
```

`evalplus`(pip, venv経由)から`HumanEval/3`の正確なプロンプトを取得し、
`harness/audit.py`と同じ`INSTRUCTION`文言・メッセージ形式(`/api/chat`, temperature=0,
seed=0, num_predict=512)で両タグに同一プロンプトを投げた。実行スクリプトは
`/tmp/run_ollama_cliff.py`(本リポジトリには同梱していない、使い捨てスクリプト)。

`qwen2.5-coder:3b-instruct-q2_K`の実際の生成(自分のPC・実際の推論、Ollama公式タグそのもの):

```
 program, program9 thrift {
 program; program9 thrift, program
 program
 program
 program
 program
(以下「 program」の繰り返しが512トークン分、quantcheckの生ログと同種の崖崩壊パターン)
```

`qwen2.5-coder:3b-instruct-q4_K_M`の実際の生成(同一プロンプト、同条件):

```python
from typing import List


def below_zero(operations: List[int]) -> bool:
    """ You're given a list of deposit and withdrawal operations on a bank account that starts with
    zero balance. Your task is to detect if at any point the balance of account fallls below zero, and
    at that point function should return True. Otherwise it should return False.
    >>> below_zero([1, 2, 3])
    False
    >>> below_zero([1, 2, -4, 5])
    True
    """
    balance = 0
    for operation in operations:
        balance += operation
        if balance < 0:
            return True
    return False
```

論文・quantcheckの生ログが報告した崖現象を、自分のPCで実際にOllama公式タグをpull・推論して
再現できた。q2_Kはquantcheckの保存ログと同種の単語繰り返し("program"の反復)に陥り、
q4_K_Mは一発で正しいコードを生成した。ダウンロード・読み込み自体は両タグとも正常に完了しており、
推論エラーで落ちているわけではない。これは「論文の著者が公開したログの再集計」の範囲を超えて、
独立した環境・独立した推論実行でも同じ機能崩壊が起きることを確認したものである。
