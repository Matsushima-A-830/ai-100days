# Day 005: Soup (Layer Streaming) の4GB GPU主張を検証する

- 対象: [Soup](https://github.com/MakazhanAlpamys/Soup)(Apache-2.0) — 単一YAMLでLLMファインチューニングを完結させるCLI
- 検証した主張: READMEの「Layer Streamingで凍結ベースをVRAM外に置き、1層ずつGPUへ流し込むことで、4GB GPUでも8Bモデルをファインチューニングできる」
- 実行環境: ローカルPC、NVIDIA GeForce RTX 5060 Ti(16GB VRAM、Blackwell / sm_120)、WSL2 Ubuntu

## クラウドRoutineではなく人間主導でローカル実行した理由

today.md/backlog.mdの時点で「検証にはCUDA GPUが前提のため、クラウド実行環境では代替手段が必要」と注記済み。
このリポジトリの昼実装Routineが動くクラウド環境にはGPUが無いため、今回は例外的にユーザー(人間)が
ローカルPCのGPUを使って検証した。branch+PR経由でのマージ・公開判断は通常フローと同じ。

## なぜこの検証が面白いか

Soup本家のREADMEに書かれている「4GB GPUで8Bモデル」の実測値(RTX 3050 Laptop 4GB、119.6 tok/s、3.32GB peak)には、
開発者自身による以下の注記がついている:

> measured on v0.72.2, before the v0.73.0 correctness repair that cost -4.8% at 32B; neither has
> been re-run on a 4 GB card since - re-measurement pending in issue #361

つまり**開発者自身が「現行バージョンでの再検証がまだ済んでいない」と明言している状態**。
本検証はこの再検証待ちの主張を、実際の4GB相当の制約下で手元のGPUで追試したもの。

`notebooks/proof-4gb.ipynb`(Colab T4向け)のSection 1-5の構成をそのまま踏襲し、
Colabより高性能な実GPU(16GB、RTX 5060 Ti)上で、プロセスを`torch.cuda.set_per_process_memory_fraction`で
4GBに人為的に制限して実行した。

## やったこと

1. (Section 1-2) バージョン確認、GPUのbf16ハードウェア対応確認
2. (Section 3) プロセスを4GBにメモリキャップし、キャップが実際に機能するか確認(予算超過の確保が拒否されるか)
3. (Section 4) Layer Streamingで分割実行したモデルと、通常のレジデントモデルのフォワード出力が
   浮動小数点ビットレベルで一致するか確認(`torch.equal`)
4. (Section 5) 4GBキャップ下で実際にLlama-3.1-8B-InstructをNF4量子化+LoRA+Layer Streamingで学習し、
   実測ピークVRAMと、保存されたLoRAアダプタの内容を確認

検証コード: `sections_1to4.py`, `section5_8b_4gb.py`。実行ログ: `run2-sections1to4.log`, `run1-section5.log`。

学習後に保存されたLoRAアダプタファイルが空(0テンソル)という不具合を発見したため、高速な
SmolLM2-135Mで原因を切り分けるデバッグスクリプト`debug_empty_adapter.py`も追加した。
根本原因(`state_dict()`と`named_parameters()`のキー不一致)と回避策の詳細は`results.md`を参照。

## 再現方法

```bash
python3 -m venv ~/soup-venv && source ~/soup-venv/bin/activate
pip install 'huggingface-hub<1.32.0' 'soup-cli[train]==0.75.0'
python3 sections_1to4.py
python3 section5_8b_4gb.py
```

バージョンは`notebooks/proof-4gb.ipynb`が検証済みとして明示的にピンしている`soup-cli==0.75.0`に合わせた。

## ライセンス・出典

- コード: [github.com/MakazhanAlpamys/Soup](https://github.com/MakazhanAlpamys/Soup)(Apache-2.0)
- 検証用ベースモデル: [NousResearch/Meta-Llama-3.1-8B-Instruct](https://huggingface.co/NousResearch/Meta-Llama-3.1-8B-Instruct)
  (Metaのオリジナル重みの非ゲート再配布、Llama 3.1 Community License)
- 比較用小型モデル: [HuggingFaceTB/SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct)(Apache-2.0)
- 訓練データはSoup公式notebookのダミー例文(4トピック×8件、自己言及的なQ&A)をそのまま使用。実データではない。
