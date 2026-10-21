---
title: "知識グラフ化ツールGraphifyでgrep/Readを置き換えたら、トークンは何倍減るのか実測した"
emoji: "🕸️"
type: "tech"
topics: ["ai", "llm", "python", "claudecode", "graphrag"]
published: false
---

## これは何の話か

海外AIネタ100日チャレンジDay 023。今回取り上げるのは[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)(PyPI配布名は`graphifyy`、ダブルyなので注意)。

コード・ドキュメント・SQLスキーマ・設定ファイルなどを1つの問い合わせ可能な知識グラフに変換するPython CLIで、Claude Code/Cursor/Codex/Gemini CLIなど向けのスキルとしても配布されている。
コード解析はtree-sitterによる完全ローカル・決定的な処理で、`--code-only`オプションを使えばLLM呼び出し無し・外部送信無しの完全オフラインで動く。

謳われている使い方は、AIコーディングエージェントが毎回grepや`Read`を繰り返す代わりに、事前に作った知識グラフへ`graphify query`等で問い合わせることでコンテキストに読み込むトークン量を大きく削れる、というものだ。

日本語記事はすでに何件もあり、「71.5分の1」というトークン削減率を紹介する記事も見かけた。
筆者はその数字が自分の環境・自分のコードベース規模でどの程度再現するのか気になったので、このリポジトリ(ai-100days)自身を対象に実際に動かして確かめてみた。

- 出典: https://github.com/Graphify-Labs/graphify
- ライセンス: 現行はApache-2.0(PyPIメタデータの`License-Expression`より)。
  加えて`LICENSE-MIT`も同梱されており、`NOTICE`ファイルによると元はMITライセンスで提供していたプロジェクトをApache-2.0へrelicenseした経緯がある(relicense前のコード部分はMIT条件のまま利用可能)。

## 導入とグラフ構築はAPIキー無しで本当に動いた

```
$ uv tool install graphifyy
Installed 30 packages in 19ms
 + graphifyy==0.9.93
Installed 2 executables: graphify, graphify-mcp

$ graphify --version
graphify 0.9.93
```

本リポジトリ全体を対象に`--code-only`でグラフを構築する。

```
$ time graphify extract . --code-only --out experiments/day-023/graphify-out
[graphify extract] --code-only: skipping 242 non-code file(s) (223 docs, 4 papers, 15 images) — no LLM extraction
[graphify extract] found 90 code, 0 docs, 0 papers, 0 images
[graphify extract] AST extraction on 90 code files...
[graphify extract] wrote .../graph.json: 914 nodes, 1657 edges, 56 communities

real    0m1.953s
```

Day 022までの22日分・90個のコードファイルの解析が2秒足らずで完了した。
ログにも"no LLM extraction"と明記されている通り、この間一度もLLM API呼び出しは発生していない。
追加の有料APIキー・GPUともに不要というtoday.mdの前提は満たされていた。

## 公式benchmarkコマンドでの計測: 37.7倍

graphifyには「トークン削減率を測る」ための公式コマンドがそのまま用意されている。

```
$ graphify benchmark experiments/day-023/graphify-out/graph.json

graphify token reduction benchmark
──────────────────────────────────────────────────
  Corpus:          45,700 words → ~60,933 tokens (naive)
  Graph:           914 nodes, 1,657 edges
  Avg query cost:  ~1,616 tokens
  Reduction:       37.7x fewer tokens per query
```

本リポジトリでは**37.7倍**という結果だった。
日本語記事でよく見る「71.5分の1」は、ベンチマークの質問セットも対象コードベースも異なるため単純比較はできないものの、同じ"公式コマンド"を使っても私の環境ではもっと小さい値になった。

## 自分で質問を立てて測る: 「公式ベンチマーク」と「現実のワークフロー」は別物

公式ベンチマークの質問("what is the main entry point"等)は汎用的すぎて、実際にエージェントが遭遇する質問とは少し違う気がしたので、具体的な質問を自分で立てて測り直した。

> Day 022のKronos実験で、`KronosPredictor`クラスはどこで定義され、どのファイルから使われていて、どんなメソッドを持つか?

### (a) 素朴に関連ファイルを全文読む

```
$ grep -rln "KronosPredictor" experiments/day-022/ --include="*.py"
experiments/day-022/model/kronos.py
experiments/day-022/main_run.py
experiments/day-022/model/__init__.py
experiments/day-022/sample_count_test.py
experiments/day-022/cpu_feasibility_test.py
```

この5ファイルを全文読むと合計35,481文字になる。
4文字≒1トークンという粗い近似で**約8,870トークン**。

### (b) grepで当たりを付けて必要箇所だけ読む(現実的なワークフロー)

grepの出力(910文字)と、`kronos.py`のクラス定義部分・各利用箇所の数行だけ(6286文字)を合わせて7,196文字、**約1,799トークン**になる。
これは経験のあるエンジニアが実際にやりそうな探索方法に近い。

### (c) `graphify explain`

```
$ graphify explain "KronosPredictor" --graph experiments/day-023/graphify-out/graph.json
Node: KronosPredictor
  Source:    experiments/day-022/model/kronos.py L482
  Degree:    9

Connections (9):
  <-- kronos.py [contains] experiments/day-022/model/kronos.py:L482
  <-- main_run.py [imports] experiments/day-022/main_run.py:L7
  <-- __init__.py [imports] experiments/day-022/model/__init__.py:L1
  <-- sample_count_test.py [imports] experiments/day-022/sample_count_test.py:L4
  <-- cpu_feasibility_test.py [imports] experiments/day-022/cpu_feasibility_test.py:L4
  --> .generate() [method] experiments/day-022/model/kronos.py:L508
  --> .predict_batch() [method] experiments/day-022/model/kronos.py:L562
  --> .predict() [method] experiments/day-022/model/kronos.py:L519
  --> .__init__() [method] experiments/day-022/model/kronos.py:L484
```

出力は966文字、**約242トークン**だった。
これ1回のコマンドで「定義場所・import元4ファイル・メソッド4つ」という質問への答えが揃う。

### 比較結果

| 方法 | 概算トークン | graphify比 |
|---|---|---|
| (a) 関連5ファイルを全文読む | 約8,870 | 36.6倍 |
| (b) grep + 該当箇所だけ読む | 約1,799 | **7.4倍** |
| (c) graphify explain | 約242 | - |

公式`benchmark`の37.7倍という数字は、(a)の「愚直に全文読む」場合との比較に近い値だった。
一方、経験あるエンジニアがgrepで当たりを付けて必要な箇所だけ読むという、実際にはよくある現実的なワークフローと比べると、優位性は**7倍程度**まで縮んだ。
今回測ったのは「定義元1ファイル+利用元4ファイル」という比較的シンプルなケースで、もっと複雑に飛び石状に参照し合うコードでは差が開く可能性はある。
それでも、少なくとも筆者が測った範囲では「71.5分の1」のような極端な数字は出なかった。
公式ベンチマークの数字を見るときは、何との比較なのかを確認した方がよさそうだ。

## 「自然言語で質問できる」query は、日本語では機能しなかった

graphifyの売り文句の一つが、`graphify query "自然言語の質問"`でグラフをBFS探索できるというものだ。
試してみた。

```
$ graphify query "KronosPredictorを呼び出している箇所はどこか" \
    --graph experiments/day-023/graphify-out/graph.json --budget 2000
Graph: ... | Start: ['compare_memory.pyと同一ロジック(比較の基準線として再掲)。', ...] | 12 nodes found

NODE compare_memory.pyと同一ロジック(比較の基準線として再掲)。 [src=experiments/day-008/compare_memory_embargo.py ...]
NODE DestructiveSummaryMemory [src=experiments/day-008/compare_memory.py ...]
(以下、day-008のメモリ実験のコードが12件。KronosPredictorは1件も含まれない)
```

`KronosPredictor`という単語は無視され、まったく無関係なDay 008(メモリ実験)のノードが12件返ってきた。
エラーにせず「それっぽいノード」を返す挙動のようだ。

英語の質問でも試したが、

```
$ graphify query "who calls KronosPredictor" \
    --graph experiments/day-023/graphify-out/graph.json --budget 2000
Graph: ... | Start: ['KronosPredictor'] | Context: call (heuristic) | 1 nodes found

NODE KronosPredictor [src=experiments/day-022/model/kronos.py loc=L482 community=Community 1]
```

シード自身の1件だけが返り、呼び出し元を辿れていない。
先に挙げた`graphify explain "KronosPredictor"`の方が、同じ質問に対してずっと有用な答えを返した。
「自然言語で質問できる」というのは、少なくとも日本語クエリでは機能せず、英語でも`query`より`explain`(ノード名を直接指定する)の方が信頼できる結果だった。

## ライセンスと注意点

PyPIメタデータ上の現行ライセンスは**Apache-2.0**。
加えて`LICENSE-MIT`も同梱されており、`NOTICE`ファイルに「元はMITライセンスで提供していたが、Apache License 2.0へrelicenseした。relicense前のMITライセンス下のコントリビューションはMIT条件のまま利用可能」という記載がある。
つまり「Apache-2.0とMIT両方の記載がある」というのは正確で、現行の主ライセンスはApache-2.0、過去のMIT時代のコード部分のみMIT条件が併存する形だった。

もう一点、PyPIの公式パッケージ名は`graphifyy`(ダブルy)。
README上に「他の`graphify*`パッケージは無関係」との注記があり、名前の衝突に注意が必要。

## まとめ

- `--code-only`なら本当にAPIキー・GPU不要・完全ローカルで、90ファイル規模のリポジトリの知識グラフ構築が2秒以内で終わった。これは主張通り動いた。
- トークン削減効果は比較対象次第で大きく変わる。「全文を愚直に読む」との比較や公式ベンチマークでは30〜38倍程度出るが、経験あるエンジニアの現実的なgrepワークフローと比べると7倍程度まで縮んだ。どちらも「71.5分の1」には届かなかった。
- `query`の自然言語対応は過大評価気味で、特に日本語では機能しなかった。ノード名を直接指定する`explain`の方が信頼できた。
- 検証中に`graphify update`実行後のノード数が非決定的にブレる場面も観測した(詳細はリポジトリ内の実行ログに記録)。グラフの正確なノード数を厳密な指標として扱うのは避けた方がよさそうだ。

「知識グラフでgrep/Readを置き換えればトークンが激減する」という主張自体は方向性として正しいと感じたが、効果の大きさは「何と比べるか」次第でかなり変わる、というのが今回の実測から得た実感だった。
