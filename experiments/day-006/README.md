# Day 006: CTWM(Core-Tail World Model)の縮小版・次状態予測ループ

出典: Song & Cai, *Heavy-Tailed Memory Traces in Long-Horizon Language Agents*
(arXiv: https://arxiv.org/abs/2610.00010 , コード: https://github.com/Hik289/world-model-self-organized-criticality , MIT License)

## これは何か

本家の「合成グラフ世界をLLMポリシーで歩き、CTWMメモリで次状態を予測する」
実験は外部LLM API(OpenAI互換エンドポイント)が前提になっている。本リポジトリの
方針(有料APIキー不要)に沿うため、**合成グラフ世界の生成コードとCTWMメモリ
コントローラ本体だけを本家から無改変で再利用し、「次の遷移を予測する」部分を
Claude Code自身(このRoutine自身)が手動ループで代替する**縮小版の概念実証を行った。

詳しい結果と、正直な失敗(両設定とも予測正解率0%だった等)は [`results.md`](./results.md) を参照。

## ディレクトリ構成

```
day-006/
├── README.md                 # このファイル
├── results.md                # 正直な実行結果ログ
├── run_prediction_loop.py    # オーケストレータ本体(このRoutine向けの手動ループ)
├── run_meta.json             # グラフ・メモリ設定のメタ情報(実行で生成)
├── prediction_results.json   # 予測結果の生ログ・集計(実行で生成)
├── logs/                     # 各ステップでRoutineに見せた実際のプロンプト(20ファイル)
└── vendor/                   # 本家コードの無改変コピー(MIT License)
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

### 1. グラフ・ウォーク・観測フェーズを再構築する

```bash
cd experiments/day-006
python3 run_prediction_loop.py init
```

これでシード固定の24ノード合成グラフ(`scale_free`)上で35ステップのランダム
ウォークを1回生成し、`baseline`(tau=0.0, 均等配分)と `ctwm`(tau=1.0, CTWM推奨値)
の2つのメモリに観測フェーズ(24遷移)を書き込む。最初の予測プロンプトが
`logs/baseline_step24_prompt.txt` に出力される。

### 2. 予測ループを1ステップずつ回す

```bash
cat logs/baseline_step24_prompt.txt   # プロンプトを読む(正解は書かれていない)
python3 run_prediction_loop.py answer --label baseline --step 24 --prediction <整数 or unknown>
```

実行すると、その場で正解と照合してログに記録し、実際の遷移をメモリに書き込んで
から次のプロンプトファイルを出力する。`baseline` の10ステップ → `ctwm` の10ステップ
の順に進み、両方終わると `prediction_results.json` に集計結果が書き出される。

この検証では、各ステップで以下のルールを一貫して適用した(事前に決めた固定ルール):

> ヒント(`context_string()` の core/tail 表示)に現在状態からの遷移が含まれて
> いれば最上位(スコア最高)のものの next を予測する。含まれていなければ
> `unknown` と答える。

### 3. やり直したい場合

`state.pkl` を削除すれば `init` から再実行できる(seed固定なので同じグラフ・
ウォークが再構築される)。

```bash
rm -f state.pkl run_meta.json prediction_results.json
rm -f logs/*.txt
python3 run_prediction_loop.py init
```

## ライセンス・出典についての注意

`vendor/` 配下のコードは https://github.com/Hik289/world-model-self-organized-criticality
からMIT Licenseのもと無改変でコピーしたもの。詳細は `vendor/NOTICE.md` と
`vendor/LICENSE` を参照。`run_prediction_loop.py` と本ディレクトリのその他のファイルは
この検証のために新規に書いたもの。
