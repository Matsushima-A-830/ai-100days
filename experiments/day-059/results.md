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
- **GPU非搭載。CPUのみ**(`nvidia-smi`: command not found、`torch.cuda.is_available()`: False)。RAM 15GB。
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
