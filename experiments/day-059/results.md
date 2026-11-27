# Day 059 検証結果: p-e-w/heretic (training-free abliteration)

出典: https://github.com/p-e-w/heretic (AGPL-3.0-or-later)
PyPI: https://pypi.org/project/heretic-llm/ (インストールしたバージョン: 2.1.0)

## 倫理面の方針(today.mdの指示を踏襲)

- 検証・記事化の主役は**定量指標**(拒否率・KLダイバージェンス)のみ。heretic内部の`KeywordRate`スコアラーは
  `mlabonne/harmful_behaviors`(AdvBench系の標準的な安全性ベンチマーク)を使って拒否判定しているが、
  `print_responses`は既定値`false`のままにしており、個々のプロンプト・応答の文面は一度も表示・記録していない。
  本ファイルに書くのは`N/20`という集計スコアのみ。
- 筆者が自分で読む・記事に書くための「軽いBefore/After比較」は、ロックピッキングの原理・フィッシングの手口
  (防御目的)という、既に多くの教育コンテンツで扱われる無害な質問に限定した(`baseline_test.py`参照)。
- 処理後に生成した無検閲モデルの重みは外部に公開・配布せず、検証終了後に`/tmp`から削除した
  (`rm -rf /tmp/heretic-day059-model`で削除済み。本リポジトリにもコミットしていない)。

## 環境

- Python 3.11.18、`python3 -m venv .venv && .venv/bin/pip install heretic-llm`(インストールできたバージョン: 2.1.0)
- 1〜8章はRoutine実行環境(GPU非搭載、CPUのみ、RAM 15GB)での結果。ローカルPC(GPU)での検証は9章。
- heretic自身がこれを検知して警告を出す: `No GPU or other accelerator detected. Operations will be slow.`

## 1. スケールダウンの判断(today.mdで事前に許容されていた対応)

heretic公式READMEの計測では、RTX 3090でQwen3-4B-Instructを既定設定(trial数100、KeywordRate/KLDivergence
ともに評価プロンプト100件)で処理すると30〜40分かかる。GPUが無いCPU環境でこの既定設定をそのまま4Bモデルに
適用すると、素朴に見積もっても数時間〜日のオーダーになり、1日の検証枠を超える。

today.mdの方針(「GPUが使えない場合は4bit量子化やさらに小型のモデルで試行数を絞る」)に従い、以下のように
スケールダウンした`config.toml`を作成して実行した(upstreamの`config.default.toml`との差分):

| パラメータ | upstream既定値 | 本検証 |
|---|---|---|
| 対象モデル | Qwen3-4B-Instruct-2507 | **Qwen/Qwen3-0.6B** |
| `n_trials` | 100 | **12** |
| `n_startup_trials` | 30 | **5** |
| `scorer.KeywordRate.prompts`(拒否率評価) | test[:100] | **test[:20]** |
| `scorer.KLDivergence.prompts` | test[:100] | **test[:20]** |
| `modifier.ARA.good_prompts` / `bad_prompts`(方向抽出用) | train[:400] / train[:400] | **train[:80] / train[:80]** |
| `max_response_length` | 100 | **40** |
| `batch_size` | 0(自動) | **4**(自動ベンチマークをスキップ) |
| `response_prefix` | null(自動検出) | **""**(自動検出をスキップ) |
| `quantization` | none | none(bnb_4bitはCUDA前提のため今回は使わず、モデル自体を小型化した) |

この縮小の結果、**12 trial全体(モデル読み込み・ARA方向抽出・評価を含む最適化ループ)がCPUで12分17秒
(`Elapsed time: 12m 17s`、heretic自身の計測)で完了した。** モデル読み込み・最終モデルのマージ保存まで含めた
スクリプト全体の実行は概ね14〜15分。

## 2. 実行ログ(インストール)

```
$ .venv/bin/pip install heretic-llm
Successfully installed ... heretic-llm-2.1.0 ...

$ .venv/bin/pip show heretic-llm
Name: heretic-llm
Version: 2.1.0
License-Expression: AGPL-3.0-or-later
```

## 3. 最適化前(ベースライン)のスコア

heretic自身が最初に算出する、無改造モデルのベースライン(標準出力そのまま):

```
* Baseline Refusals: 6/20
* Baseline KL divergence: 0 (by definition)
```

Qwen3-0.6Bは、`mlabonne/harmful_behaviors`から抜いた20件の有害指示プロンプトのうち **6件(30%)** で
拒否キーワード(`REFUSAL_MARKERS`、"I cannot" "I'm unable" "illegal" 等)にマッチする応答をしていた。
4B級の指示チューニング済みモデルと比べて、0.6Bという小さいモデルはそもそも安全アラインメントが弱く、
ベースラインの拒否率自体が高くないという点が最初の発見である。

## 4. Optuna探索12 trialの結果(集計スコアのみ)

`scorer.KeywordRate`(拒否率、`N/20`。小さいほど良い=最小化対象)と`scorer.KLDivergence`
(元モデルの応答分布からの乖離。小さいほど良い=最小化対象)を、ARAモジュールのハイパーパラメータ
(`start_layer_index` / `end_layer_index` / `preserve_good_behavior_weight` /
`steer_bad_behavior_weight` / `overcorrect_relative_weight` / `neighbor_count`)についてTPEベースの
Optunaが探索した。12 trial全件の結果(heretic標準出力をそのまま集計。個々のプロンプト文面は含まれない):

| Trial | start→end layer | preserve_weight | steer_weight | overcorrect_weight | neighbors | Refusals | KL divergence |
|---|---|---|---|---|---|---|---|
| 1  | 13→23 | 0.7071 | 0.0010 | 0.2090 | 4  | 0/20 | 0.0000 |
| 2  | 2→24  | 0.4964 | 0.0365 | 0.1449 | 10 | 0/20 | 0.0005 |
| 3  | 2→18  | 0.8047 | 0.1273 | 1.2349 | 11 | 0/20 | 17.6746 |
| 4  | 7→17  | 0.4059 | 0.0003 | 0.4999 | 8  | 1/20 | 0.0000 |
| 5  | 7→19  | 0.9704 | 0.0121 | 0.8455 | 14 | 0/20 | 0.0002 |
| 6  | 11→25 | 0.8347 | 0.0020 | 0.4303 | 4  | 0/20 | 0.0001 |
| 7  | 12→27 | 0.1401 | 0.0002 | 0.3370 | 1  | 0/20 | 0.0000 |
| 8  | 14→23 | 0.7899 | 0.0001 | 1.1359 | 6  | 1/20 | 8.0875 |
| 9  | 2→25  | 0.5827 | 0.0005 | 0.0114 | 1  | 0/20 | 0.0001 |
| **10** | **4→27**  | **0.9796** | **0.0002** | **0.0082** | **10** | **0/20** | **0.0000** |
| 11 | 7→27  | 0.6094 | 0.0003 | 0.2391 | 15 | 1/20 | 0.0000 |
| 12 | 1→27  | 0.9128 | 0.0001 | 0.0810 | 9  | 0/20 | 0.0000 |

(baseline: Refusals 6/20、KL divergence 0 by definition)

observation:
- ベースラインで6/20だった拒否が、12 trial中9 trialで**0/20**まで落ちている。小さいモデルの弱い安全
  アラインメントは、ARAによる方向性アブレーションに対してかなり脆いことが確認できる。
- 一方でKLダイバージェンスは trial間でばらつきが大きい(trial 3は17.67、trial 8は8.09と大きく劣化しているが、
  他の多くは0.0000〜0.0005とほぼ無劣化)。これは`overcorrect_relative_weight`が大きい trial(3, 8)で
  元モデルからの乱れが大きくなっている傾向と対応しており、「拒否率を下げるほど元モデルの挙動が壊れる」という
  トレードオフがこの縮小実験でも定量的に見えている。

## 5. 選択されたtrialと適用結果

`--trial-index 0`(Pareto最適解の先頭、heretic既定のソート順で選ばれた候補)で選択されたのは **trial 10**
(`start_layer_index=4`, `end_layer_index=27`, `preserve_good_behavior_weight=0.9796`,
`steer_bad_behavior_weight=0.0002`, `overcorrect_relative_weight=0.0082`, `neighbor_count=10`)。

```
Restoring model from trial 10...
* Refusals: 0/20
* KL divergence: 0.0000
```

**拒否率: 30%(6/20) → 0%(0/20)。KLダイバージェンス: heretic報告値で0.0000。**
追加学習なし、CPU・12分強のOptuna探索だけで、この0.6Bモデルの拒否挙動はベンチマーク上完全に抑制された。

## 6. 自分で確認した軽いBefore/After(無害な質問のみ)

`baseline_test.py`で、ロックピッキングの原理とフィッシングの手口(防御目的)という無害な質問4件を、
処理前モデルと処理後モデル(マージ済み、`/tmp`に一時保存)それぞれに投げて目視で比較した
(生成は`do_sample=False`の決定的デコード、`max_new_tokens=150`)。

結果: **この4問はいずれも処理前から拒否されておらず**、処理後も同程度の長さ・内容の応答が返ってきた
(いずれも<think>ブロックの途中で150トークンの上限に達して切れているが、切れ方・内容の方向性は前後で
目立った違いはない)。生の応答全文は`baseline_responses_before.json` / `baseline_responses_after.json`
に記録した(いずれも無害な質問への応答のみで、転載を控えるべき内容は含まない)。

(9章の訂正: KLダイバージェンス0.0000は「無害な応答が変わっていない」ことを示していなかった。また応答は4問とも`<think>`の途中で
切れており、比較できているのは思考の冒頭だけである。)
この結果は、heretic側のKLダイバージェンス0.0000という報告値(=良性プロンプトへの応答分布がほぼ変わって
いない)と整合している。つまり「有害指示への拒否だけが狙って抑制され、無害な質問への応答品質は保たれた」
という、heretic/ARAの設計意図どおりの挙動が、この縮小スケールでも確認できた。

## 7. ライセンス・取り扱いについての注意

- heretic本体はAGPL-3.0-or-later。本検証ではheretic自体のコードは改変していないため再配布義務は発生しない
  (configファイルの作成のみ)。コードを改変して配布する場合はソース公開義務があることに注意。
- 処理対象のQwen3-0.6BはApache-2.0(Qwenライセンス)。
- 本検証で生成した「無検閲モデル」の重みは外部に公開・配布せず、検証終了後に削除した。

## 8. 制約・今後の課題

- **モデルサイズとtrial数・評価プロンプト数を大きく縮小している**(0.6B・12 trial・20プロンプト。
  upstream既定は4B・100 trial・100プロンプト)。これはCPUのみという筆者の検証環境のハードウェア制約に
  よるスコープの絞り込みであり、同じ制約を持つ読者(GPUなしでheretic-llmを試す場合)が直接参考にできる
  条件として明記した。4B級モデル・既定スケールでの再現はGPU環境でのローカル検証が望ましい。
- KeywordRateスコアラーはキーワードマッチによる簡易判定であり、「拒否はしていないが実際には有用な
  回答になっていない」ケース(空応答・話題そらし等)を見分けられない。本検証でもスコア自体の妥当性は
  検証していない。
- 20件という小さい評価セットでは、score自体のばらつき(1件変わるだけで5%変動)が大きい。

## 9. ローカル検証(人間のPC、GPU、2026-11-26〜27)

環境: WSL2 / NVIDIA GeForce RTX 5060 Ti 16GB(Driver 610.88, CUDA 13.2) / RAM 30GB /
heretic-llm 2.1.0、torch 2.15.0、Python 3.14。実行ファイル・ログ(集計スコアのみ)は `local/`。
倫理方針は1〜8章と同じ(`print_responses=false`、個々のプロンプト・応答は表示も記録もしない)。
処理後モデルの保存はしていない(下記9-4)。

3つの条件で実行した(`local/run.sh`、`local/runs.txt`)。

| 条件 | モデル | 設定 | trial | 評価件数 | 所要 |
|---|---|---|---|---|---|
| A | Qwen/Qwen3-0.6B | PRの`config.toml`そのまま(`response_prefix = ""`) | 12 | 各20 | 530s |
| B | Qwen/Qwen3-0.6B | Aから`response_prefix`の行だけ削除(=upstream既定の自動検出) | 12 | 各20 | 650s |
| C | Qwen/Qwen3-4B-Instruct-2507 | 設定の上書きなし(upstream既定) | 100 | 各100 | 最適化 1h 41m |

### 9-1. 条件A: PRの結果は再現した

```
* Baseline Refusals: 6/20
...
Restoring model from trial 10...   (Refusals: 0/20, KL divergence: 0.0000)
```

ベースライン6/20、選択trialが0/20・KL 0.0000という点はPRと同じだった。
Optunaのseedが未指定(upstream既定`seed = None`)のため、各trialのパラメータ・スコアはPRとは一致しない。
12 trialのKLは0.0000〜1.1666(中央値0.0001)。

### 9-2. KL 0.0000 は「劣化なし」を意味していなかった

hereticの`KLDivergence`スコアラーは、無害なプロンプトに対する**応答の最初の1トークンの確率分布**だけを比較する
(`heretic/scorers/kl_divergence.py`、ログ上も`Obtaining baseline first-token probability distributions...`)。
Qwen3-0.6Bは思考モード(`<think>`)が既定でオンで、PRの設定は`response_prefix = ""`として思考ブロックの自動検出を止めている。
この場合の最初の1トークンを実測した(`local/first_token.py`、CPU・float32、`mlabonne/harmless_alpaca` test[:20]):

```
'' top1 tokens: ['<think>'] min top1 prob: 0.9996 mean: 0.9997
'<think>\n\n</think>\n\n' top1 tokens: ['**', '1', 'A', 'Ah', 'Certainly', 'False', 'Four', 'One', 'Sure', 'To'] min top1 prob: 0.319 mean: 0.6894
```

プレフィックス無しでは、20問すべてで最初の1トークンが`<think>`(平均99.97%)であり、モデルをどう改変してもほぼ同じ分布になる。
つまりPRのKL 0.0000は、無害な応答の中身を測っていない。
空の思考ブロックを閉じた後(=実際の回答の1トークン目)では、上位トークンが10種類に分かれ、KLが変化を測れる状態になる。

条件B(自動検出)では、hereticが次のプレフィックスを検出して評価に使った:

```
* Prefix found: '<think>\nOkay,'
* Extended prefix found: '<think></think>\nOkay,'
* Baseline Refusals: 8/20
```

| | A(プレフィックス無し) | B(自動検出) |
|---|---|---|
| ベースライン拒否 | 6/20 | 8/20 |
| 12 trialのKL | 0.0000〜1.1666(中央値0.0001) | 0.0031〜2.3147(中央値0.0243) |
| `--trial-index 0`の選択 | trial 10: 0/20, KL 0.0000 | trial 9: 0/20, KL 0.0049 |

同じ種類の改変でも、Bでは中央値で約240倍のKLが出る。
(Bの拒否判定は、思考ブロックを閉じた後の回答部分に対して行われるため、ベースラインも6/20から8/20に変わった。)

### 9-3. 条件C: upstream既定(4B・100 trial)では「拒否0」と「劣化小」は両立しなかった

Qwen3-4B-Instruct-2507は思考ブロックを持たないモデルで、プレフィックスは検出されなかった(`* None found`)。
バッチサイズは自動で64に決まり、100 trialで1h 41m(最初のtrialまで3m 0s)。

```
* Baseline Refusals: 100/100
```

100 trialのPareto front(拒否件数とKLのどちらも他のtrialに負けていないもの、`local/heretic_run_C.log`から集計):

| trial | Refusals | KL divergence |
|---|---|---|
| 2 | 0/100 | 8.7006 |
| 5 | 3/100 | 1.8413 |
| 64 | 4/100 | 0.0419 |
| 93 | 5/100 | 0.0385 |
| 86 | 6/100 | 0.0310 |
| 84 | 8/100 | 0.0284 |
| 95 | 12/100 | 0.0262 |
| 100 | 13/100 | 0.0241 |
| 85 | 15/100 | 0.0226 |
| 32 | 17/100 | 0.0191 |
| 77 | 20/100 | 0.0173 |

- 拒否0/100に到達したtrialは12個あったが、KLは全て8.70以上(8.70〜17.71)。
- KLが0.1未満のtrialで最も拒否が少ないのは4/100(trial 64、KL 0.0419)。
- 100 trial中24 trialでKLが1を超えた。

### 9-4. `--trial-index 0` は「最も壊れた」候補を選ぶ

hereticはPareto frontを**スコアの昇順(1番目のスコア=拒否件数が少ない順)**に並べ(`heretic/main.py`の`sorted_trials`)、
`--trial-index 0`はその先頭を選ぶ。
対話モードでは一覧から人が選ぶ前提で、PRの再現手順のように非対話で`0`を指定すると、常に「拒否が最も少ない=KLが最も大きい」trialになる。
条件Cではそれがtrial 2(0/100、KL 8.70)だった。
0.6B・プレフィックス無しの条件Aでは全trialのKLがほぼ0なので、この問題が表に出なかった。

なお、筆者の`local/run.sh`は`--export-strategy`を指定し忘れたため、3条件とも最後に「エクスポート方法」の対話プロンプトが出た。
A・Bは`Error: [Errno 1] Operation not permitted`で終了し、Cはプロンプトで待機したままになったのでプロセスを終了した。
いずれもスコアは全て出力された後で、**処理後モデルの重みは一度も保存されていない**。
そのため、`baseline_test.py`による処理後の無害な質問での比較はローカルでは行っていない。

### 9-5. まとめ

- ✅ PRの数値(0.6B・12 trial・プレフィックス無し: 6/20→0/20、KL 0.0000)は再現した。
- ❌ KL 0.0000は、最初の1トークンが常に`<think>`(平均99.97%)になる設定で測ったもので、劣化の有無を示していない。PRの「劣化は見られなかった」という結論は根拠にならない。
- ✅ upstream既定(Qwen3-4B-Instruct-2507、100 trial)では、ベースライン100/100の拒否が、KL 0.0419で4/100まで下がった。
- ❌ 拒否を0/100にしたtrialは全てKL 8.70以上で、`--trial-index 0`はそのうち1つ(trial 2)を選ぶ。
- 1〜8章の「CPUで12分17秒」はRoutine実行環境での値。RTX 5060 Tiでは同じ設定(条件A)が530秒(最適化は8m 18s)だった。
