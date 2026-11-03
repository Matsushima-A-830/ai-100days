# Day 036: Heretic(Abliterationによる拒否挙動の抑制)を検証する

対象: https://github.com/p-e-w/heretic (AGPL-3.0-or-later)

## 再現手順

```bash
# 1. venvを作る(システムPythonのpip/setuptoolsだと依存関係のビルドに失敗することがある。
#    experiments/day-036/results.md の「1. インストール時に詰まったこと」参照)
python3 -m venv heretic-venv
source heretic-venv/bin/activate
pip install -U pip setuptools wheel

# 2. heretic-llm をインストール
pip install -U heretic-llm

# 3. このディレクトリの config.toml を使って、縮小した設定でスモーク実行する
cd experiments/day-036/heretic_run
heretic --model Qwen/Qwen3-0.6B --trial-index 0 --model-action ""
```

`config.toml` は `tools/card-template.html` と同様にこのリポジトリにコミットしてあるため、
そのままコピーして使えば同じ(ごく小規模な)設定で再実行できる。

## ローカル検証(GPU、実施済み・2026-11-03)

人間のGPU環境(RTX 5060 Ti, 16GB VRAM)で、`config.toml`を使わず素の既定設定のまま
`heretic --model Qwen/Qwen3-4B-Instruct-2507 --trial-index 0 --model-action ""`を実行した。
100試行の既定規模の探索が1時間35分で完走し、CPU実行時の推定(約25時間)やREADMEのRTX 3090
参考値(30〜40分)と比較しても実用的な時間で完結することを確認した。詳細は`results.md`の
「6. ローカル検証」節を参照。

## 実行ログ

`heretic_run/run.log`(CPUでのスモーク実行)・`heretic_run_gpu/run.log`(GPUでの既定規模実行)
に標準出力をそのまま保存している。各ディレクトリの`checkpoints/`にはOptunaのstudy checkpoint
(JSON Lines)が入っている。

## 結果の詳細

`results.md` を参照。
