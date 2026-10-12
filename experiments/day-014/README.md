# Day 014 — TokenRouter(thu-nics)

出典: https://github.com/thu-nics/TokenRouter (Hugging Face Daily Papers 2026-10-09掲載)

**状態: ローカル検証が必要。** 詳細な経緯は [results.md](./results.md) を参照。

## 要約

- `today.md`で選定された候補。ライセンス確認(CLAUDE.mdの絶対ルール)とGPU要否確認を検証開始前に
  行った結果、以下2点がブロッカーとして判明した。
  1. リポジトリにLICENSEファイルが同梱されておらず、`pyproject.toml`のclassifierに
     "Apache Software License" とあるのみでライセンスが確定していない。
  2. 公式のサンプル構成(`config/*.yaml`)はすべてQwen3-32B(tp_size=2、複数GPU)+CUDA MPS前提で、
     本Routineのクラウド実行環境にはGPUデバイス自体が存在しないため、インストール・実行を試せなかった。
     0.6B+1.7Bのような軽量構成は公式にサポートされていない。
- そのため、実際のルーティング有無でのデコードスループット比較などの検証には進めず、記事・X投稿案・
  note原稿・シェアカードは**作成していない**。

## ローカル検証をお願いしたい内容(matsu氏向け)

### A. ライセンスの確認

リポジトリ https://github.com/thu-nics/TokenRouter を直接確認し、
- README/Issues/論文("NeurIPS 2026")側にライセンスに関する追記が無いか
- 必要であれば著者にIssueで問い合わせるか、`pyproject.toml`のclassifier (Apache) を実質的な
  ライセンスとして扱って良いか

を判断していただきたい。

### B. GPUでの動作確認

ローカルPCにCUDA GPU(できれば2枚、または `tp_size: 1` に変更できるか試す)がある場合、以下の手順で
公式READMEの「Environment Setup」「Reproducing Our Results」に沿って動作を確認していただきたい。

```bash
git clone https://github.com/thu-nics/TokenRouter
cd TokenRouter
conda create -n tokenrouter python=3.10
conda activate tokenrouter
pip install -e .

# 複数モデルが同じ物理GPUを共有する場合(README記載の手順)
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log
nvidia-cuda-mps-control -d

# config/ 配下のいずれかの手法(例: r2r)でサーバーを起動し、ルーティングあり/なしの
# デコードスループットを比較する(具体的な起動コマンドはREADMEの該当節を参照)
```

GPUが無い/不足している場合は、それ自体を「人間のローカルPCのスペックが足りず動かなかった」という
検証に直接関係する失敗として記録できる(CLAUDE.mdの「書く」カテゴリ)。

結果が出たら `experiments/day-014/results.md` に追記し、その内容を元に記事・X投稿案・note原稿・
シェアカードを作成する。
