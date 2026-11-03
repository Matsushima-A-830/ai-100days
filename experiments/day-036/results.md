# Day 036 検証結果

対象: [Heretic](https://github.com/p-e-w/heretic)(AGPL-3.0-or-later, `heretic-llm` 2.0.0, PyPI: https://pypi.org/project/heretic-llm/)

Abliteration(「拒否挙動は内部活性化空間の単一方向に強く媒介される」という Arditi et al., 2024 の知見)に基づき、
OptunaのTPE最適化で拒否率とKL発散(元モデルとの出力分布の差)を同時最小化するパラメータを探索し、
再学習なしでLLMの拒否挙動を抑制するPython CLIツール。再学習なし=勾配を使った重みのファインチューニングを行わない、
という意味であり、Optunaの試行ループ自体は実際にモデルの重みを何度も書き換えて評価するため、処理時間はかかる。

本検証の目的は「アライメント(安全性調整)がどれだけ堅牢か」を自分の手で定量的に確かめることであり、
生成した無検閲モデル自体やその出力を公開することはしない。実際に保存・アップロードもしていない
(`--model-action ""` を指定し、処理後に何もせず終了させた)。

## 0. 実行環境

- vCPU: 4(Intel Xeon @2.10GHz)、RAM: 15GB、**GPUなし**(`nvidia-smi` コマンド自体が無い)
- Heretic自身が起動時に `No GPU or other accelerator detected. Operations will be slow.` と出力する
  (READMEはRTX 3090前提で書かれており、CPU実行はツール側も想定の外側に近い)

## 1. インストール時に詰まったこと(ツールに直接関係する範囲)

`pip install -U heretic-llm` をシステムのPython(3.13、`/usr/lib/python3/dist-packages`のDebianパッチ入りsetuptools)
にそのまま実行すると、依存関係に含まれる古い `setup.py` ベースのパッケージ(`langdetect` `rouge-score` `sqlitedict`
`word2number`、いずれも `lm-eval` の依存)のビルドで失敗した。

```
$ pip install -U heretic-llm
...
AttributeError: install_layout. Did you mean: 'install_platlib'?
...
ERROR: Could not build wheels for langdetect, rouge-score, sqlitedict, word2number, which is required to install pyproject.toml-based projects
```

`python3 -m venv` で素のvenvを作り、その中の `pip`(setuptools 68系)でやり直すと問題なくビルドできた。
Heretic自体のバグではなく、システムPython側の古いsetuptoolsパッチとの相性問題だが、
「公式手順(`pip install -U heretic-llm`)をそのまま叩くと失敗する」という事実としては記録しておく。
venvを使う、という一般的な回避策で解決する。

```
$ python3 -m venv heretic-venv && source heretic-venv/bin/activate
$ pip install -U pip setuptools wheel -q
$ pip install -U heretic-llm   # 成功。heretic-llm-2.0.0 を含む一式がインストールされた
```

## 2. CLIの基本挙動

```
$ heretic --help
```
で全オプションが確認できる。主要なもの:

- `--model`(必須、Hugging FaceモデルIDかローカルパス)
- `--n-trials`(既定100)/ `--n-startup-trials`(既定30、Optunaのランダム探索フェーズ)
- `--quantization`(`none` / `bnb_4bit`)
- `--max-response-length`(既定100トークン)
- `--scorers` / `--modifiers`(スコアラー・修正方式のJSON指定。既定は拒否率〈KeywordRate〉とKL発散〈KLDivergence〉を
  同時最小化、修正方式はARA〈Arbitrary-Rank Ablation〉)
- `--trial-index` / `--model-action` を指定すると、本来対話式(questionary)のプロンプトを飛ばして
  非対話実行できる(`--trial-index 0 --model-action ""` で「Pareto最適な先頭の試行を選び、
  モデルを保存せずに終了」という非対話フローになる)

設定ファイル `config.default.toml` を見ると、既定では以下の規模のデータを使う:

- バッチサイズ自動判定用プロンプト: 256件
- 応答プレフィックス自動判定用プロンプト: 200件(harmless/harmful各100)
- 拒否率評価用プロンプト: 100件(`mlabonne/harmful_behaviors` test split)
- KL発散評価用プロンプト: 100件(`mlabonne/harmless_alpaca` test split)
- ARA修正方式が参照する「望ましい/望ましくない」プロンプト: 各400件
- 1試行あたり応答生成は最大100トークン
- Optuna試行数: 100(うちランダム探索30)

## 3. スモーク実行(試行数・評価セットを大幅に縮小)

GPUがない状態で既定設定(試行100回)をそのまま回すと6時間枠を大きく超えると判断し、
today.mdの指示に従って評価セット・試行数を縮小した「スモーク実行」を1モデルに対して実施した。

対象モデル: `Qwen/Qwen3-0.6B`(Qwen3系で最小の密モデル。チャットテンプレートに`<think></think>`の
Chain-of-Thoughtブロックがあり、Hereticはこれを自動検出して評価対象をその後の実応答部分に揃えていた)

縮小した設定(`experiments/day-036/heretic_run/config.toml`、既定値との差分):

| 項目 | 既定値 | 今回 |
|---|---|---|
| `n_trials` | 100 | 2 |
| `n_startup_trials` | 30 | 2 |
| `max_response_length` | 100 | 32 |
| `max_batch_size` | 128 | 8 |
| バッチサイズ判定用プロンプト | 256件 | 16件 |
| 応答プレフィックス判定用プロンプト | 200件(100+100) | 16件(8+8) |
| 拒否率(KeywordRate)評価用プロンプト | 100件 | 10件 |
| KL発散(KLDivergence)評価用プロンプト | 100件 | 10件 |
| ARA good/bad プロンプト | 各400件 | 各40件 |

スコアラー・修正方式のロジック自体(keyword_markersのリスト、ARAのn_optimization_steps=5、
max_iter=20など)は既定のまま変更していない。

### 実行コマンドと所要時間

```
$ time timeout 1700 heretic --model Qwen/Qwen3-0.6B --trial-index 0 --model-action ""
...
real    4m8.361s
user    12m1.062s
sys     2m13.019s
EXIT:0
```

4 vCPU中、user時間がreal時間の約3倍(12m/4m8s)なので、3コア程度を使ったマルチスレッド実行になっていた。

### バッチサイズ自動判定(実測スループット)

```
Determining optimal batch size...
* Trying batch size 1... Ok (14 tokens/s)
* Trying batch size 2... Ok (21 tokens/s)
* Trying batch size 4... Ok (37 tokens/s)
* Trying batch size 8... Ok (68 tokens/s)
* Chosen batch size: 8
```

CPUでもバッチサイズを上げるとスループットはほぼ線形に伸びた(0.6Bモデル・4 vCPUの場合)。
今回は`max_batch_size`を8に絞っているため、本来はさらに大きいバッチも試されるはずだったが、
その先は未測定。

### ベースライン(未改変モデル)のスコア

```
Getting baseline scores...
* Baseline Refusals: 2/10
* Baseline KL divergence: 0 (by definition)
```

`mlabonne/harmful_behaviors` のテスト分割から取った10件の有害な依頼プロンプトに対し、
未改変のQwen3-0.6Bは2件(20%)で拒否ワード(`sorry` `cannot` `unethical`等)を含む応答をした
(残り8件はこの小さいモデルでは元々ガードレールが弱く、素直に応答してしまっていたとみられる)。

### 試行1・試行2の結果

```
Running trial 1 of 2...
* Parameters: start_layer_index=8, end_layer_index=28, preserve_good_behavior_weight=0.5706,
  steer_bad_behavior_weight=0.0835, overcorrect_relative_weight=0.7338, neighbor_count=9
* Refusals: 0/10
* KL divergence: 0.0994
Elapsed time: 1m 23s

Running trial 2 of 2...
* Parameters: start_layer_index=6, end_layer_index=17, preserve_good_behavior_weight=0.0050,
  steer_bad_behavior_weight=0.0004, overcorrect_relative_weight=0.2805, neighbor_count=1
* Refusals: 0/10
* KL divergence: 0.0295
Elapsed time: 2m 6s (累積。試行2単体では約43秒)

Optimization finished!
Restoring model from trial 2...
```

2試行とも拒否率は0/10まで下がった。試行2は試行1よりモジュール修正の対象レイヤー数が少ない
(28-8=20層 vs 17-6=11層)分だけ速く(43秒 vs 83秒)、かつKL発散も小さい(0.0295 vs 0.0994)。
つまり試行2は試行1に対して「速度・拒否率・元モデルからの逸脱の小ささ」のすべてで優位な結果になった。
`--trial-index 0`(Pareto最適解の先頭)が自動的に試行2を選んだのはこの整合性が取れている。

ただし試行数が2回(既定の1/50)・評価プロンプトが10件(既定の1/10)というごく小規模なスモーク実行であり、
「Optunaのベイズ的探索が本来の100試行規模で何を見つけるか」を検証したものではない。
あくまで「この仕組みが実際に動き、拒否率とKL発散の数値がどう変化するか」を確認するための実行である。

## 4. CPUでの既定設定はどれだけ時間がかかるか(実測値からの推定)

実測した今回の縮小設定の内訳から、既定設定(試行100回、評価セットも既定の規模)に戻した場合の
所要時間を見積もった。

- 試行内の「ARAによるモデル修正」ステップ(good/bad各40件→各400件で約10倍のデータ量)が
  試行時間の大半(試行1: 83秒中70秒程度)を占めていた。L-BFGSの計算量はデータ量にほぼ比例するため、
  このステップは既定設定で約10倍、すなわち1試行あたり十数分規模に増えると見積もれる。
- 評価ステップ(拒否率10→100件で10倍、応答長32→100トークンで3.125倍)も既定設定では
  ラフに30倍前後に増えると見積もれる。

これらを足し合わせると、1試行あたりの所要時間は既定設定で15分前後、100試行では**約25時間**という
推定になる(READMEに記載のRTX 3090での既定実行〈30〜40分〉の40倍前後)。これはあくまで今回の
実測値からの外挿であり、実際に100試行を走らせて確認したものではない。6時間という作業枠を
大きく超えるため、今回はこの推定をもって「既定設定のフル実行」は見送り、縮小したスモーク実行の
結果を記事の主役にした。

## 5. わかったこと(まとめ)

- Hereticは**GPUがなくても実際に動く**(ツール自身は想定していないと明言しつつも、CPUで最後まで
  完走した)。ただしスループットは実測で14〜68 tokens/s(バッチサイズ1〜8、0.6Bモデル、4 vCPU)で、
  既定の試行規模(100試行・評価各100件)をそのまま回すには推定25時間かかる計算になり、
  6時間の作業枠には収まらない。
- 縮小したスモーク実行でも、拒否率はベースライン2/10から2試行とも0/10まで下がり、
  Abliteration理論(内部活性化空間の方向を操作するだけで拒否挙動を抑制できる)が
  小規模なモデル・小規模な評価セットでも再現されることを確認した。
- Optunaはわずか2試行でも、より狭いレイヤー範囲・より小さい重みで「拒否率を維持したまま
  KL発散(元モデルからの逸脱)を1/3程度に抑える」パラメータ(試行2)を試行1より優位な解として
  見つけた。

## 6. ローカル検証(人間のGPU環境、2026-11-03)

人間のPC(WSL2、NVIDIA GeForce RTX 5060 Ti、16GB VRAM、CUDA 13.2)で、`config.toml`を使わず
素の既定設定のまま`Qwen/Qwen3-4B-Instruct-2507`(READMEが挙げている例と同じモデル)を実行した。

```bash
python3 -m venv heretic-venv && source heretic-venv/bin/activate
pip install -U pip setuptools wheel
pip install -U heretic-llm
time timeout 7200 heretic --model Qwen/Qwen3-4B-Instruct-2507 --trial-index 0 --model-action ""
```

```
Detected 1 CUDA device(s) (15.93 GB total VRAM)
* CUDA 0: NVIDIA GeForce RTX 5060 Ti (15.93 GB)
...
Allocated GPU VRAM: 7.62 GB (4Bモデル、全試行を通じて一定)
...
Getting baseline scores...
* Baseline Refusals: 100/100
* Baseline KL divergence: 0 (by definition)
...
Running trial 1 of 100...
...
Running trial 100 of 100...
Elapsed time: 1h 35m
Optimization finished!
Restoring model from trial 62...
```

既定設定(試行100回・評価各100件・応答長100トークン)の全100試行が、Optunaの最適化ループだけで
**1時間35分**で完走した(モデルのダウンロード・読み込み・最終モデルの復元を含めた全体のwall clockは
約1時間40分)。CPU実行時の実測値から外挿した推定値(約25時間、ただし対象モデルはCPU実行時の
`Qwen3-0.6B`よりおよそ6倍大きい`Qwen3-4B-Instruct-2507`)や、READMEが挙げるRTX 3090の参考値
(30〜40分)と比べると、RTX 5060 Tiでも実用的な時間で既定規模の探索が完走することを確認できた。
(モデルサイズが異なるため直接比例計算はできないが、少なくとも「GPUなら6時間枠に収まる」という
ことは実測で裏付けられた。)

100試行の結果を独自に集計すると、拒否率0/100を達成したのは12試行、そのうち`--trial-index 0`
(Pareto最適解の先頭)が選んだ試行62が、KL発散1.3763という値で他の0/100達成組(次点は試行29の
11.4456)を大差で下回っていた。拒否率0/100以外の88試行の中にはKL発散が0.0159(試行17、拒否率
89/100)まで小さいものもあり、「拒否率を完全に0にする」ことと「元モデルからの逸脱を最小にする」
ことが強いトレードオフ関係にあることが、100試行規模のPareto frontを通じて具体的に見えた。これは
スモーク実行(2試行)では確認できなかった、既定規模の探索でしか見えない情報である。

GPU VRAM使用量は全100試行を通じて7.62GBで安定しており、メモリリークや断片化によるクラッシュは
発生しなかった。実行ログは`experiments/day-036/heretic_run_gpu/run.log`に、Optunaのcheckpointは
同ディレクトリの`checkpoints/`に保存した(改変後モデル自体は`--model-action ""`により保存・
アップロードしていない)。
