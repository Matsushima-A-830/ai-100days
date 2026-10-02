# Day 004: Jeff (Qwen3.5/Gemma4ファインチューン版ゼロショット分類モデル) 検証ログ

## 結果サマリ

**今日の検証は完了できませんでした。** 選んだ候補(`today.md` Day 004: Jeff,
https://github.com/firelex/jeff )のコード自体はクローンでき、依存関係もインストールできましたが、
モデル本体の重みは Hugging Face (`huggingface.co`) からしか配布されておらず、
このクラウド実行環境のネットワークポリシーが `huggingface.co` への接続を組織ポリシーで拒否(403)していたため、
実際の推論を一度も実行できませんでした。詳細と再現コマンドは `results.md` を参照してください。

このため、articles/ posts/ の記事・投稿案・シェアカードは作成していません
(CLAUDE.mdの「動かしていないものを動いたと書かない」に従い、実行できていない比較結果を記事化しないため)。
PRも作成していません。

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

## 人間への申し送り事項

- このクラウド実行環境のネットワークポリシーで `huggingface.co` を許可ドメインに追加するか、
  アクセスレベルを広げれば、次回以降は同じ候補で実際の推論検証が可能になる見込みです
  (環境のタイトルバーのクラウド環境メニュー → Edit → Network access)。
- もしくは、`today.md` を Hugging Face 非依存で検証可能な別候補
  (例: backlog.mdの「MicroLLM Lab」など、WebGPU/ブラウザ完結でAPIキー・HF不要なもの)に
  差し替えることをおすすめします。
