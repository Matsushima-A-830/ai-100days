---
title: "有料APIキー無しでCI/CD信頼性エージェントOpenSREは動くのか試した"
emoji: "🛠️"
type: "tech"
topics: ["ai", "llm", "ollama", "sre", "cicd"]
published: false
---

## これは何を試した記事か

[OpenSRE](https://github.com/Tracer-Cloud/opensre)は、CIが落ちたときにログを読んで根本原因を調べ、必要なら修正案をPRに出す自己ホスト型のAIエージェントである。
Apache-2.0で公開されており、GitHub Trendingで急伸していた。

本チャレンジでは有料APIキーが必須の候補は選ばないという方針があるため、OpenSREの「サインインしてホスト型モデルを使う」既定の導線は使わず、ローカルLLM(Ollama)だけで動かす前提で検証した。
結論を先に書くと、筆者が今回たどり着けたのは「OpenSREというツール自体のインストール・CLI・設定モデルを手を動かして確認した」ところまでで、Ollamaでモデルを動かしてCI障害を実際に調査・修正させるところまでは到達できなかった。
ただその過程で、有料キー無しで使おうとした人が最初に踏みそうな、生のPythonスタックトレースでクラッシュするという実際の挙動を見つけた。

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

## 何も設定しないとどうなるか

`opensre doctor`を実行すると、LLMプロバイダが未設定であることを警告として教えてくれる。

```
  OpenSRE Doctor

  ✓  python             Python 3.11.18
  !  env_file           .env not found
  !  llm_provider       LLM_PROVIDER env var is not set
  !  integrations       /root/.tracer/integrations.json not found — run 'opensre integrations setup'
  ✓  version            2026.4.5 (could not check: GitHub API returned HTTP 403)
  ✓  network            github.com reachable (HTTP 200)

  3 issue(s) found. Fix them and rerun 'opensre doctor'.
```

`opensre health`も試すと、60以上あるという連携先のうち一覧表示された約30件すべてが未設定(`0 passed | 29 missing | 1 failed`)で、裏で勝手に何かの有料サービスに接続しに行くような挙動は見られなかった。
唯一`FAILED`になっていたのはAWSで、環境に残っていた何かのAmbient資格情報でSTSを呼びに行って`InvalidClientTokenId`で失敗していたが、これは本チャレンジのAPIキーとは無関係の実行環境側の事情である。

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
複数回実行して再現性も確認したので、たまたまの一時的な問題ではない。

## `LLM_PROVIDER=ollama`を指定すると挙動が変わる

同じコマンドに、環境変数を一つだけ加えて実行してみる。

```bash
LLM_PROVIDER=ollama .venv/bin/opensre investigate -i alert.json
```

今度はさきほどのクラッシュは起きず、実際にLangGraphで組まれたエージェントの状態遷移が動き出し、`plan_actions`ノードまで進んでからOllamaサーバーへの接続を試みて失敗する。

```
File ".../app/nodes/plan_actions/node.py", line 61, in node_plan_actions
File ".../app/nodes/plan_actions/plan_actions.py", line 303, in plan_actions
File ".../app/services/llm_client.py", line 314, in invoke
RuntimeError: LLM API request failed after multiple retries. Try again in a few seconds.
During task with name 'plan_actions' ...
```

つまり、「サインイン不要・有料キー不要でOllamaだけで動かせる」という設計自体は実在していて、環境変数一つの差でクラッシュ地点が全く変わるということを、同じアラートJSON・同じコマンドで実際に確認できた。
ソースを読むと、`config/llm_auth/provider_catalog.py`でプロバイダごとの認証方式が定義されており、他のほぼ全プロバイダ(Anthropic・OpenAI・Gemini・DeepSeekなど)が`API_KEY`という認証種別なのに対し、Ollamaだけが`LOCAL`(ローカルホストへの到達性だけを見る、鍵は要らない)という扱いになっている。

## Ollama自体は今回起動できなかった

OpenSREには`opensre onboard local_llm`という「ゼロコンフィグのローカルLLM設定」コマンドがあり、Ollamaが入っていなければ公式のインストールコマンドを自動で実行してくれる設計になっている。
筆者の検証環境ではこのインストールが完了せず、Ollamaを実際に起動してモデルを動かすところまでは到達できなかった。
そのため、「意図的に壊したCIをOpenSREに調査・修正させる」という本来やりたかった検証は、今回はローカルPCでの追加検証が必要という持ち越しになった(持ち越しの詳細は`experiments/day-058/`を参照)。

## まとめ

今回手を動かして確認できたのは次の3点である。

- OpenSREはpip一発でインストールでき、CLIは素直に動く。ただしGitHubの`main`のドキュメントとPyPIの実配布版には機能差がある。
- 何も設定しない状態で`investigate`を実行すると、デフォルトプロバイダがAnthropicになっており、生のPythonスタックトレースでクラッシュする。
- `LLM_PROVIDER=ollama`を指定するだけで、クラッシュせずに本物のLangGraphエージェントパイプラインまで到達する。有料キー無しで動かす設計自体は実在する。

Public Alpha段階のツールだけあって、エラーハンドリングの粗さが実際に見つかったのは収穫だった。
Ollamaを実際に動かした上での本番の調査・修正デモは、別途ローカル環境で検証する。

## 出典・ライセンス

- https://github.com/Tracer-Cloud/opensre (Apache-2.0)
- https://pypi.org/project/opensre/ (検証バージョン: 2026.4.5)
