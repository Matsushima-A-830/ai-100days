# Day 004 results.md — Jeff ゼロショット分類モデル検証

## 選定候補

- タイトル: Jeff — Qwen3.5/Gemma4をファインチューンした22msの軽量ゼロショット分類モデル
- 出典: https://github.com/firelex/jeff (Release v1.1/v1.2)
- today.mdでの検証計画: 「キーワードルールベースの分類」と「Jeffのゼロショット分類」を
  自作の簡単な分類タスク(問い合わせ文の振り分けなど)で精度・速度の両面で比較する(Before/After)。

## 実施結果: 未完了(モデル重みを取得できず、推論を一度も実行できなかった)

### 1. リポジトリのクローン — 成功

```
$ git clone --depth 1 https://github.com/firelex/jeff.git
Cloning into 'jeff'...
```
exit code 0。README・ソース・pyproject.toml・ライセンス等は正常に取得できた。

### 2. 依存関係インストール — 成功(ただし同梱uvのバージョン問題を1点修正)

セッション標準の `uv`(`/root/.local/bin/uv`, 0.8.17)はJeffの要求する
`required-version = ">=0.12.19"` (pyproject.toml) を満たさず、以下のエラーで失敗:

```
error: Required uv version `>=0.12.19` does not match the running version `0.8.17`.
Update `uv` by running `uv self update`.
```

`uv self update` はGitHub API経由で、このセッションのGitHubアクセスがリポジトリ単位にスコープされているため
`GitHub API rate limit exceeded. Please provide a GitHub token` で失敗。
代わりに `pip install --upgrade uv`(PyPI経由、このプロキシ環境で許可されている)で
`/usr/local/bin/uv` 0.12.22 を導入し、それを明示的に使うことで解決。

```
$ /usr/local/bin/uv sync --no-default-groups --extra lora
 + torch==2.14.0
 + transformers==5.17.0
 + huggingface-hub==1.31.0
 + peft==0.21.1
 （中略、全依存関係インストール成功、exit code 0）
```

### 3. モデル重みのダウンロード — 失敗(huggingface.co が組織ポリシーでブロック)

```
$ /usr/local/bin/uv run --no-default-groups hf download mstrasser/Jeff-Qwen3.5-0.8B \
    --revision v1.2 --local-dir Jeff-Qwen3.5-0.8B-v1.2

httpcore.ProxyError: 403 Forbidden
  （huggingface_hub -> httpx -> httpcore 経由で huggingface.co への接続が
    エージェントプロキシに403で拒否された。全スタックトレースは hf_download_error.log 参照)
```

このクラウド実行環境のエージェントプロキシの状態確認コマンド結果:

```
$ curl -sS http://127.0.0.1:46677/__agentproxy/status
...
"recentRelayFailures": [
  {
    "kind": "connect_rejected",
    "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
    "host": "huggingface.co:443"
  }
]
```

プロキシの案内(`/root/.ccr/README.md`)は「403/407は組織(環境)のネットワークポリシーによる拒否であり、
リトライや別ホスト経由での迂回をせず、ブロックされたホストを報告すること」としているため、
他のミラー等を試すことはしていない。

### 4. 以降のステップ(推論実行、キーワードルールベースとの比較)— 未実施

モデルの重みが無いため、`jeff-serve` の起動・`Client.ask()` による推論・
キーワードルールベース分類器との精度/速度比較のいずれも実行していない。
**「動いた」「速かった」「精度が良かった」等の記述は一切できない状態。**

## 結論

- このクラウド実行環境では `huggingface.co` への送信アクセスが組織ポリシーでブロックされており、
  Jeffの重みはHugging Faceからしか配布されていないため、本候補の実機検証は本環境では不可能だった。
- 記事・X投稿・noteの原稿・シェアカードは作成していない(未実行の結果を記事化しないため)。
- ブランチ・PRも作成していない。
- 人間への申し送り: `experiments/day-004/README.md` の「人間への申し送り事項」を参照。
  (a) 環境のNetwork access設定で `huggingface.co` を許可する、または
  (b) today.md の候補をHugging Face非依存の別案に差し替える、のいずれかで明日以降再試行可能。
