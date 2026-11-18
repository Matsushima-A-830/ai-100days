# Day 051 — jingyaogong/minimind

出典: https://github.com/jingyaogong/minimind (commit `233d00fa068ec2b8c0d4f07b703934d6391a5a73`, 2026-10-27時点のmain)
ライセンス: Apache License 2.0(`LICENSE`ファイル参照。リポジトリそのままの全文で改変していない)

## これは何か

Tokenizer → Pretrain → SFT → LoRA/DPO/PPO/GRPO/CISPO → エージェント的RL → 蒸留まで、
LLMの学習パイプライン全体を高レベルラッパーなしでPyTorchネイティブに実装したOSS。
主ブランチの既定構成「minimind-3」はhidden_size=768, num_hidden_layers=8の
Dense Transformer(Qwen3系設定準拠)で、公式READMEは「64Mパラメータ、RTX3090 1枚で
Pretrain約1.21時間+SFT約1.10時間、合計2.3時間程度」と主張している。

本検証はクラウドRoutine実行環境(GPUなし、4 vCPU、RAM 15GB)で行った。
GPU前提の「2時間で自作LLM」という主張そのものの再現はスコープ外とし、
**実際のminimind-3設定(hidden_size=768, num_hidden_layers=8 → 実測63.91Mパラメータ)を
変えずに、データセット量とステップ数だけを縮小してCPU上でPretrain→SFTの
一連の流れが動くか、動いた場合に生成結果が学習前後でどう変わるかを確認した。**

## 再現手順

```bash
# 1. リポジトリをclone
git clone --depth 1 https://github.com/jingyaogong/minimind.git
cd minimind

# 2. Python仮想環境を作り、torch(CPU)と最小限の依存を導入
python3 -m venv .venv-minimind
.venv-minimind/bin/pip install torch
.venv-minimind/bin/pip install numpy transformers==4.57.6 datasets==3.6.0 \
    sentencepiece==0.2.0 jsonlines==4.0.0 ujson==5.1.0 rich==13.7.1 \
    einops==0.8.1 jieba==0.42.1

# 3. 公式データセット(Hugging Face: jingyaogong/minimind_dataset)から
#    HTTP Range Requestで先頭の一部だけを取得する(1.2GB/1.6GBの全量は不要なため)
curl -L -r 0-5000000 \
  -o pretrain_chunk.raw \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/pretrain_t2t_mini.jsonl"
curl -L -r 0-8000000 \
  -o sft_chunk.raw \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/sft_t2t_mini.jsonl"
# 末尾の不完全な1行を捨てて、完全なJSON Linesだけを dataset/ 配下に保存
# → pretrain_t2t_mini_sample.jsonl (6,685行) / sft_t2t_mini_sample.jsonl (2,805行)

# 4. Pretrain(公式スクリプトそのまま。データ量・ステップ数だけ縮小)
cd trainer
python train_pretrain.py \
  --epochs 2 --batch_size 8 --accumulation_steps 1 \
  --max_seq_len 256 --num_workers 0 \
  --data_path ../dataset/pretrain_t2t_mini_sample.jsonl \
  --save_dir ../out --save_weight pretrain \
  --log_interval 20 --save_interval 836 --device cpu

# 5. SFT(pretrainの重みを引き継ぎ)
python train_full_sft.py \
  --epochs 2 --batch_size 8 --accumulation_steps 1 \
  --max_seq_len 384 --num_workers 0 \
  --data_path ../dataset/sft_t2t_mini_sample.jsonl \
  --save_dir ../out --save_weight full_sft --from_weight pretrain \
  --log_interval 20 --save_interval 100000 --device cpu

# 6. Before/After生成比較(今回のために書いた非対話版スクリプト gen_compare.py)
python gen_compare.py --weight_path ./out/pretrain_768.pth --is_pretrain 1 \
    --tokenizer_path ./model --seed 42
python gen_compare.py --weight_path ./out/full_sft_768.pth --is_pretrain 0 \
    --tokenizer_path ./model --seed 42
```

### ローカルGPUでの検証(results.md 7節)

```bash
# torchはPyPIの既定wheel(2.15.0+cu132)。RTX 5060 Ti(sm_120)で動作確認
# 縮小データ: 4・5の手順で --device cuda:0 に変えるだけ
# 公式mini版データ全量・既定値で1 epochずつ(公式のRTX 3090目安: 1.21h + 1.10h)
curl -L -o dataset/pretrain_t2t_mini.jsonl \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/pretrain_t2t_mini.jsonl"
curl -L -o dataset/sft_t2t_mini.jsonl \
  "https://huggingface.co/datasets/jingyaogong/minimind_dataset/resolve/main/sft_t2t_mini.jsonl"
cd trainer
python train_pretrain.py --epochs 1
python train_full_sft.py --epochs 1
# 生成比較(minimindのリポジトリ直下で)
python ../ai-100days/experiments/day-051/gen_compare.py --weight_path out/full_sft_768.pth --is_pretrain 0
```

注意: `train_full_sft.py --from_weight` は `--save_dir` に関係なく `../out/` から重みを読む。

`gen_compare.py` は公式の対話スクリプト`eval_llm.py`が`input()`による対話入力を
要求する作りだったため、固定プロンプト4問に対して非対話でBefore/After比較できるよう
今回書き下ろしたもの(モデル読み込み・生成ロジックは`eval_llm.py`と同じ構成)。

## ディレクトリの内容

- `logs_pretrain.txt` — Pretrainの全ログ(2 epoch、1,672 step)
- `logs_sft.txt` — SFTの全ログ(2 epoch、702 step)
- `logs_generation.txt` — Before(pretrainのみ)/After(SFT後)の生成結果全文(seed=42で固定、再現可能)
- `results.md` — 検証結果のまとめ(正直な記録)
- `gen_compare.py` — Before/After生成比較スクリプト(ローカル検証時に追加)
- `logs_gpu_small_*.txt` — ローカルGPUでの縮小データ再現ログ
- `logs_gpu_full_pretrain.txt` — ローカルGPUでの公式mini版データ全量Pretrainログ

モデルの重みファイル(`pretrain_768.pth` / `full_sft_768.pth`、各約131MB)は
容量の都合でこのリポジトリにはコミットしていない。再現手順通りに実行すれば
`minimind/out/`配下に同じ構成のファイルが生成される。
