---
title: "ダウンロードもロードもできるのに0問しか解けない。Ollama公式タグの量子化崖を自分のデータ再集計で確かめた"
emoji: "🧊"
type: "tech"
topics: ["llm", "ollama", "quantization", "evaluation", "arxiv"]
published: false
---

## 要約

- arXiv:2609.05881「Broken on Arrival」という論文が、Ollama公式ライブラリの305タグをHumanEval+で機能検査し、7タグ(`qwen2.5-coder:3b-instruct`のq2_K/q3_K_S/q3_K_M/q3_K_L、`phi3.5:3.8b-mini-instruct-q2_K`、`llama3.2:1b-instruct`のq2_K/q3_K_S)が164問中0〜6問しか解けない「機能しない」状態だったと報告している。
- この論文はv1で「サイレントに壊れたファイル」と診断したが、v3で訂正されている。著者が同じチェックポイントから再ビルドしたところ、ファイル自体はビット単位で一致する正規の(無calibrationの)低bit量子化だった。壊れていたのはファイルではなく、無calibration量子化によって性能が実質ゼロまで崩壊するという現象そのものだった。
- 筆者はこの論文のコード・監査データセット(`aditi-p31/quantcheck`, MIT/CC BY 4.0)をクローンし、著者が公開している生のHumanEval+評価ログを自分のスクリプトで再集計して、この崖と、論文中のWilson信頼区間の数字が自分の再計算でも一致することを確認した。手元のOllamaでq2_K/q4_K_Mを実際にpull・推論させても同じ崖を再現できた。

## きっかけ

Hugging Face Daily Papersの巡回で見つけた一本に、妙に惹かれるタイトルがついていた。
「Broken on Arrival」、着荷時点で壊れている。
Ollamaの公式ライブラリに登録されている量子化モデルタグのうち、ダウンロードもロードもできてトークンも実際に出てくるのに、タスクをほとんど解けないものが混じっている、という調査報告である。
筆者はこれまでOllamaの量子化タグを「サイズが小さければ少し精度が落ちるだけ」くらいに考えて選んでいたので、これは試す価値があると判断した。

## 本題: v1の「壊れたファイル」診断は撤回されている

まず筆者が手を動かす前に確認すべきことがあった。
この論文には複数のバージョンがあり、現在のarXivページで読める最新版(v3)の内容は、初版(v1)とは結論が違う。
v1のタイトルは「Silently Defective LLM Artifacts」、つまり「サイレントに欠陥のあるアーティファクト」であり、問題のタグのGGUFファイル自体が壊れていると報告していた。

v3ではこの診断が訂正されている。
著者はQwen2.5-Coder-3B系・phi3.5系の該当タグを、オリジナルのチェックポイントからllama.cppで自分で再ビルドした。
その結果、Qwen側4タグは434テンソル全てが、phi3.5側は197テンソル全てが(古いllama.cppのテンソル構成に合わせれば)、公式タグのファイルとビット単位で一致した。
つまりファイルは改変も破損もしていない、正規の量子化出力だったということになる。

壊れていたのはファイルではなく、「無calibration(importance matrixを使わない)の低bit量子化によって、特定の小型モデルの性能が実質ゼロまで崩壊する」という現象だった。
importance matrixを使った量子化に切り替えると、同じQwen2.5-Coder-3Bのq2_Kは164問中0問から106〜113問まで回復し、q3_K_Mは76〜89問、q3_K_Lは80〜86問まで回復したと論文は報告している。
phi3.5のq2_Kについては、2026-09-10付でOllama側のissue(https://github.com/ollama/ollama/issues/18252 )上でも欠陥主張自体が撤回されている。
llama3.2-1B系の2タグは、チェックポイントがライセンスで再ビルドできなかったため、原因不明のまま「機能しない」タグとして残っている。

この訂正の経緯自体が、今回の記事で主役にしたい部分である。
最初に見つけた問題が、調べ直すと別の問題だったという展開は、検証をやっているとしばしば起きることだが、それを自分で正直に書き直して公開し続けている著者の姿勢は参考になる。

## 筆者が実際にやったこと

ここは正直に書く。
論文のコードと監査データセットを公開しているリポジトリ`aditi-p31/quantcheck`(MIT License、データセットはCC BY 4.0)をクローンし、著者が実際に実行した生の評価ログを自分のスクリプトで読み込んで、独自に再集計した。
このリポジトリには、327件の評価対象それぞれについて、HumanEval+の164問全てに対するpass/fail判定と、実際にモデルが生成したテキストそのものが、JSONL形式でそのまま入っている。
つまり「論文の数字を信じる」のではなく、「論文の数字の元になっている生データを自分で読んで、自分で数えて、同じ数字になるか確かめる」という形の検証をした。

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/aditi-p31/quantcheck /tmp/quantcheck
python3 -I experiments/day-033/scripts/extract_qwen3b_progression.py /tmp/quantcheck
```

出力は以下の通りだった(`qwen2.5-coder:3b-instruct`の量子化レベルごとのHumanEval+通過数、15タスクのスモーク screenと164タスクのフル実行)。

```
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

q4_0より下の4レベル(q2_K/q3_K_S/q3_K_M/q3_K_L)は、15タスクのスモークでも164タスクのフル実行でも揃って0問、q4_0から上は15タスク全問正解という、崖のような段差になっている。
中間の緩やかな劣化ではなく、ある量子化レベルを境に完全にゼロへ落ちる、という点がこの論文の主張の核心であり、自分で再集計した数字でもそれがそのまま確認できた。

## 実際に何が生成されているのか

数字だけだと実感が湧かないので、同じタスク(`HumanEval/3`)に対する生成テキストそのものを比較した。
機能しないとされる`qwen2.5-coder:3b-instruct-q2_K`の実際の出力は、次のようなものだった。

```
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
(以下 "program" の繰り返しが続く)
```

一方、同じタスクに対する健全な`qwen2.5-coder:3b-instruct-q4_K_M`の出力は、通常通りdocstringから関数定義が始まる、まともなPythonコードだった。

```python
from typing import List


def below_zero(operations: List[int]) -> bool:
    """ You're given a list of deposit and withdrawal operations on a bank account...
```

q2_Kはエラーで落ちているわけではない。
モデルはロードされ、トークンは生成され続けている。
ただ、その中身がタスクの体裁すら保っていない単語の繰り返しになっている。
「動いているように見えて実は何も解けていない」というこの論文の指摘が、生ログを自分で開いてみると非常に具体的に伝わってきた。

## 論文の統計も自分で再計算してみた

論文は「7/305タグが機能しない(2.3%, Wilson 95% CI 1.1–4.7%)」という統計を報告している。
Wilson score intervalの計算式自体は難しくないので、自分でPythonで実装して検算した。

```python
import math
def wilson(k, n, z=1.96):
    phat = k / n
    denom = 1 + z**2 / n
    center = phat + z**2 / (2 * n)
    margin = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    return (center - margin) / denom, (center + margin) / denom
```

7/305を入れると2.295%、信頼区間は1.116〜4.661%となり、論文の「1.1–4.7%」と一致した。
モデル系列単位(3/35)でも8.6%、2.96〜22.38%となり、論文の「3.0–22.4%」と一致した。
論文の数字を右から左に引用するのではなく、同じ計算を自分の手元で再現できることを確かめておくと、記事に書く数字への納得感が変わってくる。

## Ollama公式タグで実際に再現してみた

著者の生ログを自分で再集計するだけでなく、Ollamaの公式タグを自分のPCで実際に`ollama pull`して推論させ、同じ崖が起きるかを確かめた。

```bash
ollama pull qwen2.5-coder:3b-instruct-q2_K
ollama pull qwen2.5-coder:3b-instruct-q4_K_M
```

両タグとも問題なくダウンロードできた。
harness/audit.pyと同じプロンプト・パラメータ(temperature=0, seed=0)で`HumanEval/3`を投げたところ、q2_Kは次のように崩壊した。

```
 program, program9 thrift {
 program; program9 thrift, program
 program
 program
 program
(以下 "program" の繰り返しが512トークン分続く)
```

一方のq4_K_Mは同じプロンプトから一発で正しいコードを生成した。

```python
def below_zero(operations: List[int]) -> bool:
    balance = 0
    for operation in operations:
        balance += operation
        if balance < 0:
            return True
    return False
```

著者が公開したログの再集計だけでなく、自分の環境・自分の推論実行でも同じ機能崩壊を確認できた。
q2_Kはダウンロードもロードも正常に完了しており、エラーで落ちているわけではなく、生成そのものがタスクの体裁を保てていない。

## まとめ

公開モデルレジストリから量子化タグを選ぶとき、サイズとタグ名だけで「軽いから選ぶ」という判断をしていると、この論文が報告したような、ダウンロードも推論もできるのにタスクを全く解けないタグを掴んでしまう可能性がある。
もっとも、今回確認できた7タグはいずれも4B以下の小型モデルの低bit量子化(q2_K〜q3_K_L)に集中しており、q4_0以上では同じモデル系列でも崖から外れていた。
量子化レベルを下げるときは、サイズだけでなくHumanEval+のようなタスクベースの動作確認を一度挟む価値がある、ということが、著者の生データを自分で再集計してみて納得できた。

実際にOllama公式タグをpull・推論させて確認した今回の結果は、論文が報告した現象が著者の環境固有のものではなく、誰の手元でも再現する種類の問題であることを裏付けている。

## 出典

- 論文: Aditi Patodiya, "Broken on Arrival: Non-Functional Quantized LLM Artifacts in Public Model Registries and How to Catch Them", arXiv:2609.05881 https://arxiv.org/abs/2609.05881
- コード・監査データセット: https://github.com/aditi-p31/quantcheck (コード: MIT License、監査データセット: CC BY 4.0)
- phi3.5の欠陥主張撤回の経緯: https://github.com/ollama/ollama/issues/18252
