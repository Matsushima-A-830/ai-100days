# Day 058 検証結果: OpenSRE (Tracer-Cloud)

出典: https://github.com/Tracer-Cloud/opensre (Apache-2.0)
PyPI: https://pypi.org/project/opensre/ (インストールしたバージョン: 2026.4.5)

## 環境

- Python 3.11.18、`python3 -m venv .venv && .venv/bin/pip install opensre`
- GPU不要(今回はOllama自体が起動できなかったため未使用)

## 1. インストールとCLIの基本挙動

```
$ .venv/bin/opensre --version
opensre, version 2026.4.5

$ .venv/bin/opensre --help
  Usage: opensre [OPTIONS] COMMAND [ARGS]...
  Commands:
    onboard         Run the interactive onboarding wizard.
    investigate     Run an RCA investigation against an alert payload.
    deploy          Deploy OpenSRE to a cloud environment (EC2).
    remote          Connect to remote agents and hosted service ops.
    tests           Browse and run inventoried tests from the terminal.
    integrations    Manage local integration credentials.
    health          Check integration and agent setup status.
    doctor          Run a full environment diagnostic.
    update          Check for a newer version and update if one is available.
    version         Print detailed version, Python and OS info.
```

pip install・CLI起動は問題なく動いた。READMEの `opensre ask "..."` というheadless CLIの例は、
PyPI配布版2026.4.5のコマンド一覧には存在しない(GitHub `main`のドキュメントとPyPIリリースの間に
機能差がある)。該当するのは `opensre investigate` (アラートJSONを渡すRCA調査コマンド)。

## 2. `opensre doctor` / `opensre health`(実行結果そのまま)

```
$ .venv/bin/opensre doctor

  OpenSRE Doctor

  ✓  python             Python 3.11.18
  !  env_file           .env not found
  !  llm_provider       LLM_PROVIDER env var is not set
  !  integrations       /root/.tracer/integrations.json not found — run 'opensre integrations setup'
  ✓  version            2026.4.5 (could not check: GitHub API returned HTTP 403)
  ✓  network            github.com reachable (HTTP 200)

  3 issue(s) found. Fix them and rerun 'opensre doctor'.

$ .venv/bin/opensre health
  Summary: 0 passed  |  29 missing  |  1 failed
```

`health`は60以上の連携先のうち実際に列挙されたのは約30件(表示上限の都合か一部のみ)。
デフォルトでは**何も設定されていない状態で0 passed**であり、静かに有料APIや外部サービスへ
接続しに行くような挙動は確認できなかった(`aws`だけ、サンドボックス内にあった何らかの
ambientなAWS資格情報を使ってSTS呼び出しを試み、`InvalidClientTokenId`で失敗していた。
本チャレンジのAPIキーとは無関係のRoutine実行環境側の資格情報と見られる)。

## 3. LLMプロバイダ未設定での `opensre investigate`(見つかったUX上の問題)

`CLAUDE.md`の「有料APIキー必須の候補は選ばない」方針どおり、何のAPIキーも環境変数も設定せずに
RCA調査コマンドを実行すると、**デフォルトのLLMプロバイダが`anthropic`になっており、
未処理のPythonスタックトレース(`pydantic_core.ValidationError`)でクラッシュする**:

```
$ .venv/bin/opensre investigate -i alert.json
...
pydantic_core._pydantic_core.ValidationError: 1 validation error for LLMSettings
  Value error, LLM provider 'anthropic' requires ANTHROPIC_API_KEY to be set. [type=value_error, ...]
```

`opensre doctor`は`llm_provider`未設定を警告(`!`マーク)として表示するだけで、実際に
`investigate`を実行するとユーザー向けの案内(「`opensre onboard`を実行してください」等)なしに
生のPythonトレースバックで落ちる。Public Alphaゆえのエラーハンドリングの粗さと言える。
再現性は確認済み(複数回同じ結果)。

## 4. `LLM_PROVIDER=ollama` を明示した場合

API資格情報を一切渡さず、`LLM_PROVIDER=ollama`だけを設定すると、上記3のクラッシュは起きず、
実際にLangGraphベースの調査パイプラインが動き出し、`plan_actions`ノードまで進んでから
Ollamaサーバーへの接続(localhost上の想定)を試みて失敗する:

```
$ LLM_PROVIDER=ollama .venv/bin/opensre investigate -i alert.json
...
File ".../app/nodes/plan_actions/node.py", line 61, in node_plan_actions
File ".../app/nodes/plan_actions/plan_actions.py", line 303, in plan_actions
File ".../app/services/llm_client.py", line 314, in invoke
RuntimeError: LLM API request failed after multiple retries. Try again in a few seconds.
During task with name 'plan_actions' ...
```

つまり「サインインも有料キーも無しでOllama一本で動かせる」という設計自体は実在し、
設定(`LLM_PROVIDER=ollama`という環境変数1つ)だけでクラッシュせず本物のエージェント
パイプライン(LangGraphのstate graph、`plan_actions`ノード)まで到達することを確認した。
3と4は同じ`alert.json`・同じコマンドに対する実際の差分であり、作為的な数値の整形はしていない。

## 5. Ollama自体の起動(Routine環境の制約により未検証、ローカル検証待ち)

`opensre onboard local_llm`(ゼロコンフィグのローカルLLM導線)を実行すると、Ollama未導入を
検出して公式インストーラ(`curl -fsSL https://ollama.com/install.sh | sh`)を実行しようとしたが、
このRoutine実行環境のネットワークポリスで`ollama.com`への接続がブロックされており、
インストールが完了しなかった。Routine環境の制約により未検証、ローカル検証待ち。
(detail: `curl: (22) The requested URL returned error: 403` → `Ollama still not found after install.`)

この先の「Ollamaでモデルを動かし、意図的に壊したCI/PRをOpenSREに調査・修正させる」という
today.md本来の検証スコープは、ローカルPC(Ollamaが普通に使える環境)での実施が必要。
また、本リポジトリ(ai-100days)自体にはGitHub Actionsのワークフローが存在しないため、
壊す対象のCIは別途ダミーで用意する必要がある(README.md参照)。

## まとめ

- ✅ pip経由のインストール、CLI、`doctor`/`health`、設定モデル(credential_kind: ollamaは
  "local"、他はAPIキー必須)は実際に動かして確認した。
- ✅ 有料キー無し・LLM_PROVIDER未設定だと生のトレースバックでクラッシュする実際のバグを発見した。
- ✅ `LLM_PROVIDER=ollama`だけで(Ollama自体は未起動でも)本物のLangGraphパイプラインまで
  到達することを確認した。
- ⏸️ Ollamaの起動とそれを使った実際のCI障害調査・修正提案のデモは、Routine環境のネットワーク
  制約によりローカル検証にエスカレーションする。
