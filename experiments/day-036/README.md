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
そのままコピーして使えば同じ(ごく小規模な)設定で再実行できる。GPUが使える環境では
`config.toml` を使わずに素の既定設定(`heretic Qwen/Qwen3-4B-Instruct-2507` など)を
試すほうが、ツール本来の挙動(100試行のベイズ的最適化)を確認できる。

## 実行ログ

`heretic_run/run.log` に標準出力をそのまま保存している(`time` コマンドの実測時間を含む)。
`heretic_run/checkpoints/` にはOptunaのstudy checkpoint(JSON Lines)が入っている。

## 結果の詳細

`results.md` を参照。
