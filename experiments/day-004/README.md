# Day 004: Jeff (Qwen3.5/Gemma4ファインチューン版ゼロショット分類モデル) 検証ログ

## 結果サマリ(2026-10-02 再試行で更新)

**初回(2026-10-01)はネットワーク制限のため検証未完了でしたが、2026-10-02の再試行で
`huggingface.co` へのアクセスが回復していることを確認し、実際にモデルをダウンロードして
推論・比較検証まで完了しました。** 詳細は下の「初回の記録」および `results.md` の
「再試行(2026-10-02)」セクションを参照してください。

- モデル重み(`mstrasser/Jeff-Qwen3.5-0.8B`, 約1.79GB)のダウンロードに成功。
- `jeff-serve` をこの環境で起動し、README記載のクイックスタート例で動作を確認。
- 自作の問い合わせメール分類タスク(18件、うち8件は単純なキーワードルールだと
  誤分類しやすい意地悪な例)で、「キーワードルールベース分類」と「Jeffのゼロショット分類」を比較。
  Jeffが精度94.4%(ルールベース72.2%)、意地悪な例だけで見ると87.5%(ルールベース37.5%)という結果。
- 記事・X投稿案・シェアカードは今回作成済み(`articles/day-004-jeff-zero-shot-classification.md`,
  `posts/day-004.md`, `posts/day-004-card.html`)。

## 初回(2026-10-01)の記録: 検証未完了だった経緯

**このときの検証は完了できませんでした。** 選んだ候補(`today.md` Day 004: Jeff,
https://github.com/firelex/jeff )のコード自体はクローンでき、依存関係もインストールできましたが、
モデル本体の重みは Hugging Face (`huggingface.co`) からしか配布されておらず、
このクラウド実行環境のネットワークポリシーが `huggingface.co` への接続を組織ポリシーで拒否(403)していたため、
実際の推論を一度も実行できませんでした。詳細と再現コマンドは `results.md` を参照してください。

このため、articles/ posts/ の記事・投稿案・シェアカードは作成していませんでした
(CLAUDE.mdの「動かしていないものを動いたと書かない」に従い、実行できていない比較結果を記事化しないため)。

## 試したこと(時系列)

1. `git clone https://github.com/firelex/jeff` → 成功(GitHubはアクセス可)。
2. `uv sync --no-default-groups --extra lora` → 当初セッションの `uv` が 0.8.17 でJeffの要求(`>=0.12.19`)を
   満たさずエラー。`pip install --upgrade uv` で `/usr/local/bin/uv` 0.12.22 を導入し、
   それを使って再実行したところ依存関係のインストールは成功。
3. `uv run --no-default-groups hf download mstrasser/Jeff-Qwen3.5-0.8B --revision v1.2 --local-dir Jeff-Qwen3.5-0.8B-v1.2`
   → `huggingface.co` への接続が `httpcore.ProxyError: 403 Forbidden` で拒否され、重みのダウンロードに失敗
   (エラーログ全文: `hf_download_error.log`)。
4. この実行環境のエージェントプロキシの状態 (`/__agentproxy/status`) を確認したところ、
   `huggingface.co:443` への接続が `connect_rejected`(組織ポリシーによる拒否)として記録されていた。
   プロキシのREADME(`/root/.ccr/README.md`)は「403/407は組織ポリシーによる拒否であり、
   リトライや迂回をせず、ブロックされたホストを報告すること」と明記しているため、
   別ミラー経由での取得などは試みていない。

## 再現方法(このままでは重みが取得できない点に注意)

```bash
git clone https://github.com/firelex/jeff && cd jeff
pip install --upgrade uv   # 同梱のuvが古い場合、hfパッケージ要求(>=0.12.19)を満たすため
/usr/local/bin/uv sync --no-default-groups --extra lora
/usr/local/bin/uv run --no-default-groups hf download mstrasser/Jeff-Qwen3.5-0.8B --revision v1.2 \
  --local-dir Jeff-Qwen3.5-0.8B-v1.2
# → huggingface.co への送信ネットワークが許可されている環境でないとここで失敗する
```

`huggingface.co` への送信アクセスが許可された環境(またはローカルPC)であれば、
`today.md`/`backlog.md` に記載の通り CPU推論・GPU不要で動作するはずです
(README記載のCPU推論時間: Jeff-Qwen3.5-0.8Bで463ms/決定)。

## 確認できたこと(重みなしでも検証可能だった事実)

- リポジトリは実在し、`git clone` でコード取得可能(2026-10-01時点のv1.2相当)。
- ライセンス: コードMIT([LICENSE](https://github.com/firelex/jeff/blob/main/LICENSE)、
  Mathias Strasser 2026 / AutoJev由来部分は Denis Yarats 2026)、重みはREADME記載でApache 2.0。
- 依存関係(`pyproject.toml`)は `huggingface-hub` 経由での重み取得を前提とした設計で、
  リポジトリ内にもGitHub Releaseアセットにも重みは同梱されていない
  (= Hugging Faceへの到達性が必須)。

## 人間への申し送り事項(初回時点のもの。2026-10-02に解決済み)

- このクラウド実行環境のネットワークポリシーで `huggingface.co` を許可ドメインに追加するか、
  アクセスレベルを広げれば、次回以降は同じ候補で実際の推論検証が可能になる見込みです
  (環境のタイトルバーのクラウド環境メニュー → Edit → Network access)。
- もしくは、`today.md` を Hugging Face 非依存で検証可能な別候補
  (例: backlog.mdの「MicroLLM Lab」など、WebGPU/ブラウザ完結でAPIキー・HF不要なもの)に
  差し替えることをおすすめします。

→ 2026-10-02、環境のネットワークアクセス設定が修正され `huggingface.co`
(および `cas-server.xethub.hf.co`, `us.aws.cdn.hf.co`)への到達性が回復したため、以下の通り再試行して成功した。

## 再試行(2026-10-02): 成功した再現手順

実際に動かして確認したコマンド。詳しい出力ログと比較結果の数値は `results.md` の
「再試行(2026-10-02)」セクションを参照。

```bash
# 1. モデルダウンロード用の依存関係(hf CLI)をインストール
pip install -U huggingface_hub transformers torch

# 2. モデル重みを実際にダウンロード(約1.79GB、成功)
hf download mstrasser/Jeff-Qwen3.5-0.8B --local-dir ./Jeff-Qwen3.5-0.8B

# 3. Jeffのサーバー実行環境を用意(uvが古いと pyproject.toml の required-version を満たせないので更新)
git clone --depth 1 https://github.com/firelex/jeff.git && cd jeff
pip install --upgrade uv
/usr/local/bin/uv sync --no-default-groups --extra lora

# 4. ダウンロード済みのチェックポイントを指定してサーバーを起動
JEFF_CHECKPOINT=/path/to/Jeff-Qwen3.5-0.8B PORT=8765 .venv/bin/jeff-serve
curl http://127.0.0.1:8765/health
# => {"status":"ready","model":"jeff-qwen3.5-0.8b", ...}

# 5. README記載のクイックスタート例で疎通確認(クライアントは client.py を単体コピーして使用可、
#    PEP 695 の type 文を使っているため Python 3.12 以降が必要。このセッションには python3.13 があったため使用)
python3.13 experiments/day-004/verify/dataset.py  # (データセット定義。直接実行はしない)
python3.13 experiments/day-004/verify/run_compare.py
```

`experiments/day-004/verify/` に今回使った検証コード一式を置いている:
- `jeff_client.py` — `jeff/src/jeff/client.py` をそのままコピーしたもの(MITライセンス、
  標準ライブラリのみで動くようdocstringで「コピーして使ってよい」と明記されているため)。
- `dataset.py` — 筆者が自作した18件の問い合わせメール分類タスク(お問い合わせを
  billing/technical/cancellation/shippingの4カテゴリに分類)。10件は素直な例、
  8件はキーワールベース分類器だと誤分類しやすいように意図して作った意地悪な例。
- `rule_based.py` — 比較対象の単純なキーワードルールベース分類器(文中の単語を出現順に見て、
  最初にヒットしたキーワードのカテゴリを採用する)。
- `run_compare.py` — 両者を実行して精度・レイテンシを比較し `compare_results.json` に出力する。
