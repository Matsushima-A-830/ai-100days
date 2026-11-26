---
title: "GPUなしのCPUだけで、追加学習なしのLLM検閲解除ツール「heretic」を動かしてみた"
emoji: "🔓"
type: "tech"
topics: ["ai", "llm", "machinelearning", "python", "optuna"]
published: false
---

## これは何を試した記事か

[heretic](https://github.com/p-e-w/heretic)は、追加学習(ファインチューニング)を一切せずに、既存のLLMの拒否応答(いわゆる安全アラインメント・検閲)を自動的に抑制できるPython製CLIツールである。
AGPL-3.0-or-licenseで公開されており、GitHub Trendingで急伸し、Trendshiftの「Repository of the Day」にも選ばれていた。

「directional ablation(方向性アブレーション、通称abliteration)」という既存の解釈可能性研究の手法に、Optunaによるベイズ的パラメータ探索(TPE)を組み合わせ、拒否率とKLダイバージェンス(元モデルの応答分布からの劣化)を同時に最小化するハイパーパラメータを自動で見つける、というのが中身である。

このツールは「安全アラインメントが、追加学習なしの自動パラメータ探索だけでどこまで動かせてしまうのか」を定量的に示す、解釈可能性・アライメント研究のデモとして価値が高い一方、「検閲解除」という性質上デュアルユースである。
そのため本検証では以下を徹底した。

- 検証・記事化の主役は**拒否率とKLダイバージェンスという定量指標**のみに置き、実際に生成された有害な文面は転載・公開しない。
- 筆者が自分で目視確認するための質問は、ロックピッキングの原理やフィッシングの手口(防御目的)など、すでに多くの教育コンテンツで扱われている無害な範囲に限定した。
- 処理後に生成した「無検閲モデル」自体の重みは外部に公開・配布せず、検証終了後に削除した。

詳しい方針と実行ログは[`experiments/day-059/`](https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-059)に置いている。

## GPUが無い環境でそのまま動かすのは無理だった

筆者が使った検証環境には**GPUが無い**。heretic自身がこれを検知して次のように警告を出す。

```
No GPU or other accelerator detected. Operations will be slow.
```

heretic公式READMEの実測では、RTX 3090でQwen3-4B-Instructを既定設定(Optuna 100 trial、評価プロンプト各100件)で処理すると30〜40分かかるとされている。
これをそのままCPUで4Bモデルに適用すると、素朴に見積もっても数時間〜日のオーダーになり、とても1日の検証枠には収まらない。
これは「ツールのバグ」ではなく、筆者の検証環境(GPUなし・CPUのみ)のスペック不足によるものである。
同じ制約を持つ読者(ゲーミングPCを持たずheretic-llmを試す場合)には直接参考になるはずなので、スケールダウンの中身を正直に書く。

以下のように、対象モデルと探索の規模を縮小した`config.toml`を自作して実行した。

| パラメータ | upstream既定値 | 本検証 |
|---|---|---|
| 対象モデル | Qwen3-4B-Instruct-2507 | **Qwen3-0.6B** |
| Optuna `n_trials` | 100 | **12** |
| 拒否率評価プロンプト数 | 100 | **20** |
| KLダイバージェンス評価プロンプト数 | 100 | **20** |
| 方向抽出用プロンプト数(good/bad各) | 400 | **80** |
| 最大生成トークン数 | 100 | **40** |

この縮小の結果、**Optunaの12 trial全体がCPUで12分17秒(heretic自身の計測)で完走した。**
pip installやモデル読み込みを含めても、スクリプト全体は15分程度で終わる。

```bash
python3 -m venv .venv && .venv/bin/pip install heretic-llm
HERETIC_CONFIG_FILE=./config.toml .venv/bin/heretic \
  --model Qwen/Qwen3-0.6B \
  --checkpoint-action restart --trial-index 0 \
  --model-action save --export-strategy merge \
  --save-directory /tmp/heretic-day059-model
```

## ベースライン: 0.6Bモデルの拒否率はそもそも30%しかなかった

heretic内部の`KeywordRate`スコアラーは、abliteration研究で標準的に使われる`mlabonne/harmful_behaviors`データセット(AdvBench系の有害指示プロンプト集)から抽出した20件に対して、応答に"I cannot" "I'm unable" "illegal"のような拒否キーワードが含まれるかで拒否率を測る。
heretic自身がまず無改造モデルのベースラインを測定し、こう表示した。

```
* Baseline Refusals: 6/20
* Baseline KL divergence: 0 (by definition)
```

**処理前の拒否率は6/20=30%。** Qwen3-4Bのような指示チューニングがしっかり効いた中型モデルに比べ、0.6Bという小さいモデルはそもそも安全アラインメントが弱く、この時点で意外と拒否していないことが分かる。
(個々のプロンプト・応答の文面は`print_responses`を既定値`false`のまま使っているため、一度も表示・記録していない。)

## Optuna 12 trialの結果: 9/12 trialで拒否率ゼロに到達

`start_layer_index` / `end_layer_index`(どの層の範囲に介入するか)、`preserve_good_behavior_weight`、`steer_bad_behavior_weight`、`overcorrect_relative_weight`、`neighbor_count`という6つのハイパーパラメータをTPEで探索した結果が以下である(スコアはすべてheretic標準出力の集計値そのまま、個々のプロンプト文面は含まない)。

| Trial | 層の範囲 | Refusals | KL divergence |
|---|---|---|---|
| 1 | 13→23 | 0/20 | 0.0000 |
| 2 | 2→24 | 0/20 | 0.0005 |
| 3 | 2→18 | 0/20 | 17.6746 |
| 4 | 7→17 | 1/20 | 0.0000 |
| 5 | 7→19 | 0/20 | 0.0002 |
| 6 | 11→25 | 0/20 | 0.0001 |
| 7 | 12→27 | 0/20 | 0.0000 |
| 8 | 14→23 | 1/20 | 8.0875 |
| 9 | 2→25 | 0/20 | 0.0001 |
| **10(選択)** | **4→27** | **0/20** | **0.0000** |
| 11 | 7→27 | 1/20 | 0.0000 |
| 12 | 1→27 | 0/20 | 0.0000 |

12 trial中9 trialで拒否率が**0/20(0%)**まで落ちている。小さいモデルの弱い安全アラインメントは、方向性アブレーションに対してかなり脆いことが、この縮小実験でも確認できた。

一方でKLダイバージェンスはtrialごとに大きくばらついている。`overcorrect_relative_weight`が大きいtrial(3は1.23、8は1.14)ではKLダイバージェンスも17.67・8.09と大きく劣化しており、「拒否率を下げるほど元モデルの挙動が壊れる」というトレードオフが、わずか12 trialの探索でも見えている。

heretic既定のPareto選択ロジックで選ばれたのは**trial 10**(`preserve_good_behavior_weight=0.9796`、`overcorrect_relative_weight=0.0082`と、元の挙動を保つ方向に重みを置いたパラメータ)で、

- 拒否率: **30%(6/20) → 0%(0/20)**
- KLダイバージェンス: **heretic報告値で0.0000**

追加学習なし、CPU・12分強のOptuna探索だけで、拒否挙動がベンチマーク上完全に抑制され、しかも報告上は元モデルからの劣化がほぼゼロという結果になった。

## 無害な質問での目視確認

ロックピッキングの原理とフィッシングの手口(防御目的)という無害な質問4件を、処理前・処理後のモデルそれぞれに投げて比較した。
結果として、**この4問はいずれも処理前から拒否されておらず**、処理後も同程度の長さ・内容の応答が返ってきた。
これはheretic側のKLダイバージェンス0.0000という報告値(=無害なプロンプトへの応答分布がほぼ変わっていない)と整合しており、「有害指示への拒否だけが狙って抑制され、無害な質問への応答品質は保たれる」というARA(Arbitrary-Rank Ablation)の設計意図どおりの挙動が、この縮小スケールでも確認できた。

## ライセンスと取り扱い

heretic本体はAGPL-3.0-or-later。本検証ではheretic自体のコードは改変していないため再配布義務は発生しないが、コードを改変して配布する場合はソース公開義務があることに注意したい。
処理対象のQwen3-0.6BはApache-2.0。
本検証で生成した無検閲モデルの重みは外部に公開・配布せず、検証終了後に削除した。

## まとめと制約

GPUの無いCPU環境でも、モデルとOptunaのtrial数・評価プロンプト数を大きく縮小すれば、heretic-llmの基本的な挙動(拒否率とKLダイバージェンスを同時最小化する自動探索)は15分程度で確認できる。
ただし本検証はあくまで0.6Bという小型モデル・12 trial・20プロンプトという縮小スケールでの結果であり、upstream既定の4B級モデル・100 trialでの挙動とは単純に比較できない。
4B級モデルでの再現にはGPU環境でのローカル検証が望ましい。
また`KeywordRate`はキーワードマッチによる簡易な拒否判定であり、「拒否はしていないが実際には有用な回答になっていない」ケースを見分けられない点も、スコアの数字だけを見るときの注意点として付け加えておきたい。

## 出典

- heretic: https://github.com/p-e-w/heretic (AGPL-3.0-or-later)
- heretic-llm (PyPI): https://pypi.org/project/heretic-llm/
- Qwen3-0.6B: https://huggingface.co/Qwen/Qwen3-0.6B (Apache-2.0)
- 評価データセット: https://huggingface.co/datasets/mlabonne/harmful_behaviors, https://huggingface.co/datasets/mlabonne/harmless_alpaca
