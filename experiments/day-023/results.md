# Day 023 検証結果: Graphify(コードベースの知識グラフ化)で grep/Read の代わりになるか実測する

対象: Graphify-Labs/graphify (PyPI配布名: `graphifyy`)
https://github.com/Graphify-Labs/graphify
インストールしたバージョン: 0.9.93

## ライセンス

- PyPIメタデータ上の `License-Expression` は `Apache-2.0`。
- 加えて `LICENSE-MIT` ファイルも同梱されている。`NOTICE` ファイルには
  「元はMITライセンスで提供していたが、Apache License 2.0へrelicenseした。
  relicense前にMITライセンス下で行われたコントリビューション部分はMIT条件のまま
  利用可能」という記載がある。
- つまりbacklog.mdで触れていた「Apache-2.0/MIT両方の記載」は不正確ではなく、
  現行の主ライセンスはApache-2.0、過去のMIT時代のコード部分のみMIT条件が併存する
  という経緯だと分かった。
- PyPI公式パッケージ名は `graphifyy`(ダブルy)。READMEに「他の`graphify*`という名前の
  PyPIパッケージは無関係」との注記があり、名前の衝突に注意が必要。

## 検証の範囲

today.mdの方針(追加の有料APIキー不要)に従い、`--code-only`モード
(tree-sitterによるローカルAST解析のみ、LLM呼び出し無し)に限定した。

1. 本リポジトリ(ai-100days)自身を対象に知識グラフを構築する。
2. 公式の `graphify benchmark` コマンドでトークン削減率を計測する。
3. 自分で立てた具体的な1つの質問について、
   (a) 素朴に関連ファイルを全文読む場合、
   (b) 経験のあるエンジニアがgrepで当たりを付けて必要箇所だけ読む現実的な場合、
   (c) `graphify explain` を使う場合、
   の3パターンで「読み込む文字数」を実測し、概算トークン数を比較する。
4. `graphify query` の自然言語質問としての挙動を日本語・英語それぞれで確認する。

ドキュメント・PDF・画像の意味抽出(LLM使用)、PostgreSQL連携、Neo4j連携などは
今回のスコープ外。

## 1. インストール(APIキー不要・完全ローカル)

```
$ uv tool install graphifyy
Downloading numpy (16.1MiB)
Downloading networkx (2.0MiB)
Downloading graphifyy (1.6MiB)
Installed 30 packages in 19ms
 + graphifyy==0.9.93
 + networkx==3.6.1
 + numpy==2.4.6
 + rapidfuzz==3.14.6
 + tree-sitter==0.25.2
 + tree-sitter-bash==0.25.1
 (... 言語ごとのtree-sitterパーサ多数 ...)
Installed 2 executables: graphify, graphify-mcp

$ graphify --version
graphify 0.9.93
```

追加の有料APIキー・GPUともに不要で導入できた。

## 2. `--code-only`でのグラフ構築

```
$ time graphify extract . --code-only --out experiments/day-023/graphify-out
[graphify extract] scanning /home/user/ai-100days
[graphify extract] --code-only: skipping 242 non-code file(s) (223 docs, 4 papers, 15 images) — no LLM extraction
[graphify extract] found 90 code, 0 docs, 0 papers, 0 images
[graphify extract] 28 file(s) not classified (no supported extension or shebang), skipped: .gitattributes, .gitignore, .gitkeep, LICENSE, LICENSE-upstream, after-literature-review.stderr.log (+22 more)
[graphify extract] AST extraction on 90 code files...
  warning: 11 code file(s) yielded no symbols (0.01 MB) — a data file, or source this extractor models no symbols for: experiments/day-002/rust/Cargo.toml, experiments/day-004/verify/dataset.py (+9 more)
[graphify] note: node 'experiments_day_018_samples_recovered_module' was extracted twice from 'experiments/day-018/samples/recovered-module.js' under different labels — keeping '_', dropping 'recovered-module.js'.
[graphify extract] wrote .../graph.json: 914 nodes, 1657 edges, 56 communities

real    0m1.953s
```

(補足: `--out experiments/day-023/graphify-out`と指定すると、ツールの仕様で
さらにその下に`graphify-out/`というサブディレクトリが作られ、実際には
`experiments/day-023/graphify-out/graphify-out/graph.json`に書き出される。
本リポジトリにコミットするファイルは見やすさのため、その内容を1段上の
`experiments/day-023/graphify-out/`直下に移動してある。以降この節で示す
コマンド例は実際に実行したときのパスそのままにしている。)

Day 022までの22日分・90個のコードファイルの解析が2秒足らずで完了した。ログに
"no LLM extraction"と明記されている通り、この間一度もLLM API呼び出しは発生していない。

```
$ graphify cluster-only experiments/day-023/graphify-out --no-label
Loading existing graph...
Graph: 914 nodes, 1657 edges
Re-clustering...
Done - 56 communities. GRAPH_REPORT.md, graph.json and graph.html updated.
```

`--no-label`を指定したのは「有料APIキー必須の候補は選ばない」方針を守るため
(labelコマンド/clusterのラベル付けはLLMバックエンドを使うオプション機能であり、
指定しなければ"Community N"という無名のままで構わない)。

## 3. 公式`benchmark`コマンドでの計測

```
$ graphify benchmark experiments/day-023/graphify-out/graphify-out/graph.json

graphify token reduction benchmark
──────────────────────────────────────────────────
  Corpus:          45,700 words → ~60,933 tokens (naive)
  Graph:           914 nodes, 1,657 edges
  Avg query cost:  ~1,616 tokens
  Reduction:       37.7x fewer tokens per query

  Per question:
    [37.4x] what is the main entry point
    [37.8x] what connects the data layer to the api
    [37.9x] what are the core abstractions
```

本リポジトリ(90ファイル、914ノード)という中規模コードベースでは、公式コマンド自身が
出す値として**37.7倍**という結果になった。日本語記事でよく言及される
「71.5分の1」という数字はここでは再現しなかった(ベンチマークの質問セットも
リポジトリの性質も異なるため単純比較はできないが、同じ"公式benchmarkコマンド"を
使った上でもっと小さい値が出た、という事実は記録しておく)。

## 4. 自分の質問での実測(Before/After)

質問: 「day-022のKronos実験で、`KronosPredictor`クラスはどこで定義され、
どのファイルから使われていて、どんなメソッドを持つか」

### (a) 素朴に関連ファイルを全文読む場合

```
$ grep -rln "KronosPredictor" experiments/day-022/ --include="*.py"
experiments/day-022/model/kronos.py
experiments/day-022/main_run.py
experiments/day-022/model/__init__.py
experiments/day-022/sample_count_test.py
experiments/day-022/cpu_feasibility_test.py

$ wc -c experiments/day-022/model/kronos.py experiments/day-022/main_run.py \
       experiments/day-022/model/__init__.py experiments/day-022/sample_count_test.py \
       experiments/day-022/cpu_feasibility_test.py
  30133 experiments/day-022/model/kronos.py
   2416 experiments/day-022/main_run.py
    395 experiments/day-022/model/__init__.py
   1492 experiments/day-022/sample_count_test.py
   1045 experiments/day-022/cpu_feasibility_test.py
  35481 合計
```

5ファイルを全文読むと**35,481文字**。4文字≒1トークンという粗い近似で
概算**約8,870トークン**。

### (b) 経験あるエンジニアの現実的な探索(grep+該当箇所だけ読む)

```
$ grep -rn "KronosPredictor" experiments/day-022/ --include="*.py" | wc -c
910
```

grepの出力(910文字)で5ファイル中の該当行が全て分かる。続いて
`kronos.py`のクラス定義部分(L482-570、89行)と各利用箇所の数行だけを読むと

```
$ sed -n '482,570p' experiments/day-022/model/kronos.py | wc -c   # クラス本体
(各ファイルの利用箇所付近 数行を合わせて)
合計 6286文字
```

grep出力(910)+対象箇所の読み込み(6286) = **7,196文字 → 概算約1,799トークン**。

### (c) `graphify explain`

```
$ graphify explain "KronosPredictor" --graph experiments/day-023/graphify-out/graphify-out/graph.json
Node: KronosPredictor
  ID:        experiments_day_022_model_kronos_kronospredictor
  Source:    experiments/day-022/model/kronos.py L482
  Type:      code
  Community: Community 1
  Degree:    9

Connections (9):
  <-- kronos.py [contains] [EXTRACTED] experiments/day-022/model/kronos.py:L482
  <-- main_run.py [imports] [EXTRACTED] experiments/day-022/main_run.py:L7
  <-- __init__.py [imports] [EXTRACTED] experiments/day-022/model/__init__.py:L1
  <-- sample_count_test.py [imports] [EXTRACTED] experiments/day-022/sample_count_test.py:L4
  <-- cpu_feasibility_test.py [imports] [EXTRACTED] experiments/day-022/cpu_feasibility_test.py:L4
  --> .generate() [method] [EXTRACTED] experiments/day-022/model/kronos.py:L508
  --> .predict_batch() [method] [EXTRACTED] experiments/day-022/model/kronos.py:L562
  --> .predict() [method] [EXTRACTED] experiments/day-022/model/kronos.py:L519
  --> .__init__() [method] [EXTRACTED] experiments/day-022/model/kronos.py:L484
```

出力は**966文字 → 概算約242トークン**。これ1回のコマンドで
「定義場所・import元4ファイル・メソッド4つ」という質問への答えが一通り揃う。

### 比較

| 方法 | 文字数 | 概算トークン | graphify比 |
|---|---|---|---|
| (a) 関連5ファイルを全文読む | 35,481 | 約8,870 | 36.6倍 |
| (b) grep + 該当箇所だけ読む(現実的なワークフロー) | 7,196 | 約1,799 | 7.4倍 |
| (c) `graphify explain` | 966 | 約242 | - |

**公式`benchmark`コマンドの37.7倍という数字は、(a)の「愚直に全文読む」場合との
比較に近い値になった。** 一方、経験のあるエンジニアがgrepで当たりを付けて
必要な箇所だけ読む(b)という、実際にはよくある現実的なワークフローと比べると、
優位性は7倍程度まで縮んだ。今回計測したのは「定義元1ファイル+利用元4ファイル」
という比較的シンプルな呼び出し関係のケースであり、より複雑に飛び石状に
参照し合うコードでは差が開く可能性はある。それでも、少なくとも今回測った範囲では
日本語記事で言及される「71.5分の1」のような極端な数字は出なかった。

## 5. `graphify query`の自然言語質問としての挙動

日本語で質問した場合:

```
$ graphify query "KronosPredictorを呼び出している箇所はどこか" \
    --graph experiments/day-023/graphify-out/graphify-out/graph.json --budget 2000
Graph: ... | Traversal: BFS depth=2 | Start: ['compare_memory.pyと同一ロジック(比較の基準線として再掲)。', ...] | 12 nodes found

NODE compare_memory.pyと同一ロジック(比較の基準線として再掲)。 [src=experiments/day-008/compare_memory_embargo.py ...]
NODE DestructiveSummaryMemory [src=experiments/day-008/compare_memory.py ...]
(以下、day-008のメモリ実験のコードが12件。KronosPredictorは1件も含まれない)
```

`KronosPredictor`という単語は無視され、まったく無関係なday-008(メモリ実験)の
ノードが返ってきた。キーワードマッチが外れたまま、ヒットしなかったことを
エラーにせず「それっぽいノード」を返してしまう挙動だと分かった。

英語での質問も試したが、こちらも芳しくなかった:

```
$ graphify query "who calls KronosPredictor" \
    --graph experiments/day-023/graphify-out/graphify-out/graph.json --budget 2000
Graph: ... | Traversal: BFS depth=2 | Start: ['KronosPredictor'] | Context: call (heuristic) | 1 nodes found

NODE KronosPredictor [src=experiments/day-022/model/kronos.py loc=L482 community=Community 1]
```

シード自身の1件だけが返り、呼び出し元を辿れていない。同じ質問に対して
`graphify explain "KronosPredictor"`(上記4.(c))の方が安定して有用な答えを返した。
「自然言語で質問できる」という`query`コマンドの売り文句は、少なくとも
日本語クエリでは機能せず、英語でも`explain`(ノード名を直接指定する)の方が
信頼できる結果だった。この制約についての明記はREADME上では見当たらなかった。

## 6. インクリメンタル更新(`update`)時に観測した非決定性

検証中、`experiments/day-022/main_run.py`に1行コメントを追記しただけの変更の後、
`graphify update experiments/day-023/graphify-out`を実行したところ、
914ノード/1657エッジ/56コミュニティ → 890ノード/1554エッジ/51コミュニティという、
1行コメント追加だけでは説明できない規模の変化が起きた。コメントを取り消して
`graphify extract`をクリーンな状態からやり直すと914/1657/56に戻った。
重複ラベルの解決順序や再クラスタリングの非決定性が原因の可能性があるが、
今回はそこまでは特定できていない。ノード・エッジ・コミュニティの正確な件数を
厳密な指標として扱うのは避けた方がよい、という所見として残す。
(本記事・X投稿案の数値は、すべてこの節とは無関係な「クリーンな状態からの
`extract`→`cluster-only`」の結果に基づく。4.と5.の実測もすべてこの版で統一している。)

## 7. Routine環境の制約により未検証(ローカル検証待ち)

`graph.html`をブラウザで確認する工程で、`vis is not defined` / `network is not defined`
というJSエラーが発生し可視化が描画されなかった。原因は`graph.html`が
`https://unpkg.com/vis-network@9.1.6/...`というCDNからvis-network.jsを読み込む構成で
あり、このRoutine実行環境のネットワークプロキシがunpkg.comへの接続を
403(policy denial)で拒否していたため。CLAUDE.mdに記載されている
「Routine環境のネットワーク制限によるCDN/自動ダウンロードのブロック」に該当するため、
記事・X投稿案・シェアカードでは触れていない。

ローカル検証待ち: 通常のインターネット接続があるローカルPCで、本PRにコミット済みの
`experiments/day-023/graphify-out/graph.html`をそのままブラウザで開いて
ノードリンク図が正しく描画されるか確認してください
(手元で最初から再現する場合は以下の手順。ツールの仕様で`--out`の下にさらに
`graphify-out/`が作られるため、生成されるパスは`graphify-out/graphify-out/graph.html`になる)。

再現手順:
```
cd experiments/day-023
uv tool install graphifyy
graphify extract /path/to/ai-100days --code-only --out graphify-out
graphify cluster-only graphify-out --no-label
# graphify-out/graphify-out/graph.html をブラウザで開く
```

## まとめ

- `--code-only`なら本当にAPIキー・GPU不要・完全ローカルで、中規模リポジトリ
  (90ファイル)の知識グラフ構築が2秒以内で終わる。これ自体は主張通り動いた。
- トークン削減効果は「比較対象をどう取るか」で大きく変わる。公式ベンチマークや
  「全文を愚直に読む」との比較では30〜38倍程度出るが、経験あるエンジニアの
  現実的なgrepワークフローと比べると7倍程度まで縮む。どちらも「71.5分の1」には
  届かなかった。
- `query`コマンドの自然言語対応は過大評価気味で、特に日本語では機能しなかった。
  ノード名を直接指定する`explain`の方が信頼できた。
- ライセンスはApache-2.0が現行の主ライセンスで、MITはrelicense前のコード分のみ
  併存する形。
