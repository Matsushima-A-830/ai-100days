---
title: "検閲解除ツールhereticの「KL 0.0000」は劣化ゼロではなかった: Qwen3の<think>が指標を素通りさせていた"
emoji: "🔓"
type: "tech"
topics: ["ai", "llm", "machinelearning", "python", "optuna"]
published: false
---

## これは何を試した記事か

[heretic](https://github.com/p-e-w/heretic)は、追加学習なしで既存のLLMの拒否応答(安全アラインメント)を抑制するPython製CLIツールである(AGPL-3.0-or-later)。
方向性アブレーション(abliteration)という解釈可能性研究の手法に、OptunaのTPE探索を組み合わせ、「拒否率」と「KLダイバージェンス(元モデルからのズレ)」を同時に小さくするパラメータを自動で探す。

筆者は[Day 036の記事](https://zenn.dev/matsushima_a/articles/day-036-heretic-abliteration-cpu-smoke-test)でもhereticを試し、upstream既定(Qwen3-4B-Instruct-2507、100 trial)で「拒否を0にすること」と「元モデルからのズレを小さくすること」が強いトレードオフにあることを見た。
今回はその続きとして、小さいモデル(Qwen3-0.6B)と縮小した設定で走らせたところ、**拒否率6/20→0/20、KLダイバージェンス0.0000**という、劣化なしで拒否だけが消えたように見える結果が出た。
記事にする前にこの「0.0000」を疑って調べると、指標が劣化を測っていなかったことが分かった。

検閲解除という性質上デュアルユースのツールなので、本検証では次を守った。

- 記事に書くのは拒否率とKLダイバージェンスという集計値だけにし、有害な指示への応答の文面は表示も記録もしない(heretic既定の`print_responses = false`のまま)。
- 処理後のモデルの重みは保存も公開もしない。

## 最初の結果: 拒否が消えて、劣化はゼロに見えた

対象はQwen/Qwen3-0.6B(Apache-2.0)で、upstream既定から規模を縮小した`config.toml`を使った。

| パラメータ | upstream既定値 | 本検証 |
|---|---|---|
| 対象モデル | Qwen3-4B-Instruct-2507 | **Qwen3-0.6B** |
| Optuna `n_trials` | 100 | **12** |
| 拒否率・KLの評価プロンプト数 | 各100 | **各20** |
| 最大生成トークン数 | 100 | **40** |
| `response_prefix` | 自動検出 | **`""`(空文字列で固定)** |

```bash
python3 -m venv .venv && .venv/bin/pip install heretic-llm==2.1.0
HERETIC_CONFIG_FILE=./config.toml .venv/bin/heretic --model Qwen/Qwen3-0.6B \
  --checkpoint-action restart --trial-index 0 --model-action save --save-directory ./model
```

`--export-strategy`を指定していないので、最適化の後はエクスポート方法を尋ねる対話で止まり、重みは保存されない(スコアはそれまでに全て出力される)。
RTX 5060 Ti(16GB)で、12 trialの最適化は8分18秒で終わった。

```
* Baseline Refusals: 6/20
* Baseline KL divergence: 0 (by definition)
...
Restoring model from trial 10...   (Refusals: 0/20, KL divergence: 0.0000)
```

12 trialのKLは0.0000〜1.1666で、中央値は0.0001だった。
ほとんどのtrialで、拒否を消しながら元モデルからのズレは測れないほど小さい、という結果である。
Day 036で同じ0.6Bを縮小設定で回したときはKLが0.03〜0.1程度だったので、この差が気になった。

## KLは「最初の1トークン」しか見ていない

hereticの`KLDivergence`スコアラーのソース(`heretic/scorers/kl_divergence.py`)を読むと、比べているのは無害なプロンプトに対する**応答の最初の1トークンの確率分布**だけである。
実行ログにも`Obtaining baseline first-token probability distributions...`と出ている。

最初の1トークンだけで比べるのは、普通のモデルなら妥当な近似である。
回答の書き出し(「Sure」「To」「1.」など)はプロンプトごとに分かれるので、モデルを壊せばその分布が動く。

ところがQwen3-0.6Bは思考モードが既定でオンで、応答は必ず`<think>`から始まる。
hereticには本来、この思考ブロックを自動で検出し、閉じた`<think></think>`の後ろ(=実際の回答の書き出し)で評価する仕組み(`response_prefix`の自動検出)がある。
今回の設定は`response_prefix = ""`として、この自動検出を止めていた。

実際に、無害なプロンプト20件で、改変していないQwen3-0.6Bの最初の1トークンを調べた。

```
$ python first_token.py
'' top1 tokens: ['<think>'] min top1 prob: 0.9996 mean: 0.9997
'<think>\n\n</think>\n\n' top1 tokens: ['**', '1', 'A', 'Ah', 'Certainly', 'False', 'Four', 'One', 'Sure', 'To'] min top1 prob: 0.319 mean: 0.6894
```

プレフィックス無しでは、20問すべてで最初の1トークンが`<think>`で、確率は平均99.97%だった。
重みをどう書き換えても、「次は`<think>`」という予測はほとんど動かないので、KLは0近くに張り付く。
空の思考ブロックを閉じた後では、上位のトークンが10種類に分かれ、確率も平均69%まで下がる。
こちらなら、モデルが壊れたときに分布が動く。

## 自動検出に戻すと、KLは動き出した

`config.toml`から`response_prefix = ""`の1行だけを削除し、upstream既定の自動検出に戻して、同じ12 trialを回した。

```
* Prefix found: '<think>\nOkay,'
* Extended prefix found: '<think></think>\nOkay,'
* Baseline Refusals: 8/20
```

| | プレフィックス無し(元の設定) | 自動検出 |
|---|---|---|
| ベースライン拒否 | 6/20 | 8/20 |
| 12 trialのKL | 0.0000〜1.1666(中央値0.0001) | 0.0031〜2.3147(中央値0.0243) |
| `--trial-index 0`の選択 | 0/20、KL 0.0000 | 0/20、KL 0.0049 |

同じ種類の改変でも、自動検出ではKLの中央値が約240倍になった。
Day 036の0.6BのKL(0.03〜0.1程度)とも桁が合う。
ベースラインの拒否が6/20から8/20に変わったのは、拒否の判定が思考の冒頭ではなく回答の部分に対して行われるようになったためである。

元の設定には、無害な質問4問で処理前後の応答を見比べ、劣化が無いことを確かめた、という確認も付いていた。
しかしその応答は8件とも`<think>`の途中で150トークンの上限に達して切れており、比べられていたのは思考の書き出しだけだった。
KL 0.0000と合わせて「劣化は見られなかった」と書くと、二重に根拠の無い結論になるところだった。

## `--trial-index 0`は「最も拒否が少ない」trialを選ぶ

もう一つ、非対話で実行するときに使う`--trial-index 0`の意味も確かめた。
hereticは最適化の後、Pareto front(拒否件数とKLのどちらも他に負けていないtrial)を並べて、どれを使うか人に選ばせる。
ソース(`heretic/main.py`の`sorted_trials`)では、この一覧はスコアの昇順、つまり1番目のスコアである**拒否件数が少ない順**に並ぶ。
したがって`--trial-index 0`は、常に「拒否が最も少ない=KLが最も大きい」trialを選ぶ。

0.6B・プレフィックス無しの設定ではKLがどれもほぼ0なので、この性質は表に出なかった。
upstream既定のQwen3-4B-Instruct-2507、100 trialで回すと、はっきり見える。

```
* Baseline Refusals: 100/100
...
Elapsed time: 1h 41m
```

Pareto frontは次のとおりだった。

| trial | 拒否 | KL |
|---|---|---|
| 2 | 0/100 | 8.7006 |
| 5 | 3/100 | 1.8413 |
| 64 | 4/100 | 0.0419 |
| 93 | 5/100 | 0.0385 |
| 86 | 6/100 | 0.0310 |
| 84 | 8/100 | 0.0284 |
| 100 | 13/100 | 0.0241 |
| 77 | 20/100 | 0.0173 |

(途中の行は一部省略。全件は`experiments/day-059/results.md`。)

拒否0/100に到達したtrialは12個あったが、KLは全て8.70以上だった。
KLが0.1未満のtrialで最も拒否が少ないのは4/100(KL 0.0419)である。
`--trial-index 0`が選んだのはtrial 2(0/100、KL 8.70)で、Pareto frontの中で最も元モデルから離れたものだった。
Day 036の同じ条件の実行でも拒否0/100のtrialは12個あり、選ばれたtrialのKLは1.3763だった。
Optunaのseedが既定で未指定のため、どのtrialが出るかは実行ごとに変わるが、「拒否を0にした解はKLが大きい」という形は2回とも同じだった。

## まとめ

- 縮小設定(Qwen3-0.6B、12 trial、`response_prefix = ""`)では、拒否率6/20→0/20、KL 0.0000という結果が再現した。
- しかしこのKLは、思考モードのモデルで最初の1トークンが常に`<think>`(平均99.97%)になる位置で測っていて、劣化の有無を示していなかった。
- `response_prefix`を既定の自動検出に戻すと、同じ12 trialのKLの中央値は0.0001から0.0243に上がった。
- `--trial-index 0`はPareto frontの先頭、つまり拒否が最も少なくKLが最も大きいtrialを選ぶ。Qwen3-4B-Instruct-2507・100 trialでは、それが拒否0/100・KL 8.70のtrialだった。

hereticの「拒否率とKLを同時に見る」という設計自体は筋が通っている。
ただ、KLが1トークンだけで測られていること、思考モデルではその1トークンがどこになるかで結果が桁で変わることは、数字だけを見ていると気づけない。
設定を縮小するときに「時間がかかるから」と自動検出を止めたことが、そのまま評価を無効にしていた。
指標が劣化ゼロと言ったときこそ、その指標が何を見ているのかをソースで確かめる必要がある。

設定ファイル・集計ログ・最初の1トークンを調べたスクリプトは`experiments/day-059/`に置いている。

## 出典・ライセンス

- heretic: https://github.com/p-e-w/heretic (AGPL-3.0-or-later、検証バージョン: heretic-llm 2.1.0)
- Qwen3-0.6B: https://huggingface.co/Qwen/Qwen3-0.6B (Apache-2.0)
- Qwen3-4B-Instruct-2507: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 (Apache-2.0)
- 評価データセット: https://huggingface.co/datasets/mlabonne/harmful_behaviors , https://huggingface.co/datasets/mlabonne/harmless_alpaca
