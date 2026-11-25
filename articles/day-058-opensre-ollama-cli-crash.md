---
title: "CI障害調査エージェントOpenSREを有料APIキー無し・ローカルLLMで動かし、壊したCIを調べさせた"
emoji: "🛠️"
type: "tech"
topics: ["ai", "llm", "ollama", "sre", "cicd"]
published: false
---

## これは何を試した記事か

[OpenSRE](https://github.com/Tracer-Cloud/opensre)は、CIや本番環境で障害が起きたときにログを読んで根本原因を調べる、自己ホスト型のAIエージェントである。
Apache-2.0で公開されており、GitHub Trendingで急伸していた。

本チャレンジでは有料APIキーが必須の候補は選ばないという方針があるため、OpenSREの「サインインしてホスト型モデルを使う」既定の導線は使わず、ローカルLLM(Ollama)だけで動かした。
そのうえで、わざと壊したCIの失敗ログを渡して、本当の原因を言い当てられるかを試した。

結論を先に書く。

- 何も設定しないと、デフォルトのLLMプロバイダがAnthropicになっていて、生のPythonスタックトレースでクラッシュする。
- `LLM_PROVIDER=ollama`を指定し、qwen2.5の7Bモデル(CPU推論)を使うと、調査は4回中4回最後まで走った(1回419〜580秒)。
- ただし「コード側の不具合」という分類は4回とも正しかった一方、本当の原因(`round`を`int()`の切り捨てに置き換えたこと)を指摘した回は0回だった。
- 14Bモデルは、OpenSREのLLMクライアントに60秒固定のタイムアウトがあるため、CPU推論では2回とも完走しなかった。

## インストールしてみる

PyPIで配布されているので、素直にpip installできる。

```bash
python3 -m venv .venv && .venv/bin/pip install opensre
.venv/bin/opensre --version
```

```
opensre, version 2026.4.5
```

READMEには`opensre ask "why is checkout-api slow?"`というheadless CLIの例が載っているが、筆者が実際にpip installしたバージョン(2026.4.5)の`--help`には`ask`コマンドが存在しない。

```
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

GitHubの`main`ブランチのドキュメントと、PyPIで実際に配布されているリリースの間に機能差があるということ自体が、Public Alphaらしい最初の発見だった。
RCA調査に相当するのは`investigate`コマンドで、アラート情報をJSONで渡す形式になっている。

なお、OpenSREは既定で利用状況(匿名ID・イベント名・Python/OSのバージョンなど)をPostHogに送信する。
ソース(`app/analytics/provider.py`)を読むと`DO_NOT_TRACK=1`または`OPENSRE_ANALYTICS_DISABLED=1`で止まるので、試すときは先に設定しておくとよい。

## 何も設定しないとどうなるか

`opensre doctor`を実行すると、LLMプロバイダが未設定であることを警告として教えてくれる。

```
  OpenSRE Doctor
  ✓  python             Python 3.12.16
  !  env_file           .env not found
  !  llm_provider       LLM_PROVIDER env var is not set
  !  integrations       /home/runner/.tracer/integrations.json not found — run 'opensre integrations setup'
  ✓  version            2026.4.5 (up to date)
  ✓  network            github.com reachable (HTTP 200)
  3 issue(s) found. Fix them and rerun 'opensre doctor'.
```

`opensre health`も試すと、一覧表示された連携先30件がすべて未設定(`0 passed | 30 missing | 0 failed`)だった。

ここまでは警告止まりで優しいのだが、実際に`investigate`コマンドでRCA調査を動かそうとすると様子が変わる。

```bash
.venv/bin/opensre investigate --print-template generic > alert.json
.venv/bin/opensre investigate -i alert.json
```

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for LLMSettings
  Value error, LLM provider 'anthropic' requires ANTHROPIC_API_KEY to be set. [type=value_error, ...]
```

`LLM_PROVIDER`を何も指定していないのに、デフォルトのプロバイダは`anthropic`になっている。
そして、未設定であることをユーザーに案内する処理が無く、`pydantic`の生のバリデーションエラーがそのままスタックトレースとして吐かれて終了する。
「有料キーを使わずに試してみよう」と思って最初に`investigate`を叩いた人は、ここで面食らうはずである。

## `LLM_PROVIDER=ollama`を指定すると挙動が変わる

同じコマンドに、環境変数を一つだけ加えて実行してみる(Ollamaはまだ起動していない状態)。

```bash
LLM_PROVIDER=ollama .venv/bin/opensre investigate -i alert.json
```

今度はさきほどのクラッシュは起きず、LangGraphで組まれたエージェントの状態遷移が動き出し、`plan_actions`ノードまで進んでからOllamaサーバーへの接続を試みて失敗する。

```
File ".../app/nodes/plan_actions/node.py", line 61, in node_plan_actions
File ".../app/nodes/plan_actions/plan_actions.py", line 303, in plan_actions
File ".../app/services/llm_client.py", line 314, in invoke
RuntimeError: LLM API request failed after multiple retries. Try again in a few seconds.
During task with name 'plan_actions' ...
```

ソースを読むと、`config/llm_auth/provider_catalog.py`でプロバイダごとの認証方式が定義されており、他のほぼ全プロバイダ(Anthropic・OpenAI・Gemini・DeepSeekなど)が`API_KEY`という認証種別なのに対し、Ollamaだけが`LOCAL`(ローカルホストへの到達性だけを見る、鍵は要らない)という扱いになっている。
「サインイン不要・有料キー不要でOllamaだけで動かせる」という設計自体は実在する。

## わざと壊したCIを用意する

ここからは実際にOllamaを起動し、OpenSREに壊れたCIを調べさせる。
壊す対象として、消費税込みの金額を計算するだけの小さなPythonリポジトリ`invoice-calc`を作り、GitHub Actionsのワークフロー(`ruff check .`と`pytest -q`)を付けた。

`main`の実装は次の1行である。

```python
def total_with_tax(subtotal: float, rate: float = TAX_RATE) -> float:
    """Return subtotal plus tax, rounded to 2 decimal places."""
    return round(subtotal * (1 + rate), 2)
```

これを壊すブランチ`feature/fast-total`を切り、「整数のセント単位で計算して速くした」という体裁のコミットを入れた。

```diff
-    return round(subtotal * (1 + rate), 2)
+    # Faster: integer cents arithmetic
+    return int(subtotal * (1 + rate) * 100) / 100
```

`int()`は切り捨てなので、19.99円の税込みは21.989から21.98になり、21.99を期待するテストが落ちる。
lintは通るので、ログを見ただけでは原因の場所が分からず、差分を読む必要がある、という程度の難しさを狙った。
ワークフローと同じ手順をコンテナ内で実行したCIログは次のとおりである。

```
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

PyPI版2026.4.5には、GitHub Actionsのログを取りに行く機能や、PRに修正を出す機能は見当たらなかった。
GitHub連携はCopilotのMCPサーバー経由の読み取り専用で、トークンが必要になる。
そこで、`investigate`に渡すアラートJSONにCIログ全文を入れた版(v1)と、さらに`git diff main..feature/fast-total`全文も入れた版(v2)を用意した。

## ローカルLLMで調査させる

環境はWSL2上のAMD Ryzen 7 7700(8コア16スレッド)、RAM 30GBで、OllamaはCPUのみで推論させた。
OpenSRE 2026.4.5は`python:3.12-slim`のDockerコンテナに入れ、ホストのOllamaに接続させた。

```bash
docker run --rm --network host -v $W:/work \
  -e LLM_PROVIDER=ollama -e OLLAMA_MODEL=qwen2.5:7b-instruct -e OLLAMA_HOST=http://127.0.0.1:11599 \
  -e DO_NOT_TRACK=1 -e OPENSRE_ANALYTICS_DISABLED=1 \
  day058-opensre:2026.4.5 opensre investigate -i /work/alert_v1_log.json -o /work/out/q7-v1-r1.json
```

実行すると、アラートの読み込み→連携先の確認→計画→証拠収集→診断という流れが表示される。

```
  ● Reading alert  43.5s
  ● Loading integrations  0ms  No auth context and no local integrations found
  ● Planning  80.7s  error logs, run diagnostic code
[WARNING] Action failed: get_error_logs:FAILED(Action not available: required data sources not fo)
[WARNING] Action failed: run_diagnostic_code:FAILED(TypeError: run_diagnostic_code() missing 1 require)
  ● Gathering evidence  1ms  No evidence collected | Errors: ...
  ● Diagnosing  46.4s  confidence 25%
  (計画→証拠収集→診断をさらに4周)

Investigation complete

test_rounding assert failure due to incorrect rounding in the `total_with_tax` function
```

qwen2.5:7b-instructでv1とv2を2回ずつ、qwen2.5:14b-instructで1回ずつ走らせた結果が次の表である。

| モデル | 入力 | 終了 | 所要 | 結論(レポートの先頭行) |
|---|---|---|---|---|
| 7B | ログ | 完走 | 451s | `Most likely: code_defect`(所見では`test_calc.py`の変更を疑う) |
| 7B | ログ | 完走 | 419s | `incorrect rounding in the total_with_tax function` |
| 7B | ログ+diff | 完走 | 462s | `Most likely: code_defect`(「コミット履歴が必要」) |
| 7B | ログ+diff | 完走 | 580s | `Most likely: code_defect`(所見で`total_with_tax`の変更とDB層の不整合を挙げる) |
| 14B | ログ | 失敗 | 1459s | `RuntimeError: LLM API request failed after multiple retries.` |
| 14B | ログ+diff | 失敗 | 1016s | 同上 |

7Bは4回とも最後まで走り、「コード側の不具合(code_defect)」という分類は4回とも正しかった。
一方で、壊した関数名`total_with_tax`に触れたのは4回中2回で、`int()`の切り捨てという本当の原因を指摘した回は1回も無かった。
diffを渡したv2でも、diffの中の`round`→`int`の変更には触れなかった。
原因をテスト側のファイルに求めた回、存在しないデータベースやAWSのログ(`aws_rds_events`、`datadog_logs`)を根拠に挙げた回もそれぞれ1回あった。
最終的な確信度(confidence)は4回とも25%で、OpenSRE自身も自信が無いという評価をしていた。

## なぜ当たらないのか: 証拠が1件も集まっていない

ログを読むと、7Bの4回はどれも「計画→証拠収集→診断」を5周して打ち切られている。
そして、証拠収集の20回(4回×5周)で、証拠が1件でも集まった回は0回だった。
原因は2つある。

1つ目は、計画で選ばれるツールの多くが連携先を前提にしていることである。
`get_error_logs`や`get_failed_jobs`はDatadogやAWS Batchなどの設定が前提で、何も連携していないと`Action not available: required data sources not found`で失敗する。

2つ目は、LLMが書いたコードを実行する`run_diagnostic_code`が、毎回`TypeError: run_diagnostic_code() missing 1 required ...`で失敗していることである。
`app/tools/run_diagnostic_code.py`を読むと、`investigate`の経路ではこのツールに渡す引数を組み立てる処理が定義されておらず、引数なしで呼ばれている。
結果として、LLMが書いたコードは一度も実行されていない。

つまり今回の診断は、アラートに入れたCIログとdiffだけを見て、7Bモデルが一発で答えを出したのとほぼ同じである。
OpenSREの強みは、オブザーバビリティやインフラの連携先から証拠を集めて突き合わせるところにあるはずで、連携先が何も無い状態ではその強みが働かない。

## 14Bが完走しない理由: 60秒固定のタイムアウト

14Bの失敗は、モデルの性能ではなくOpenSRE側の設定が原因だった。
`app/services/llm_client.py`では、Ollamaへの接続にも使うOpenAI互換クライアントが`timeout=60.0`固定で作られている。

```python
self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=60.0)
```

1回の応答が60秒を超えると3回まで再試行し、それでも駄目なら`RuntimeError`で終了する。
環境変数などでこの値を変える方法は見当たらなかった。
CPU推論の14Bは1回の応答に60秒以上かかるので、Ollama側のログでは2回合わせて44回の呼び出しのうち43回が`1m0s`で打ち切られていた。
7Bでも最初のアラート読み込みが60秒を超えて再試行になり、105.5秒かかった回があった。
今回GPUでは試していないが、CPUでローカルLLMを試す場合は、7B程度のモデルでないと完走は難しい。

## まとめ

今回手を動かして確認できたのは次のことである。

- OpenSREはpip一発でインストールでき、CLIは素直に動く。ただしGitHubの`main`のドキュメントとPyPIの実配布版には機能差があり、`ask`コマンドやPRへの修正機能は配布版では使えなかった。
- 何も設定しない状態で`investigate`を実行すると、デフォルトプロバイダがAnthropicになっており、生のPythonスタックトレースでクラッシュする。
- `LLM_PROVIDER=ollama`とqwen2.5:7b-instructで、壊したCIの調査は4回中4回完走し、「コード側の不具合」という分類は正しかった。
- ただし本当の原因(`int()`の切り捨て)は4回とも指摘できず、確信度は25%止まりだった。連携先が無いと証拠収集のツールが使えず、20回の証拠収集で証拠は0件だった。
- CPU推論の14Bは、60秒固定のタイムアウトで2回とも完走しなかった。
- 利用状況の送信が既定でオンなので、`DO_NOT_TRACK=1`を設定してから試すとよい。

「有料キー無しでも動く」こと自体は本当だった。
ただ、連携先を何も持たずにCIログだけを渡す使い方では、OpenSREは「ログを要約するエージェント」以上の働きはしなかった。
DatadogやAWSなどの連携先を実際に持っている環境で、もう一段大きいモデルと組み合わせたときにどこまで当たるのかは、別の機会に試したい。

検証に使ったダミーリポジトリ・アラートJSON・全ログは、リポジトリの`experiments/day-058/`に置いている。

## 出典・ライセンス

- https://github.com/Tracer-Cloud/opensre (Apache-2.0)
- https://pypi.org/project/opensre/ (検証バージョン: 2026.4.5)
- https://ollama.com/library/qwen2.5 (Qwen2.5、Apache-2.0。検証モデル: qwen2.5:7b-instruct / qwen2.5:14b-instruct)
