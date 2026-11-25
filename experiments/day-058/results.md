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
接続しに行くような挙動は確認できなかった(Routine環境では`aws`が1件failedになったが、
ローカルでは再現せず`0 passed | 30 missing | 0 failed`だった。6章参照)。

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

## 5. Ollama自体の起動(Routine環境)

Routine環境の制約により未検証、ローカル検証待ちとしていた。ローカル検証の結果は6章。

## 6. ローカル検証(人間のPC、2026-11-25)

環境: WSL2 (Linux 6.6) / AMD Ryzen 7 7700 (8コア16スレッド) / RAM 30GB / Ollama(CPU推論、`CUDA_VISIBLE_DEVICES=-1`、n_ctx 4096) /
OpenSRE 2026.4.5を`python:3.12-slim`のDockerコンテナで実行(`local/Dockerfile`)。
GPU(RTX 5060 Ti)は別の長時間ジョブが使用中だったため、Ollamaは**CPUのみ**で動かした。
実行に使ったファイル・ログはすべて `local/` にある。

### 6-1. 3章・4章の再現

- `LLM_PROVIDER`未設定(HOMEも空の状態)で`investigate` → 3章と同じ`ValidationError ... requires ANTHROPIC_API_KEY`で終了(rc=1)。再現した。
- `LLM_PROVIDER=ollama`、Ollama未起動 → 4章と同じく`plan_actions`まで進み`RuntimeError: LLM API request failed after multiple retries.`(rc=1)。再現した。
- `opensre doctor`: `.env not found` / `LLM_PROVIDER env var is not set` / integrations未設定の3件(`LLM_PROVIDER=ollama`を付けると`✓ llm_provider provider=ollama`で2件)。
- `opensre health`: `Summary: 0 passed | 30 missing | 0 failed`。Routine環境で出ていたAWSのfailedはローカルでは出なかった。

### 6-2. 意図的に壊したCIを調査させる

today.mdの計画どおり、壊すためのダミーリポジトリ `local/invoice-calc/` を作った(GitHub Actionsのワークフロー `.github/workflows/ci.yml` 付き)。

- `main`(e558453): 消費税込み金額 `round(subtotal * (1 + rate), 2)`。テスト3件。
- `feature/fast-total`(6917f6e "Speed up total_with_tax using integer cents"): 1行を `int(subtotal * (1 + rate) * 100) / 100` に変更(`local/feature-fast-total.diff`)。
  `int()`は切り捨てなので 19.99×1.1 = 21.989 → 21.98 になり、`test_rounding`が落ちる。**正解の根本原因は「calc.pyの`total_with_tax`で`round`を`int()`切り捨てに置き換えたこと」**。

ワークフローと同じ手順(`pip install` → `ruff check .` → `pytest -q`)を`local/ci.sh`でコンテナ内実行したCIログ:

```
$ (main) ... 3 passed ... Process completed with exit code 0.
$ (feature/fast-total)
$ ruff check .
All checks passed!
$ pytest -q
.F.
>       assert total_with_tax(19.99) == 21.99
E       assert 21.98 == 21.99
E        +  where 21.98 = total_with_tax(19.99)
FAILED tests/test_calc.py::test_rounding - assert 21.98 == 21.99
1 failed, 2 passed in 0.02s
Process completed with exit code 1.
```

PyPI版2026.4.5にはGitHub ActionsのログやPRを直接読みに行く機能が無い(GitHub連携はCopilot MCP経由の読み取り専用で、
トークンが必要)。そのため、`investigate`の入力アラートJSONにCIログ全文を入れて渡した。

- `local/alert_v1_log.json`: アラート名・ブランチ・コミット・失敗ステップ・**CIログ全文**
- `local/alert_v2_log_diff.json`: v1 + **`git diff main..feature/fast-total`全文**

実行コマンド(`local/run_inv.sh`):

```bash
docker run --rm --network host -v $W:/work \
  -e LLM_PROVIDER=ollama -e OLLAMA_MODEL=<model> -e OLLAMA_HOST=http://127.0.0.1:11599 \
  -e DO_NOT_TRACK=1 -e OPENSRE_ANALYTICS_DISABLED=1 \
  day058-opensre:2026.4.5 opensre investigate -i /work/<alert>.json -o /work/out/<tag>.json
```

### 6-3. 結果(`local/out/runs.txt`、各ログ・JSONは`local/out/`)

| tag | モデル | 入力 | 終了 | 所要 | LLM呼び出し(成功/タイムアウト) |
|---|---|---|---|---|---|
| q7-v1-r1 | qwen2.5:7b-instruct | ログ | rc=0 | 451s | 11 / 1 |
| q7-v1-r2 | qwen2.5:7b-instruct | ログ | rc=0 | 419s | 11 / 1 |
| q7-v2-r1 | qwen2.5:7b-instruct | ログ+diff | rc=0 | 462s | 12 / 1 |
| q7-v2-r2 | qwen2.5:7b-instruct | ログ+diff | rc=0 | 580s | 11 / 3 |
| q14-v1-r1 | qwen2.5:14b-instruct | ログ | rc=1 | 1459s | 1 / 25 |
| q14-v2-r1 | qwen2.5:14b-instruct | ログ+diff | rc=1 | 1016s | 0 / 18 |

(成功/タイムアウトはOllamaサーバーログの`/v1/chat/completions`のHTTPステータスを実行時間帯ごとに数えたもの。
タイムアウトは全て所要`1m0s`で切られた500/499。Ollama側でプロンプトの切り詰めは0件、最大プロンプトは約2.5kトークン。)

7Bの4回が出した結論(`report`の先頭行と所見、原文):

| tag | 結論 | 所見(Non-Validated Claimsを含む) | 最終confidence |
|---|---|---|---|
| q7-v1-r1 | `Most likely: code_defect` | 「`test_calc.py`の最近の変更が原因かもしれない」 | 25% |
| q7-v1-r2 | `test_rounding assert failure due to incorrect rounding in the total_with_tax function` | 「`total_with_tax`の丸めロジックが誤っているかもしれない」 | 25% |
| q7-v2-r1 | `Most likely: code_defect` | 「最近のコード変更かもしれないが、コミット履歴が必要」 | 25% |
| q7-v2-r2 | `Most likely: code_defect` | 「`total_with_tax`の最近の変更」+「データベース層の不整合かもしれない [evidence: aws_rds_events, datadog_logs]」 | 25% |

- 4回とも完走し、「コード側の不具合(code_defect)」という分類は4回とも正しかった。
- 壊した関数名`total_with_tax`に触れたのは4回中2回。**`int()`による切り捨てという本当の原因を指摘した回は0回**。
  diffをアラートに入れても(v2)、diffの中身(`round`→`int`)には言及しなかった。
- 1回(q7-v1-r1)は原因をテスト側のファイル(`test_calc.py`)に求め、1回(q7-v2-r2)は存在しないDB・AWSのデータソースを根拠として挙げた。
- 修正案(パッチ)やPRは出力されない。PyPI版`investigate`の出力はRCAレポート(`report`/`root_cause`/`problem_md`/`is_noise`)のみ。

### 6-4. エージェントのループの中身

7Bの4回とも、計画(Planning)→証拠収集(Gathering evidence)→診断(Diagnosing)のループを5周して打ち切られた。
**証拠収集20回(4回×5周)のうち、証拠が1件でも集まった回は0回**(`No evidence collected`)。原因は次の2つ:

- `get_error_logs` / `get_failed_jobs`など、計画で選ばれるツールの多くは連携先(Datadog・AWS Batch等)の設定が前提で、
  未設定だと`Action not available: required data sources not found`で失敗する。
- `run_diagnostic_code`(LLMが書いたコードを実行するツール)は、毎回`TypeError: run_diagnostic_code() missing 1 required ...`で失敗した。
  investigateの経路ではこのツールに引数を渡す処理(extract_params)が定義されておらず、引数なしで呼ばれている(ソース`app/tools/run_diagnostic_code.py`を確認)。
  結果として、LLMが書いたコードは一度も実行されていない。

診断はアラートに入っていたCIログだけから行われており、最終的に「SRE runbook(`get sre guidance`)」だけが引用された。

### 6-5. 14Bモデルが完走しない理由

`app/services/llm_client.py`でOpenAI互換クライアントが`timeout=60.0`固定で作られており、1回60秒を超えると3回まで再試行した後
`RuntimeError: LLM API request failed after multiple retries.`で終了する。環境変数や設定でこの値を変える方法は見当たらなかった。
CPU推論の14Bは1回の応答に60秒以上かかるため、2回とも診断・計画の途中で落ちた(q14-v1-r1は`diagnose`ノード、q14-v2-r1は`plan_actions`ノード)。
7Bでも「Reading alert」の最初の呼び出しが60秒を超えて再試行になった回があった(q7-v1-r1は105.5s)。

### 6-6. その他、手元で気づいたこと

- **利用状況の送信が既定でオン**: OpenSREはPostHog(`us.i.posthog.com`)へ、匿名ID・イベント名・Python/OSのバージョン・CLIバージョンを送る。
  `DO_NOT_TRACK=1`または`OPENSRE_ANALYTICS_DISABLED=1`で止まる(ソース`app/analytics/provider.py`で確認)。6-1の最初の2回はオプトアウトせずに実行し、それ以降は全て止めて実行した。
- `opensre onboard local_llm`は`OLLAMA_HOST`を見ず`localhost:11434`固定で、このPCでは`llama3.1:8b`を推奨してpullしようとする。
  既存のOllama(GPU使用中)に新しいモデルを載せることになるため、今回は実行していない。
- README記載の`opensre ask`はPyPI版に無い(1章の再現)。

## まとめ

- ✅ pip経由のインストール、CLI、`doctor`/`health`、設定モデル(Ollamaだけ鍵不要の`LOCAL`)を確認した。
- ✅ `LLM_PROVIDER`未設定だと生のトレースバックでクラッシュする挙動を、Routine環境とローカルの両方で確認した。
- ✅ `LLM_PROVIDER=ollama`+qwen2.5:7b-instruct(CPU)で、壊したCIの調査が4回中4回完走した(419〜580秒)。分類(code_defect)は4回とも正しい。
- ❌ 本当の原因(`int()`切り捨て)を指摘した回は0回。関数名に触れたのが2回、誤ったファイル・存在しないデータソースを挙げたのが各1回。最終confidenceは全て25%。
- ❌ 連携先が未設定だと証拠収集ツールが使えず、20回の証拠収集で証拠は0件。`run_diagnostic_code`は引数不足で毎回失敗。
- ❌ qwen2.5:14b-instruct(CPU)は60秒固定のタイムアウトで2回とも完走しなかった。
- ❌ 修正案・PRはPyPI版`investigate`では出力されない。
