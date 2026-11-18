---
title: "「3090で約2.3時間」の64M LLM自作を、RTX 5060 Tiで公式手順どおり回したら7時間19分だった"
emoji: "🧩"
type: "tech"
topics: ["ai", "llm", "pytorch", "python", "opensource"]
published: false
---

## これは何の話か

[jingyaogong/minimind](https://github.com/jingyaogong/minimind)は、Tokenizer・Pretrain・SFT・LoRA・DPO・PPO・GRPO・CISPO・エージェント的RL・蒸留まで、LLMの学習パイプライン全体を高レベルラッパーなしでPyTorchネイティブに実装したOSSである(Apache License 2.0)。
本稿執筆時点でGitHub Trending(Python)に入り、スター数は65,881・前日比+188だった。
公式READMEは「RMB 3・2時間でLLMをゼロから作れる」を掲げ、既定構成の`minimind-3`(64Mパラメータ)はRTX 3090 1枚でPretrain約1.21時間+SFT約1.10時間、合計約2.31時間で学習できると主張している(Training Cost表)。

この主張を、手元のRTX 5060 Ti 16GBで確かめた。
**モデル構成・学習スクリプトの既定値は一切変えず、公式のmini版データセットを全量使い、`--epochs 1`だけ指定してPretrain→SFTを最後まで回した。**
あわせて、データを0.4〜0.5%まで減らした縮小版をCPU 4コアとGPUの両方で回し、速度と学習結果を比べた。
日本語でのZenn/Qiita/note紹介記事は検索時点で見つからなかった。

検証コード・全ログは[experiments/day-051](https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-051)に置いた。

## 検証環境

| 項目 | 内容 |
|---|---|
| GPU | NVIDIA GeForce RTX 5060 Ti 16GB |
| OS | Windows + WSL2(Linux 6.6) |
| Python / PyTorch | 3.12.3 / `torch==2.15.0+cu132` |
| minimind | commit `233d00fa` |

## minimind-3という構成

`minimind-3`はDecoder-OnlyのTransformerで、Qwen3系の設定に揃えてある(RoPE、RMSNorm、SwiGLU、`q_heads=8`・`kv_heads=4`)。
スクリプトの既定値は`hidden_size=768`・`num_hidden_layers=8`で、学習開始時のログには次のように出た。

```
Model Params: 63.91M
Trainable Params: 63.912M
```

公式が主張する「64Mパラメータ」と一致している。

## データセットを全量ダウンロードする

公式の学習データは[Hugging Face: jingyaogong/minimind_dataset](https://huggingface.co/datasets/jingyaogong/minimind_dataset)で公開されている。
公式の学習時間の目安に使われている`pretrain_t2t_mini.jsonl`と`sft_t2t_mini.jsonl`を、そのまま全量取得した。

```bash
$ curl -L -o pretrain_t2t_mini.jsonl https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/pretrain_t2t_mini.jsonl
$ curl -L -o sft_t2t_mini.jsonl https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/sft_t2t_mini.jsonl
$ wc -l *.jsonl
   1270238 pretrain_t2t_mini.jsonl   # 1,241,043,656 bytes
    905718 sft_t2t_mini.jsonl        # 1,739,201,170 bytes
```

"mini"と名付けられていても、Pretrain用は約127万行・1.2GB、SFT用は約91万行・1.7GBある。

## Pretrainを公式既定値のまま回す

スクリプトの既定は2 epochなので、公式の目安(1 epoch)に合わせて`--epochs 1`だけ指定した。
既定値はbatch_size 32、accumulation_steps 8、max_seq_len 340、lr 5e-4、bfloat16である。

```bash
$ cd trainer
$ python train_pretrain.py --epochs 1 --data_path .../pretrain_t2t_mini.jsonl
```

```
Epoch:[1/1](100/39695), loss: 7.5222, ... epoch_time: 186.0min
Epoch:[1/1](39695/39695), loss: 2.0073, ...
WALL 9741.46 s
```

39,695 stepを**9,741秒(2時間42分)**で完走した。
公式の3090目安1.21時間の約2.2倍である。
lossは7.52(step 100)から2.01(最終step)まで下がり、4k stepごとの値は2.80 / 2.61 / 2.40 / 2.33 / 2.17 / 2.12 / 1.90 / 2.06 / 2.16だった。
学習中の`nvidia-smi`はGPU使用率99%、GPU使用メモリ約7.7GB(学習前の待機時0.9GBを含む)で、16GBのうち半分程度しか使っていない。

## SFTを公式既定値のまま回す

`train_full_sft.py`は既定で`../out/pretrain_768.pth`を読み込んでSFTを始める。
既定値はbatch_size 16、max_seq_len 768、lr 1e-5、bfloat16である。

```bash
$ python train_full_sft.py --epochs 1 --data_path .../sft_t2t_mini.jsonl
```

```
Epoch:[1/1](100/56608), loss: 2.2343, ...
Epoch:[1/1](56608/56608), loss: 1.6899, ...
WALL 16607.99 s
```

56,608 stepを**16,608秒(4時間37分)**で完走した。
公式の3090目安1.10時間の約4.2倍で、Pretrainよりも公式との差が大きい。
lossは2.23(step 100)から1.69(最終step)まで下がったが、step 5,000以降は1.5〜1.9の間を上下していて、Pretrainほどはっきりとは下がらなかった。

## 公式の目安との比較

| | 公式(RTX 3090) | 今回(RTX 5060 Ti 16GB) | 比 |
|---|---|---|---|
| Pretrain 1 epoch | 約1.21h | 2h42m(9,741秒) | 約2.2倍 |
| SFT 1 epoch | 約1.10h | 4h37m(16,608秒) | 約4.2倍 |
| 合計 | 約2.31h | **7h19m(26,349秒)** | 約3.2倍 |

RTX 5060 Ti 16GBでも、公式既定値のままメモリ不足やエラーなしに最後まで動いた。
ただし所要時間は合計7時間19分で、「2時間程度」はRTX 3090クラスのGPUを前提にした数字であることが分かる。
同じ構成でも、GPUが変わると半日近い作業になる。

## 全量学習の前後で生成結果はどう変わったか

Pretrainのみの重みとSFT後の重みに、同じ4問を答えさせた。
公式の`eval_llm.py`も`echo 0 | python eval_llm.py --weight full_sft`とすれば固定8問を自動で回せるが、プロンプトごとのseedが乱数になる。
そこで同じ読み込み・生成設定(fp16、top_p=0.95、temperature=0.85)で、プロンプトごとに`seed=42`を固定する`gen_compare.py`を書いた。

```bash
$ python gen_compare.py --weight_path out/pretrain_768.pth --is_pretrain 1
$ python gen_compare.py --weight_path out/full_sft_768.pth --is_pretrain 0
```

**Before(Pretrainのみ。チャットテンプレートなしで続きを書かせる)**

```
PROMPT: 你有什么特长？(あなたの得意なことは？)
RESPONSE: 我是一个AI语言模型，没有能力，我被设计和训练，没有亲身体验和感受。我被训练以理解和生成人类语言，…
```

**After(SFT後。チャットテンプレート適用)**

```
PROMPT: 你有什么特长？
RESPONSE: 我是MiniMind，一个由jingyaogong创造的高效AI模型。我擅长处理复杂的计算任务，同时提供准确的回答和逻辑推理。…
(私はMiniMind、jingyaogongが作った効率的なAIモデルです。複雑な計算タスクと正確な回答・論理的推論が得意です。)
```

Pretrainのみでも、全量学習後は文として成立した中国語が出てくる。
ただし質問に答えるのではなく、プロンプトの続きを書いているだけである(他の質問では「？」「。」「菜谱。」のように、プロンプトの続きの文字から書き始めた)。
SFT後はチャット形式で答え、自己紹介には「MiniMind」「jingyaogong」という名前まで入るようになった。

知識を問う質問では、形式は整ったが内容は不正確なままだった。

```
PROMPT: 解释一下"光合作用"的基本过程(光合成の基本的な過程を説明して)
RESPONSE(After): 光合作用是一种生物化学过程，主要由以下几个步骤和原理构成：

1. **光反应**：光反应是将原子核反应，将电子排出来，释放出能量。…
(光合成は生化学的な過程で、主に以下の段階からなる。1. 光反応:光反応とは原子核反応で、電子を放出してエネルギーを放つ…)
```

見出し付きの箇条書きというSFTデータの応答形式は身についている一方、光反応を「原子核反応」と説明している。
料理の質問でも、火鍋の説明に「烤鸭和鸭肉为食(北京ダックと鴨肉を食材とする)」と書くなど、64Mパラメータ・1 epochでは事実の正確さまでは届かなかった。
Pretrainのみの重みでは、料理の質問が「湘菜、湘菜、湘菜…」の繰り返しに陥った(既定の`repetition_penalty=1`のため)。

なお生成速度は28〜75 tok/sだった。
SFT後の1問目だけは計測値が負(-0.54秒)になっており、WSL2上で`time.time()`の時刻が巻き戻ったためと見られるので、この1件は除外している。

## 縮小データでCPUとGPUを比べる

全量学習とは別に、データを先頭の一部だけ(Pretrain 6,685行=全量の約0.42%、SFT 2,805行=約0.5%)に減らし、同じ公式スクリプトをCPU 4コアとRTX 5060 Tiで回した。
引数はbatch_size 8、max_seq_len 256(SFTは384)、2 epochで、違いは`--device`だけである。

```bash
$ curl -L -r 0-5000000 -o pretrain_chunk.raw \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/pretrain_t2t_mini.jsonl"
$ python train_pretrain.py --epochs 2 --batch_size 8 --accumulation_steps 1 \
  --max_seq_len 256 --num_workers 0 --data_path ../dataset/pretrain_t2t_mini_sample.jsonl \
  --save_dir ../out --save_weight pretrain --log_interval 20 --save_interval 836 --device cuda:0
```

| | CPU 4コア | RTX 5060 Ti |
|---|---|---|
| Pretrain 2 epoch / 1,672 step | 約62分 | **124.5秒** |
| Pretrain loss(step 20 → 最終) | 7.4156 → 4.0453 | 7.4153 → 4.0189 |
| SFT 2 epoch / 702 step | 約38分 | **64.7秒** |
| SFT loss(step 20 → 最終) | 4.9916 → 3.5065 | 4.9991 → 3.5349 |
| 合計 | 約1時間40分 | 約3分10秒 |

lossの下がり方はCPUとGPUでほぼ同じで、違うのは速さだけだった。
パイプラインがCPUでも最後まで動くことは確認できたが、全量をCPUで回すのは現実的ではない。
縮小データの重みでも、SFT後は「你有什么特长？」に`我是由jingyaogong创建的…`と自己紹介で答えた。
一方で光合成などの質問は、事実と無関係な単語が連なるだけの文になった。
全量学習後の出力と比べると、データ量の差がそのまま文の質の差になっている。

## つまずいた点: `--from_weight`は`--save_dir`を見ない

縮小データの検証では、全量学習の重みと混ざらないよう`--save_dir ../out_small`を指定してPretrainを保存し、SFTを`--save_dir ../out_small --from_weight pretrain`で実行した。
すると次のエラーで止まった。

```
FileNotFoundError: ... '../out/pretrain_768.pth'
```

`train_full_sft.py`の`--from_weight`は`--save_dir`を参照せず、`trainer_utils.init_model()`の`save_dir`既定値`'../out'`から常に読み込む作りになっていた。
保存先を変える場合は、Pretrainの重みを`../out/`に置いておく必要がある。
公式手順どおり`../out`を使う限りは問題にならない。

## まとめ

- minimind-3(64M、実測63.91M)は、RTX 5060 Ti 16GBでも公式mini版データ全量・既定値のままPretrain→SFTを最後まで完走した。
- 所要時間はPretrain 2時間42分+SFT 4時間37分=**合計7時間19分**で、公式の3090目安(約2.31時間)の約3.2倍だった。
- lossはPretrain 7.52→2.01、SFT 2.23→1.69まで下がった。
- SFT後のモデルは自己紹介や箇条書きの形式は身につけたが、知識を問う質問の内容は不正確だった。
- 縮小データではCPU 4コアの約1時間40分がGPUでは約3分10秒になり、lossの推移はほぼ同じだった。

「2時間でLLMを作れる」は、RTX 3090クラスのGPUがあればという条件付きで読むのがよさそうである。
それでも、64Mのモデルをゼロから学習させてチャット形式で答えさせるところまでを、一般的なゲーミングGPU 1枚で一晩のうちに終えられた。

## 出典・ライセンス

- リポジトリ: https://github.com/jingyaogong/minimind (Apache License 2.0、commit `233d00fa068ec2b8c0d4f07b703934d6391a5a73`)
- データセット: https://huggingface.co/datasets/jingyaogong/minimind_dataset
- 検証コード・全ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-051
