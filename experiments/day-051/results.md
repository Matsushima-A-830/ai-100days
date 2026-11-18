# Day 051 — jingyaogong/minimind 検証結果

出典: https://github.com/jingyaogong/minimind (commit `233d00fa068ec2b8c0d4f07b703934d6391a5a73`)
データセット出典: https://huggingface.co/datasets/jingyaogong/minimind_dataset
(`pretrain_t2t_mini.jsonl` / `sft_t2t_mini.jsonl`)
ライセンス: Apache License 2.0

## 検証スコープ

today.md記載のとおり、公式の「RTX3090 1枚でPretrain約1.21h+SFT約1.10h、
合計2.3時間でLLMを作れる」というフルスケールの主張の再現はGPU前提のため
今回のスコープ外とした。かわりに、**モデル構成(hidden_size=768,
num_hidden_layers=8、公式のminimind-3既定値)は一切変えずに**、データセットの
量とステップ数だけを縮小し、GPUなしのクラウドRoutine実行環境(4 vCPU、
RAM 15GB、`nvidia-smi`なし)でPretrain→SFTの一連の流れが最後まで動くか、
動いた場合に生成結果が学習前後でどう変わるかを確認した。
LoRA/DPO/PPO/GRPO/CISPO/エージェント的RL/蒸留は今回は対象外。

## 0. 環境

```
$ python3 --version
Python 3.11.18
$ nvidia-smi
bash: nvidia-smi: command not found
$ nproc
4
$ free -h
               total        used        free
Mem:            15Gi       473Mi        15Gi
```

## 1. セットアップ

```
$ git clone --depth 1 https://github.com/jingyaogong/minimind.git
$ python3 -m venv .venv-minimind
$ .venv-minimind/bin/pip install torch
```

`download.pytorch.org`(CPU専用wheelの配布元)はプロキシ経由で`403 Forbidden`になり
到達できなかったため、通常のPyPIから`torch`を導入した。結果として
CUDA関連の依存パッケージ(nvidia-cublas等)も一緒にダウンロードされ、
`torch==2.15.0+cu132`がインストールされた(`torch.cuda.is_available()`は`False`、
実際の学習・推論はすべてCPUで実行)。これは検証対象のツールではなく実行環境の
パッケージ取得経路に起因するため、記事本文には書かない。

その後`numpy transformers==4.57.6 datasets==3.6.0 sentencepiece==0.2.0
jsonlines==4.0.0 ujson==5.1.0 rich==13.7.1 einops==0.8.1 jieba==0.42.1`を導入。
`requirements.txt`全量(wandb/streamlit/fastapi等、今回の検証に不要なもの含む)は
導入していない。

モデル初期化時の実測パラメータ数:

```
Model Params: 63.91M
Trainable Params: 63.912M
```

公式READMEが主張する「minimind-3は64Mパラメータ」と一致した。

## 2. データセットの縮小取得

公式データセット(Hugging Face `jingyaogong/minimind_dataset`)の
`pretrain_t2t_mini.jsonl`(1.2GB)・`sft_t2t_mini.jsonl`(1.6GB)は、
「mini」と名付けられていても1GB超と大きいため、全量ダウンロードはせず
HTTP Range Requestで先頭の一部だけを取得した。

```
$ curl -L -r 0-5000000 -o pretrain_chunk.raw \
    "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/pretrain_t2t_mini.jsonl"
HTTP:206 size:5000001
$ curl -L -r 0-8000000 -o sft_chunk.raw \
    "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/sft_t2t_mini.jsonl"
HTTP:206 size:8000001
```

末尾の不完全な1行を除いて完全なJSON Linesだけを抜き出した結果:

- `pretrain_t2t_mini_sample.jsonl`: **6,685行**(全量1.2GBのうち約5MB、約0.42%相当)
- `sft_t2t_mini_sample.jsonl`: **2,805行**(全量1.6GBのうち約8MB、約0.5%相当)

## 3. Pretrain

公式スクリプト`trainer/train_pretrain.py`をそのまま使用。
変更したのはデータ量・バッチサイズ・系列長・ステップ数のみで、モデル構成
(`--hidden_size 768 --num_hidden_layers 8`、スクリプトの既定値)は変えていない。

```
$ python train_pretrain.py \
    --epochs 2 --batch_size 8 --accumulation_steps 1 \
    --max_seq_len 256 --num_workers 0 \
    --data_path ../dataset/pretrain_t2t_mini_sample.jsonl \
    --save_dir ../out --save_weight pretrain \
    --log_interval 20 --save_interval 836 --device cpu
```

2 epoch、合計1,672 step(1 epoch = 836 step、6,685行 ÷ batch_size 8)。
全ログは`logs_pretrain.txt`。抜粋(先頭・末尾):

```
Model Params: 63.91M
Trainable Params: 63.912M
Epoch:[1/2](20/836), loss: 7.4156, ...
Epoch:[1/2](836/836), loss: 4.7361, ...
Epoch:[2/2](20/836), loss: 4.3748, ...
Epoch:[2/2](836/836), loss: 4.0453, ...
```

lossは**7.42(step 20)→4.05(最終step)** まで単調に近い形で下がった。
壁時計時間は実測で**約62分**(CPU 4コア)。

## 4. SFT

公式スクリプト`trainer/train_full_sft.py`をそのまま使用し、`--from_weight pretrain`で
直前のPretrain済み重みを引き継いだ。

```
$ python train_full_sft.py \
    --epochs 2 --batch_size 8 --accumulation_steps 1 \
    --max_seq_len 384 --num_workers 0 \
    --data_path ../dataset/sft_t2t_mini_sample.jsonl \
    --save_dir ../out --save_weight full_sft --from_weight pretrain \
    --log_interval 20 --save_interval 100000 --device cpu
```

2 epoch、合計702 step(1 epoch = 351 step、2,805行 ÷ batch_size 8)。
全ログは`logs_sft.txt`。抜粋:

```
Epoch:[1/2](20/351), loss: 4.9916, ...
Epoch:[1/2](351/351), loss: 3.3691, ...
Epoch:[2/2](20/351), loss: 3.5584, ...
Epoch:[2/2](351/351), loss: 3.5065, ...
```

lossは**4.99(step 20)→3.51(最終step)** まで下がった(ばらつきはあるが下降傾向)。
壁時計時間は実測で**約38分**。

**Pretrain + SFT の合計壁時計時間は約1時間40分**(CPU 4コア、GPUなし)。
公式が主張する「RTX3090 1枚で合計約2.3時間」とは、GPU/CPUの違いに加えて
データ量が0.42〜0.5%相当まで縮小している点が大きく異なるため、単純な比較はできない。

## 5. Before/After 生成比較

`eval_llm.py`は`input()`による対話入力を要求する作りで非対話実行ができなかったため、
同じモデル読み込み・生成ロジック(`model.generate`、top_p=0.95, temperature=0.85）を
使って固定4問に答えさせる`gen_compare.py`を今回書いた。`seed=42`固定で再現可能。
全文は`logs_generation.txt`。

**Before(Pretrainのみ。チャットテンプレートを使わない生文継続)**:

| プロンプト | 生成結果(先頭) |
|---|---|
| 你有什么特长？ | 我很高兴去哪里餐厅？作为AI语言模型，我建议您咨询一些建议。我建议你在巴黎里。您希望您想要看《哈密夫》... |
| 推荐一些中国的美食 | 菜单，包括意大利菜、蛋糕和肉类等。1. 蔬菜：烤鸡蛋、豆腿、西瓜、牛肉、芝士... |

**After(SFT後。チャットテンプレート適用)**:

| プロンプト | 生成結果 |
|---|---|
| 你有什么特长？ | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、准确的信息和回答。我由jingyaogong设计，但用户可能想知道我的功能。 |
| 推荐一些中国的美食 | 好的，用户问《红蹈鹿》的。首先，我需要确保不超过100字。需要提到一些适合美食的食谱... |

**正直な評価**:
「你有什么特长？(あなたの得意なことは？)」という自己紹介系の質問には、SFT後は
`我是由jingyaogong创建的高效小参数AI模型(私はjingyaogongが作った効率的な小型AIモデルです)`
という、文法的に通り事実としても妥当な一文で答えられるようになった。この手の
自己紹介応答はSFTデータ中に類似パターンが多数含まれるため、少量データでも
学習しやすかったと考えられる。

一方で「天空はなぜ青いか」「光合成とは」「中国料理を勧めて」のような知識を要する
質問は、Before/After問わず文法的には多少整っても内容が破綻している
(光合成の説明で「気温は水」「黒洞(ブラックホール)ができる」など事実と無関係な単語が
連鎖する、料理の推薦で存在しない作品名が混入するなど)。これは0.4〜0.5%相当という
データ量の少なさと、公式推奨の全量学習(pretrain_t2t + sft_t2t)に遠く及ばない
ステップ数が主因と考えられる。**「Pretrain→SFTのパイプラインはCPUでも最後まで
動き、自己紹介のような頻出パターンでは実際に応答が改善したが、今回の縮小量では
知識を要する質問にまともに答えられるようにはならなかった」というのが正直な結論。**

## 6. わかったこと(まとめ)

1. 公式の`minimind-3`既定構成(64M、実測63.91M)はCPU・GPUなし環境でも
   Pretrain→SFTのスクリプトがエラーなく最後まで動いた。
2. データを公式推奨量の0.4〜0.5%相当まで減らし、Pretrain 2 epoch(1,672 step)+
   SFT 2 epoch(702 step)、合計壁時計約1時間40分(4 vCPU)で、lossはPretrain
   7.42→4.05、SFT 4.99→3.51まで下がった。
3. 生成結果は、SFTデータに頻出するパターン(自己紹介)では学習前後で明確に改善した
   一方、知識を要する質問では改善が確認できなかった。この量のデータでは
   「文法は整うが内容は不正確」という小型LLMにありがちな限界がそのまま出た。
4. 公式が掲げる「GPU 1枚・2時間でLLMを作れる」という主張そのものはGPU前提であり、
   今回のCPU縮小版の結果からその主張の真偽を判断することはできない
   (今回はスコープ外として明記した通り)。
