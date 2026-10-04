# Day 006: CTWM(Core-Tail World Model)の縮小版・次状態予測ループ

出典: Song & Cai, *Heavy-Tailed Memory Traces in Long-Horizon Language Agents*
(arXiv: https://arxiv.org/abs/2610.00010 , コード: https://github.com/Hik289/world-model-self-organized-criticality , MIT License)

## これは何か

本家の「合成グラフ世界をLLMポリシーで歩き、CTWMメモリで次状態を予測する」
実験は外部LLM API(OpenAI互換エンドポイント)が前提になっている。本リポジトリの
方針(有料APIキー不要)に沿うため、**合成グラフ世界の生成コードとCTWMメモリ
コントローラ本体だけを本家から無改変で再利用し、「次の遷移を予測する」部分を
Claude Code自身(このRoutine自身)が手動ループで代替する**縮小版の概念実証を行った。

最初の試行(v1, 24ノード・35ステップ)は両設定とも予測正解率0%という結果に
終わった。原因を分析し、予測ルールを頻度ベースに変えグラフ規模を拡大した
再実験(v2, 60ノード・61ステップ)では、**正解率は両設定とも13.3%で同じ
だったが、ctwmはbaselineの約6割の文字数で同じ精度を達成した**。
詳しい結果と正直な経緯は [`results.md`](./results.md) を参照。

## ディレクトリ構成

```
day-006/
├── README.md                    # このファイル
├── results.md                   # 正直な実行結果ログ(v1・v2両方)
├── run_prediction_loop.py       # v1オーケストレータ(最上位エントリ予測、24ノード)
├── run_meta.json                # v1: グラフ・メモリ設定のメタ情報(実行で生成)
├── prediction_results.json      # v1: 予測結果の生ログ・集計(実行で生成)
├── logs/                        # v1: 各ステップで見せた実際のプロンプト(20ファイル)
├── run_prediction_loop_v2.py    # v2オーケストレータ(頻度ベース予測、60ノード)
├── run_meta_v2.json             # v2: グラフ・メモリ設定のメタ情報(実行で生成)
├── prediction_results_v2.json   # v2: 予測結果の生ログ・集計(実行で生成)
├── logs_v2/                     # v2: 各ステップで見せた実際のプロンプト(30ファイル)
└── vendor/                      # 本家コードの無改変コピー(MIT License、v1/v2共通)
    ├── synthetic_graph_world.py
    ├── backends_ctwm.py
    ├── LICENSE
    └── NOTICE.md
```

## 再現手順

### 0. 依存パッケージ

```bash
pip install networkx numpy
```

(APIキーは一切不要)

### v1(最初の試行、正解率0%)を再現する

```bash
cd experiments/day-006
python3 run_prediction_loop.py init
```

シード固定の24ノード合成グラフ(`scale_free`)上で35ステップのランダム
ウォークを1回生成し、`baseline`(tau=0.0, 均等配分)と `ctwm`(tau=1.0, CTWM推奨値)
の2つのメモリに観測フェーズ(24遷移)を書き込む。最初の予測プロンプトが
`logs/baseline_step24_prompt.txt` に出力される。

```bash
cat logs/baseline_step24_prompt.txt   # プロンプトを読む(正解は書かれていない)
python3 run_prediction_loop.py answer --label baseline --step 24 --prediction <整数 or unknown>
```

実行すると、その場で正解と照合してログに記録し、実際の遷移をメモリに書き込んで
から次のプロンプトファイルを出力する。`baseline` の10ステップ → `ctwm` の10ステップ
の順に進み、両方終わると `prediction_results.json` に集計結果が書き出される。

v1では各ステップで以下の予測ルールを一貫して適用した(事前に決めた固定ルール):

> ヒント(`context_string()` の core/tail 表示)に現在状態からの遷移が含まれて
> いれば最上位(スコア最高)のものの next を予測する。含まれていなければ
> `unknown` と答える。

やり直したい場合は `state.pkl` を削除すれば `init` から再実行できる
(seed固定なので同じグラフ・ウォークが再構築される)。

```bash
rm -f state.pkl run_meta.json prediction_results.json
rm -f logs/*.txt
python3 run_prediction_loop.py init
```

### v2(改善版、頻度ベース予測+規模拡大)を再現する

```bash
cd experiments/day-006
python3 run_prediction_loop_v2.py init
```

シード固定の60ノード合成グラフ上で61ステップのランダムウォークを生成し、
同じ2つのメモリ設定(tail_slotsのみv1と同じ)に観測フェーズ(45遷移)を
書き込む。最初の予測プロンプトが `logs_v2/baseline_step45_prompt.txt` に出力される。

```bash
cat logs_v2/baseline_step45_prompt.txt
python3 run_prediction_loop_v2.py answer --label baseline --step 45 --prediction <整数 or unknown>
```

v2のプロンプトにはv1と違い、各ヒントエントリの頻度 `f` が明示される。
予測ルールは以下の頻度ベースに変更した:

> ヒントの中に現在状態をprevとするエントリがあれば、最も頻度(f)の高い
> next を予測する(同率なら先に表示されている方)。無ければ `unknown`。

`baseline` の15ステップ → `ctwm` の15ステップの順に進み、両方終わると
`prediction_results_v2.json` に集計結果が書き出される。やり直す場合は
`state_v2.pkl` と `logs_v2/*.txt`・`run_meta_v2.json`・`prediction_results_v2.json`
を削除してから再実行する。

## ライセンス・出典についての注意

`vendor/` 配下のコードは https://github.com/Hik289/world-model-self-organized-criticality
からMIT Licenseのもと無改変でコピーしたもの。詳細は `vendor/NOTICE.md` と
`vendor/LICENSE` を参照。`run_prediction_loop.py` と本ディレクトリのその他のファイルは
この検証のために新規に書いたもの。
