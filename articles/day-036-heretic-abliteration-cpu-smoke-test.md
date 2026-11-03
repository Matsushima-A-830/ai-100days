---
title: "GPUなしでAbliteration CLI『Heretic』を動かし、拒否率とKL発散を実測した"
emoji: "🧩"
type: "tech"
topics: ["ai", "llm", "python", "optuna", "machinelearning"]
published: false
---

## これは何を試した記事か

[Heretic](https://github.com/p-e-w/heretic) という、LLMの拒否挙動(いわゆる検閲・安全性アラインメント)を再学習なしで抑制するPython製CLIツールを実際に動かし、処理前後の拒否率とKL発散(元モデルの出力分布からのズレ)を数値で確認した記事である。
筆者の環境にはGPUがなく、READMEが前提にしているRTX 3090での実行(既定設定で30〜40分)とは条件が大きく異なる。
そこで「GPUなしのCPU環境でこのツールはどこまで動くのか、既定設定を全部回すとどれくらいかかるのか」を実測し、試行数と評価セットを大幅に絞った「スモーク実行」1回分の結果を主役にしている。

出典は本家リポジトリ(https://github.com/p-e-w/heretic 、AGPL-3.0-or-later)とPyPIパッケージ(`heretic-llm` 2.0.0、https://pypi.org/project/heretic-llm/ )である。
Zenn・Qiita・noteを検索した範囲では、このツールの一次検証記事(実際に動かして結果を載せた記事)は2026年11月2日時点で0件だった。
GIGAZINEなどのニュース解説記事はあるが、実行ログを伴う検証記事は見当たらなかった。

念のため先に書いておくと、この検証の目的は「アライメント(安全性調整)という仕組みがどれだけ脆いか」を定量的に確かめることであり、生成した無検閲モデルの出力そのものを見せることではない。
実際に改変後のモデルを保存・アップロードもしていない。

## Hereticという仕組み

Hereticは、Arditi et al. (2024) の「LLMの拒否挙動は内部の活性化空間のある単一方向に強く媒介されている」という知見をもとに、その方向を打ち消すようにモデルの重みを操作する(Abliteration、あるいはARA = Arbitrary-Rank Ablationという手法)ツールである。
「再学習なし」とはいっても、勾配によるファインチューニングをしないという意味であり、OptunaのTPE(ベイズ的な探索)で「拒否率」と「元モデルとの出力分布のKL発散」を同時に最小化するパラメータを探すループの中で、実際にモデルの重みを何度も書き換えて評価する。
既定ではこの探索を100試行繰り返す。

## 筆者の実行環境

- vCPU 4コア(Intel Xeon @2.10GHz)、RAM 15GB
- **GPUなし**(`nvidia-smi` コマンド自体が存在しない)

Heretic自身、起動時に次のように出力する。

```
No GPU or other accelerator detected. Operations will be slow.
```

READMEはGPU環境を前提に書かれているツールであることを、ツール自身が起動直後に認めている。

## インストールで一度詰まった

`pip install -U heretic-llm` をシステムのPython(Debianパッチ入りのsetuptoolsが入った環境)にそのまま実行すると、依存関係に含まれる古い`setup.py`ベースのパッケージ(`langdetect` `rouge-score` `sqlitedict` `word2number`。いずれも評価ライブラリ`lm-eval`の依存)のビルドに失敗した。

```
$ pip install -U heretic-llm
...
AttributeError: install_layout. Did you mean: 'install_platlib'?
...
ERROR: Could not build wheels for langdetect, rouge-score, sqlitedict, word2number, which is required to install pyproject.toml-based projects
```

これはHeretic自体のバグというより、システムPython側の古いsetuptoolsパッチとの相性問題である。
`python3 -m venv` で素のvenvを作り、その中のpip(setuptools新しめ)でやり直すと問題なくビルドできた。

```
$ python3 -m venv heretic-venv && source heretic-venv/bin/activate
$ pip install -U pip setuptools wheel -q
$ pip install -U heretic-llm   # 成功
```

## CLIの挙動と既定設定

`heretic --help` で全オプションを確認できる。
主要なものは、対象モデルを指定する`--model`、Optunaの試行数`--n-trials`(既定100)とランダム探索フェーズの数`--n-startup-trials`(既定30)、量子化方式`--quantization`(`none`か`bnb_4bit`)、1回の応答生成の最大トークン数`--max-response-length`(既定100)である。
`--trial-index`と`--model-action`を両方指定すると、本来は対話式(questionaryライブラリによる選択メニュー)の部分を飛ばして非対話実行できる。
今回は`--trial-index 0 --model-action ""`として、「Pareto最適な先頭の試行を選び、モデルを保存せず終了する」という非対話フローにした。

設定ファイル`config.default.toml`を読むと、既定では次の規模のデータを使うとわかる。

- バッチサイズ自動判定用プロンプト: 256件
- 応答プレフィックス自動判定用プロンプト: 200件(harmless/harmful各100)
- 拒否率評価用プロンプト: 100件(`mlabonne/harmful_behaviors`のテスト分割)
- KL発散評価用プロンプト: 100件(`mlabonne/harmless_alpaca`のテスト分割)
- ARA修正方式が参照する「望ましい/望ましくない」プロンプト: 各400件
- Optuna試行数: 100(うちランダム探索30)

## スモーク実行: 何を・どう縮小したか

既定設定(試行100回)をGPUなしでそのまま回すと6時間の作業枠を大きく超えると判断し、試行数と評価セットを大幅に縮小した「スモーク実行」を1モデルに対して1回実施した。
対象は、Qwen3シリーズで最小の密モデルである`Qwen/Qwen3-0.6B`である。
このモデルのチャットテンプレートには`<think></think>`というChain-of-Thoughtブロックがあり、Hereticはこれを自動検出して、評価の対象をその後の実際の応答部分に揃えていた。

縮小した項目は次のとおりである(ロジック自体、たとえば拒否判定のキーワードリストやARAのL-BFGS反復回数は既定のまま変更していない)。

| 項目 | 既定値 | 今回 |
|---|---|---|
| 試行数 `n_trials` | 100 | 2 |
| ランダム探索数 `n_startup_trials` | 30 | 2 |
| 最大応答長 `max_response_length` | 100 | 32 |
| 拒否率評価用プロンプト | 100件 | 10件 |
| KL発散評価用プロンプト | 100件 | 10件 |
| ARA good/badプロンプト | 各400件 | 各40件 |

## 実行結果

実行コマンドと実測時間は次のとおりである。

```
$ time timeout 1700 heretic --model Qwen/Qwen3-0.6B --trial-index 0 --model-action ""
...
real    4m8.361s
user    12m1.062s
sys     2m13.019s
EXIT:0
```

4 vCPU中、user時間がreal時間の約3倍になっており、3コア程度を使うマルチスレッド実行になっていたとわかる。

バッチサイズの自動判定では、バッチサイズを上げるとスループットがほぼ線形に伸びた。

```
* Trying batch size 1... Ok (14 tokens/s)
* Trying batch size 2... Ok (21 tokens/s)
* Trying batch size 4... Ok (37 tokens/s)
* Trying batch size 8... Ok (68 tokens/s)
* Chosen batch size: 8
```

未改変モデルのベースラインは、10件の有害な依頼プロンプトのうち2件(20%)が拒否ワードを含む応答になった。

```
* Baseline Refusals: 2/10
* Baseline KL divergence: 0 (by definition)
```

Optunaによる2回の試行結果は次のとおりである。

```
試行1: start_layer_index=8, end_layer_index=28, ...
  Refusals: 0/10 / KL divergence: 0.0994 / 所要 1分23秒

試行2: start_layer_index=6, end_layer_index=17, ...
  Refusals: 0/10 / KL divergence: 0.0295 / 所要(累積) 2分6秒(単体では約43秒)
```

2試行とも拒否率はベースラインの2/10から0/10まで下がった。
試行2は、修正対象のレイヤー数が試行1より少なく(28-8=20層に対して17-6=11層)、その分だけ速く(43秒対83秒)、かつKL発散も試行1の1/3程度(0.0295対0.0994)に抑えられていた。
つまり試行2は、速度・拒否率・元モデルからの逸脱の小ささのすべてで試行1より優位な結果になっており、`--trial-index 0`で自動選択されるPareto最適解の先頭に試行2が来たことも、この結果と整合している。

ただし試行数2回・評価プロンプト10件というのは既定のそれぞれ1/50、1/10の規模であり、「Optunaのベイズ的探索が本来の100試行規模で何を見つけるか」を検証したものではない。
あくまで「この仕組みが実際に動き、拒否率とKL発散の数値がどのように変化するか」を確認するための実行である。

## 既定設定(試行100回)はCPUでどれくらいかかるのか

実測した縮小設定の内訳から、既定設定に戻した場合の所要時間を見積もってみる。
試行時間の大半(試行1では83秒中70秒程度)を占めていたのは、ARAによるモデル修正ステップだった。
このステップが参照するgood/badプロンプトを40件から400件(既定)に戻すと、L-BFGSの計算量はデータ量にほぼ比例して増えるため、1試行あたり十数分規模に増えると見積もれる。
評価ステップも、拒否率評価用プロンプトを10件から100件(10倍)、応答長を32トークンから100トークン(3.125倍)に戻すと、ラフに30倍前後に増えると見積もれる。
これらを足し合わせると、1試行あたりの所要時間は既定設定で15分前後、100試行では**約25時間**という推定になる。
これはREADMEに記載のRTX 3090での既定実行(30〜40分)の40倍前後にあたる。
この推定はあくまで今回の実測値からの外挿であり、実際に100試行を走らせて確認したものではないが、6時間という作業枠には到底収まらないと判断できる数字である。

## まとめ

Hereticは、GPUがなくても最後まで完走する(ツール自身は想定していないと明言しつつも、CPUでエラーなく動いた)。
ただしスループットは実測で14〜68 tokens/s(バッチサイズ1〜8、0.6Bモデル、4 vCPU)にとどまり、既定の試行規模をそのまま回すには推定25時間という計算になった。
一方で、試行数と評価セットを大幅に縮小したスモーク実行でも、Abliteration理論(内部活性化空間のある方向を操作するだけで拒否挙動を抑制できるという考え方)が小規模なモデル・小規模な評価セットでも再現されることは確認できた。
ベースラインで2/10だった拒否率は、2試行ともで0/10まで下がり、Optunaはわずか2試行の中でも「拒否率を維持したままKL発散(元モデルからの逸脱)を1/3程度に抑える」パラメータをより優れた解として見つけていた。

「安全性のアラインメントは、方向を1つ潰すだけで崩れるほど薄い層でしかないのかもしれない」ということを、自分の手で、しかもGPUなしの環境でも数値として確認できたのは収穫だった。
一方で、今回の評価セットは10件というごく小さな規模であり、これをもって「Hereticが安全に・一般的に拒否挙動を外せる」と結論づけることはできない点は強調しておきたい。
