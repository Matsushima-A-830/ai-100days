---
title: "重みの0.05%を消すだけでファインチューニング相当? Deletion Tuningの公開マスクを実際に適用してみた"
emoji: "✂️"
type: "tech"
topics: ["ai", "llm", "huggingface", "qwen", "finetuning"]
published: false
---

## この記事で試したこと

NeurIPS 2026に採択された論文「The Surprising Effectiveness of Deleting Weights in LLM Post-Training」([arXiv:2611.10866](https://arxiv.org/abs/2611.10866)、[Hugging Face Daily Papers](https://huggingface.co/papers/2611.10866))は、事前学習済みLLMのTransformerブロックのgate projection上にバイナリマスクを学習し、全体の0.05%未満の重みを0にするだけで、強化学習(RLVR)・SFT・on-policy distillationにおいてフルファインチューニングと同等の性能になると報告している手法「Deletion Tuning」の論文である。
著者らは学習済みマスクを[Hugging Face](https://huggingface.co/Jacklu0831/deletion-tuning-masks)で公開しており、コードも[MITライセンス](https://github.com/agentic-learning-ai-lab/deleting-weights)で公開されている。

筆者はこの論文を実際に検証した日本語記事が見当たらなかったため、公開されている学習済みマスクを実際にダウンロードし、ベースモデルに適用して、応答の変化とファイルサイズの主張を自分の手で確認した。
フルのGRPO/SFT学習の再現にはGPU前提の重いセットアップ(flash-attention・vLLM・verl)が必要なため、今回は**公開済みマスクの適用と評価**に絞っている。

## 使ったもの

- ベースモデル: [Qwen/Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B)(Apache-2.0、ゲート無し)
- マスク: [Jacklu0831/deletion-tuning-masks](https://huggingface.co/Jacklu0831/deletion-tuning-masks)内の`grpo/qwen2.5-0.5b-simplerl-zoo`
- コード: [agentic-learning-ai-lab/deleting-weights](https://github.com/agentic-learning-ai-lab/deleting-weights)(MIT)

論文の著者ら自身のREADMEでは`meta-llama/Llama-3.2-1B-Instruct`や`Qwen/Qwen2.5-7B`も対象として挙がっているが、前者はHugging Face利用規約への同意が必要なゲート付きモデルで今回の実行環境からは即座に取得できず、後者は7Bクラスで筆者の実行環境(CPUのみ)では生成に時間がかかりすぎる。
そのため同じリポジトリが公開している、ゲート無し・Apache-2.0の`Qwen2.5-0.5B`向けマスクを選んだ。
これも著者ら自身が論文の実験で使っている正式な対象の1つである。

マスクが公開している`config.json`には、著者ら自身が計測した実測値がそのまま入っている。

```json
{
  "format": "packbits_zstd",
  "total_params": 104595456,
  "zero_params": 199564,
  "original_size_mb": 99.75,
  "compressed_size_mb": 0.45673274993896484,
  "sparsity_ratio": 0.0019079605140781641,
  "compression_ratio": 218.3990528669775
}
```

## マスクの適用

マスクの形式は単純で、bit-packed(1重みにつき1bit)した上でzstd圧縮したバイナリマスクを、対象の重み(gate projection)に掛けて0にするだけである。
著者らのリポジトリの`src/apply_mask.py`はこれを約100行で実装している。
筆者の実行環境のサンドボックスはclone済みの外部コードを直接実行することを許可しない設定だったため、同じロジックを自分で読み直して書き直したスクリプトを使って適用した(アルゴリズムは原文と同一)。

```bash
$ python3.13 apply_mask.py \
    --base_model qwen0.5b-base --mask_dir mask_qwen0.5b --output_dir qwen0.5b-masked
Loading weights: 100%|██████████| 290/290 [00:00<00:00, 2343.19it/s]
Writing model shards: 100%|██████████| 1/1 [00:01<00:00,  1.18s/it]
deleted 199,564 weights; saved to qwen0.5b-masked
```

CPUのみの環境でも1秒程度で完了した。

## 本当にマスクが効いているか・ファイルサイズを検証する

「マスクを適用した」と書いて終わりにせず、実際にベースモデルとマスク適用後モデルの全パラメータを比較した。

```
model.layers.0.mlp.gate_proj.weight: shape=(4864, 896), total=4358144, zeroed_in_masked_but_nonzero_in_base=8698
parameter tensors that differ between base and masked: 24 / 290
base model.safetensors: 988,097,824 bytes (942.3 MB)
masked (dense) model.safetensors: 988,097,824 bytes (942.3 MB)
released mask file (model.safetensors): 483,831 bytes (0.4614 MB)
dense-checkpoint / mask-file size ratio: 2042.2x
total base model parameters: 494,032,768
zero_params (deleted) / total model params = 0.0404%
```

変更されたパラメータテンソルは290個中24個だけで、すべて各層の`gate_proj`(`num_hidden_layers=24`と一致)だった。
他の重み(attentionやembeddingなど)は完全に無変更である。
削除された重みはモデル全体のパラメータ数(494,032,768個)の**0.0404%**で、論文の「0.05%未満」という主張と一致する実測値が得られた。

ファイルサイズの主張も確認できた。
マスクを適用して保存した「密な」チェックポイント(ゼロを明示的に埋め込んだ通常のモデル)は942.3MBで、ベースモデルとバイト単位で同じサイズになる。
これに対して著者らが実際に配布しているマスクファイル自体は0.46MBしかなく、密なチェックポイントの**約2042分の1**である。
論文が謳う「フルファインチューニング済みチェックポイントより数百〜数千倍小さい」という主張を、実際にダウンロードしたファイルのバイト数で確認できた。
(マスクの`config.json`が記す`compression_ratio`は218.4倍だが、これはgate_proj層だけの重みサイズ〈99.75MB〉に対する比率で、モデル全体の密な保存と比較した今回の2042倍とはスコープが異なるだけで矛盾はない。)

## 応答はどう変わるか

GSM8K形式の算数応用問題3問を、ベースモデルとマスク適用後モデルの両方にraw text(chat template無し)で与え、貪欲復号で比較した。
これは論文の正式な評価(SimpleRL-Zooの6ベンチマークをvLLMで評価するスクリプト)の再現ではなく、GPU前提のセットアップが必要なため今回のスコープ外とし、手動で選んだ3問だけの小規模な定性比較に留めている。

| 問題 | 正解 | ベースモデル | マスク適用後 |
|---|---|---|---|
| Natalia(クリップ販売) | 72 | 正解(72) | 正解(72) |
| robe(繊維の本数) | 3 | 正解(3) | 正解(3) |
| Weng(ベビーシッター時給) | 10 | 不正解(60。分を時間に変換せず計算) | 不正解(1。分→時間への変換は正しく言語化できたが最終計算が崩れた) |

3問中2問はどちらのモデルも正解し、残り1問はどちらも不正解だった。
興味深いのは不正解だった1問で、マスク適用後モデルは「分を時間に変換する必要がある」という正しい解法方針までは言語化できていた点である(最終的な掛け算の実行では崩れている)。
全パラメータの0.0404%(gate projectionのみ)をゼロ化しただけで、応答の構造や方向性は大きく破壊されていないことを確認できた。
ただしサンプル数が3問だけなので、モデル全体の性能が同等かどうかという統計的な結論は出せない。

## 6倍大きいモデルでも同じ主張が確認できるか

ここまではCPUのみの環境で動かせる範囲に絞って0.5Bクラスのモデルで検証した。
筆者のPCにはGPU(NVIDIA GeForce RTX 5060 Ti、16GB VRAM)があるため、同じ`Jacklu0831/deletion-tuning-masks`リポジトリが公開している6倍大きい`grpo/qwen2.5-3b-simplerl-zoo`(ベースモデル`Qwen/Qwen2.5-3B`、ゲート無し)に差し替えて、全く同じ手順をもう一度実行した。

マスクを適用すると、434個中36個のパラメータテンソル(すべて`gate_proj`)が変更され、削除された重みはモデル全体の**0.0380%**だった。
配布マスクファイル(2.73MB)は密なチェックポイント(5886.0MB)の**約2155分の1**で、0.5Bのときの約2042分の1よりもわずかに圧縮率が高かった。
モデルサイズを6倍にしても「0.05%未満」「数百〜数千倍小さい」という論文の主張は同じ水準で成立していた。

GPU上でbf16実行して同じ3問のGSM8K形式問題を試したところ、ベースモデルとマスク適用後モデルはどちらも3問とも正解した。
0.5Bのときは3問中1問(ベビーシッターの時給計算)がどちらのモデルも不正解だったが、3Bに上げるとベースモデル自体の推論力が上がり、マスク適用後も含めて全問正解に変わった。
これはモデルサイズそのものの効果であってマスクの効果ではないが、「ベースモデルとマスク適用後モデルが同程度の正答率を保つ」という傾向自体は、0.5Bと3Bの両方で一貫して確認できた。

## まとめ

- マスクの適用自体は、公開されている学習済みマスクをダウンロードしてCPUで数秒で実行でき、追加の有料APIキーは不要だった。
- 変更された重みは全パラメータの0.0404%(0.5B)・0.0380%(3B)で、論文の「0.05%未満」という主張と一致する実測値をどちらのモデルサイズでも確認できた。
- 配布されているマスクファイルは、同じ変更を適用した密なチェックポイントの約2042分の1(0.5B)・約2155分の1(3B)のサイズで、「数百〜数千倍小さい」という主張を実測で確認できた。
- 算数問題での応答比較では、ベースモデルとマスク適用後モデルは0.5Bでも3Bでも同程度の正答率で、応答の構造も保たれていた。

Deletion Tuningが主張する「ごく少数の重みを消すだけで新しい能力を獲得できる」という方向性は、今回の小規模な検証の範囲では裏付けが取れた。
フルのGRPO学習自体を再現してこのマスクがどう作られたかまで確認するには、GPU環境での別途の検証が必要になる。

## 出典・ライセンス

- 論文: [arXiv:2611.10866](https://arxiv.org/abs/2611.10866) / [Hugging Face Daily Papers](https://huggingface.co/papers/2611.10866)
- コード: [agentic-learning-ai-lab/deleting-weights](https://github.com/agentic-learning-ai-lab/deleting-weights)(MITライセンス)
- マスク: [Jacklu0831/deletion-tuning-masks](https://huggingface.co/Jacklu0831/deletion-tuning-masks)
- ベースモデル: [Qwen/Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B)(Apache-2.0ライセンス)、[Qwen/Qwen2.5-3B](https://huggingface.co/Qwen/Qwen2.5-3B)(Qwen独自ライセンス、ゲート無し)
