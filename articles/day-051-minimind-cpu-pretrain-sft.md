---
title: "GPUなしで「64MパラメータのLLMを自作する」公式パイプラインを最後まで動かしてみた"
emoji: "🧩"
type: "tech"
topics: ["ai", "llm", "pytorch", "python", "opensource"]
published: false
---

## これは何の話か

[jingyaogong/minimind](https://github.com/jingyaogong/minimind)は、Tokenizer・Pretrain・SFT・LoRA・DPO・PPO・GRPO・CISPO・エージェント的RL・蒸留まで、LLMの学習パイプライン全体を高レベルラッパーなしでPyTorchネイティブに実装したOSSである(Apache License 2.0)。
本稿執筆時点でGitHub Trending(Python)に入り、スター数は65,881・前日比+188だった。
公式READMEは「RMB 3・2時間でLLMをゼロから作れる」を掲げ、既定構成の`minimind-3`(64Mパラメータ)はRTX3090 1枚でPretrain約1.21時間+SFT約1.10時間、合計2.3時間程度で学習できると主張している。

筆者が検証に使えたのはGPUなしのクラウド実行環境(4 vCPU、RAM 15GB)だった。
そこで「2時間でLLMを作れる」というフルスケールの主張そのものの再現は最初からスコープ外とし、代わりに**モデル構成は公式のminimind-3既定値から一切変えず、データセットの量とステップ数だけを大きく減らして、GPUなしでPretrain→SFTの一連の流れが最後まで動くか、動いた場合に生成結果が学習前後でどう変わるか**を確認した。
日本語でのZenn/Qiita/note紹介記事は検索時点で見つからなかった。

検証コード・全ログは[experiments/day-051](https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-051)に置いた。

## minimind-3という構成

`minimind-3`はDecoder-OnlyのTransformerで、Qwen3系の設定に揃えてある(RoPE、RMSNorm、SwiGLU、`q_heads=8`・`kv_heads=4`)。
スクリプトの既定値は`hidden_size=768`・`num_hidden_layers=8`で、実際にモデルを初期化してパラメータ数を数えると次のようになった。

```
Model Params: 63.91M
Trainable Params: 63.912M
```

公式が主張する「64Mパラメータ」と一致している。
この構成はそのまま変えずに検証した。

## データセットを「mini」のさらに0.4%まで減らす

公式の学習データは[Hugging Face: jingyaogong/minimind_dataset](https://huggingface.co/datasets/jingyaogong/minimind_dataset)で公開されている。
"mini"と名付けられた軽量版データセットでも、Pretrain用`pretrain_t2t_mini.jsonl`は1.2GB、SFT用`sft_t2t_mini.jsonl`は1.6GBあり、全量ダウンロードは今回のCPU検証には不要に大きい。
そこでHTTP Range Requestで先頭の一部だけを取得した。

```bash
curl -L -r 0-5000000 -o pretrain_chunk.raw \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/pretrain_t2t_mini.jsonl"
curl -L -r 0-8000000 -o sft_chunk.raw \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/sft_t2t_mini.jsonl"
```

末尾の不完全な1行を除いて完全なJSON Linesだけを残した結果、Pretrainは**6,685行(全量の約0.42%)**、SFTは**2,805行(全量の約0.5%)**になった。
この量でCPU上のPretrain→SFTが実際に意味のある学習になるかどうかが、今回の検証の核心である。

## Pretrainを実行する

公式スクリプト`trainer/train_pretrain.py`をそのまま使い、変更したのはデータ量・バッチサイズ・系列長・エポック数だけである。

```bash
python train_pretrain.py \
  --epochs 2 --batch_size 8 --accumulation_steps 1 \
  --max_seq_len 256 --num_workers 0 \
  --data_path ../dataset/pretrain_t2t_mini_sample.jsonl \
  --save_dir ../out --save_weight pretrain \
  --log_interval 20 --save_interval 836 --device cpu
```

6,685行をbatch_size 8で割った836 stepが1 epochで、2 epoch・合計1,672 stepを実行した。
ログの一部を示す。

```
Epoch:[1/2](20/836), loss: 7.4156, ...
Epoch:[1/2](836/836), loss: 4.7361, ...
Epoch:[2/2](20/836), loss: 4.3748, ...
Epoch:[2/2](836/836), loss: 4.0453, ...
```

lossは7.42(最初のログ)から4.05(最終step)までほぼ単調に下がった。
壁時計時間は**約62分**で、GPUなしの4コアCPUでも最後までエラーなく完走した。

## SFTを実行する

Pretrain済みの重みを`--from_weight pretrain`で引き継ぎ、同じく公式スクリプト`trainer/train_full_sft.py`をそのまま使った。

```bash
python train_full_sft.py \
  --epochs 2 --batch_size 8 --accumulation_steps 1 \
  --max_seq_len 384 --num_workers 0 \
  --data_path ../dataset/sft_t2t_mini_sample.jsonl \
  --save_dir ../out --save_weight full_sft --from_weight pretrain \
  --log_interval 20 --save_interval 100000 --device cpu
```

2,805行・batch_size 8で351 stepが1 epoch、2 epoch・合計702 stepを実行した。

```
Epoch:[1/2](20/351), loss: 4.9916, ...
Epoch:[1/2](351/351), loss: 3.3691, ...
Epoch:[2/2](20/351), loss: 3.5584, ...
Epoch:[2/2](351/351), loss: 3.5065, ...
```

lossは4.99から3.51まで下がり、壁時計時間は**約38分**だった。
Pretrain+SFTの合計はおよそ**1時間40分**で、公式が主張する「RTX3090で約2.3時間」とはGPU/CPUの違いに加えてデータ量が0.4〜0.5%相当という前提の違いがあるため、単純な速度比較はできない。

## 学習前後で生成結果はどう変わったか

公式の対話スクリプト`eval_llm.py`は`input()`による対話入力を要求する作りで、非対話実行ができなかった。
そこで同じモデル読み込み・生成ロジックを使って固定の4問に答えさせる非対話スクリプトを今回書き、`seed=42`固定で再現できるようにした。

自己紹介を聞く質問では、学習前後で明確な変化があった。

**Before(Pretrainのみ。チャットテンプレートなしの生文継続)**

```
PROMPT: 你有什么特长？(あなたの得意なことは？)
RESPONSE: 我很高兴去哪里餐厅？作为AI语言模型，我建议您咨询一些建议。我建议你在巴黎里。...
```

**After(SFT後。チャットテンプレート適用)**

```
PROMPT: 你有什么特长？
RESPONSE: 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、准确的信息和回答。
(私はjingyaogongが作った効率的な小型AIモデルで、正確な情報と回答の提供に専念しています)
```

Beforeは質問を無視してレストランや映画の話を続けてしまうのに対し、Afterは文法的に通り、内容としても妥当な自己紹介文で答えられるようになった。
この手の自己紹介応答はSFTデータに類似パターンが多く含まれるため、0.5%相当という少量データでも学習しやすかったと考えられる。

一方で、知識を要する質問では改善が確認できなかった。

```
PROMPT: 解释一下"光合作用"的基本过程(光合成の基本的な過程を説明して)
RESPONSE(After): 今天天气明媚，气温高，气温是水。地球变成四季，由一个体积分，形成一个黑洞。
(今日は天気が良く、気温が高く、気温は水です。地球は四季になり、ある体積分により、黒洞〈ブラックホール〉を形成します。)
```

文法的には多少整っているように見えても、内容は事実と無関係な単語が連鎖しているだけで破綻している。
これは今回のデータ量(全量の0.4〜0.5%相当)の少なさと、公式推奨の全量学習に遠く及ばないステップ数が主因と考えられる。

## まとめ

minimind-3の既定構成(64M、実測63.91M)を一切変えず、データ量を公式の0.4〜0.5%相当まで減らしてGPUなしの4 vCPU環境で検証したところ、Pretrain→SFTのパイプラインはエラーなく最後まで動き、合計約1時間40分でlossはPretrain側7.42→4.05、SFT側4.99→3.51まで下がった。
生成結果は、SFTデータに頻出するパターン(自己紹介)では学習前後で明確に改善した一方、知識を要する質問では改善が確認できなかった。
「GPU 1枚・2時間でLLMを作れる」という公式の主張そのものの真偽は今回のCPU縮小版の結果からは判断できないが、少なくともこのパイプライン自体はGPUを持たない環境でも、データを削ればその場で動かして学習の進み方を観察できるという点は確認できた。

## 出典・ライセンス

- リポジトリ: https://github.com/jingyaogong/minimind (Apache License 2.0、commit `233d00fa068ec2b8c0d4f07b703934d6391a5a73`)
- データセット: https://huggingface.co/datasets/jingyaogong/minimind_dataset
- 検証コード・全ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-051
