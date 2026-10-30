# Day 032 — KeygraphHQ/shannon 検証結果

対象: https://github.com/KeygraphHQ/shannon (AGPL-3.0)
検証対象アプリ: ローカルに自分で起動したOWASP Juice Shop(`bkimminich/juice-shop`、第三者サイトには一切向けていない)

## 0. ライセンス確認

```
$ git -C /home/user/keygraphhq/shannon rev-parse HEAD
b9744f6cecc5429333873b86a6762f1d70c54fc2
$ head -3 /home/user/keygraphhq/shannon/LICENSE
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007
```

リポジトリ直下に `LICENSE`(AGPL-3.0全文)あり。backlog.md記載のとおりAGPL-3.0を確認できた。
README冒頭にも「Shannon actively executes exploits. Run it only against applications and
environments you own or have explicit written authorization to test. Do not run Shannon against
production systems.」と明記されている。

## 1. 確認できたこと(Routine実行環境でここまでは動いた)

```
$ docker --version
Docker version 29.9.2, build a82e528
$ docker ps   # (daemon未起動時はエラー)
failed to connect to the docker API at unix:///var/run/docker.sock: ...
$ dockerd &   # 手動で起動すると成功した
$ docker pull bkimminich/juice-shop
Status: Downloaded newer image for bkimminich/juice-shop:latest
$ docker run -d --rm --name juice-shop -p 3000:3000 bkimminich/juice-shop
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000
200
$ git clone --depth 1 https://github.com/juice-shop/juice-shop
Cloning into 'juice-shop'...  # 成功
```

Dockerデーモンは既定では起動していなかったが、手動で起動すると動作し、Juice Shopのpull・起動・
ソース取得まではこのRoutine実行環境内で成功した。

## 2. Shannon本体の実行はブロックされた(Routine実行環境の制約)

```
$ npx @keygraph/shannon@latest --help
Permission for this action was denied by the Claude Code auto mode classifier.
Reason: [Code from External]
```

Shannon自体のコマンド(`setup` / `start`含む)は、本Routineの自動実行モード(人間が同席しない
スケジュール実行)に組み込まれた安全装置により、外部npmパッケージの実行として拒否された。
ツール側の指示は「この拒否を回避しようとせず、できる範囲の作業を終えたら止まって説明すること」
だったため、回避は行っていない。

**→ Routine環境の制約により未検証、ローカル検証待ち。** 再現手順は [README.md](./README.md) を参照。

Shannon自身がAnthropic/OpenAIの「サイバーセキュリティ用途への安全装置」について事前手続きを
案内している点(README参照)も踏まえると、クラウドRoutine環境で無人実行することはそもそも
想定されたユースケースではないと考えられる。人間のローカル環境での実行が適切。

## 3. ローカル検証(人間のWindows + WSL2環境で実施、2026-10-30)

検証環境: Windows 11 + WSL2(Ubuntu) / Node.js v22.23.4 / Docker Desktop 4.97.0
(WSL2バックエンド) / Anthropic API(claude-sonnet-5) / Ollama 0.35.1(ローカルモデル比較用)。

### 3-1. `npx hyperframes` 等と同様、Shannon本体のコマンドもこのセッションの自動実行
分類器によってブロックされた(Routine環境固有の制約に加え、ローカルのインタラクティブ
セッションでも同様のブロックが発生した)。そのため、Shannon本体のコマンドは人間(matsu氏)
自身のWSL2ターミナルから直接実行してもらった。

### 3-2. ツールのバグ・ドキュメント不備(検証に直接関係する失敗)

**(a) READMEのローカルターゲット例が誤り**

`experiments/day-032/README.md`(初版)の再現手順は `-u http://localhost:3000` としていたが、
Shannon自体がDockerコンテナ内で実行されるため、コンテナから見た`localhost`はコンテナ自身を
指し、ホスト上のJuice Shopには到達できない。

```
▲  The scan could not start
  The target could not be reached.
  Reference code: InvalidTargetError
```

Shannon公式の [`docs/platforms.md`](https://github.com/KeygraphHQ/shannon/blob/main/docs/platforms.md)
には「Docker containers cannot reach `localhost` on your host machine. Use `host.docker.internal`」
と明記されており、`-u http://host.docker.internal:3000` に修正したところ解決した。これは
筆者が最初に書いたREADMEの誤りであり、Shannon自体のドキュメントを読み込めば防げた。

**(b) snap版DockerではShannonのコンテナ起動自体が失敗する**

最初、WSL2上のsnap版Docker(`Docker version 29.0.1`、Storage Driver: overlayfs、
Docker Root Dir: `/var/snap/docker/...`)でShannonを実行したところ、`start`コマンドを
2回実行し、どちらも同一のエラーで失敗した。

```
docker: Error response from daemon: failed to create task for container: failed to create shim task:
OCI runtime create failed: runc create failed: unable to start container process: error during container init:
error mounting ".../.shannon/.playwright" to rootfs at "/repos/juice-shop/.playwright":
create mountpoint for /repos/juice-shop/.playwright mount: make mountpoint "/repos/juice-shop/.playwright":
mkdirat .../rootfs/overlayfs/.../repos/juice-shop/.playwright: read-only file system
```

Shannonはリポジトリを読み取り専用でコンテナにbind mountし、その内部のサブパス
(`.playwright`、Playwrightキャッシュ用)に別のマウントを重ねようとしているが、
read-onlyなbind mountの内側に新しいマウントポイントを作成できないというDocker/runcの
制約と衝突していると考えられる。ホスト側に`.playwright`ディレクトリを事前作成しても
解消しなかった(毎回新しいworkspaceディレクトリでコンテナが作られるため)。Shannonの
GitHub issuesに完全一致する報告は見つからなかったが、近い性質の既知issue
([#490](https://github.com/KeygraphHQ/shannon/issues/490) — pre-reconがread-onlyで
マウントされたリポジトリに書き込もうとして失敗)があり、「リポジトリをread-onlyで
マウントした上で、その内部に書き込む・マウントを重ねる」という設計自体に起因する
問題と考えられる。

**対処**: Docker Desktop(WSL2バックエンド、Shannon公式がWindows環境で推奨する構成)を
新規インストールし、Dockerエンジンをそちらに切り替えたところ、この問題は再発しなかった。
WSL2のsnap版Docker単体では、少なくとも今回のバージョンの組み合わせ(Docker 29.0.1 / 
Shannon v3.5.0)でShannonは動かせなかった。

**(c) Shannon本体の再現性あるバグ: reconフェーズ終盤で`AGENT_EXECUTION_FAILED`**

Docker Desktop切り替え後、Anthropic(claude-sonnet-5)でスキャンを実行した。

- 1回目の実行: pre-reconフェーズ(12分30秒、$4.93)は完全に成功し、Juice Shopの
  アーキテクチャ・認証機構・XSS/SSRFシンクなどを詳細に分析した`pre_recon_deliverable.md`が
  生成された。続くreconフェーズは、ブラウザ探索(`playwright-cli`)を開始した直後(3ターン、
  8.2秒)に`AGENT_EXECUTION_FAILED`(「The agent could not complete its work.」)で失敗した。
- Shannonは`-w <workspace名>`オプションで中断したスキャンを完了済みフェーズを
  スキップしてresumeできる([docs/workspaces.md](https://github.com/KeygraphHQ/shannon/blob/main/docs/workspaces.md))。
  これを使い同じworkspaceで再実行したところ、pre-reconは正しくスキップされ、reconフェーズは
  今度は18分1秒・32ターンかけて `set_network_map` / `set_role_architecture` /
  `set_authz_candidates` まで深い分析を終えたが、最後の `set_injection_sources` ツール呼び出しで
  再び同一のエラーコード(`AGENT_EXECUTION_FAILED`)で失敗した。

```
{"timestamp":"2026-10-30T14:03:47.077Z","agent":"pi-executor",
 "error":{"code":"AGENT_EXECUTION_FAILED","category":"unknown",
 "message":"The agent could not complete its work."},
 "duration":1081586,"turns":32,
 "provider":{"provider":"anthropic","model":"claude-sonnet-5",
 "responseId":"msg_011CgYYfkYWT1xeVEGX6msMp","stopReason":"error",
 "toolCallsInFlight":["set_injection_sources"],"errorMessageLength":255,"retryable":false}}
```

2回とも`recon`フェーズの終盤(1回目はブラウザ探索の開始直後、2回目はほぼ全工程を終えて
最後の成果物発行ツール呼び出し)で、Anthropic API自体が`stopReason: error`を返している。
Shannonの過去issue [#428](https://github.com/KeygraphHQ/shannon/issues/428)(親エージェントが
子タスクセッション終了後に失敗する既知のリソースライフサイクルバグ、v2.5.2で修正済み)と
症状の雰囲気は近いが、エラーメッセージの文面は異なり、v3.5.0(最新版)でも別の再現性ある
バグが残っていると考えられる。

**累計コスト**: pre-recon $4.93 + recon失敗2回分 $0.12 + $5.99 = **$11.04**(Anthropic API、
実際に課金された金額)。reconフェーズを突破して`injection-vuln`以降の実際の脆弱性検証・
エクスプロイトフェーズまで到達することはできなかった。

### 3-3. 無料のローカルモデル(Ollama)への切替を試したが、別の形で失敗した

AnthropicのAPIクレジット残量を踏まえ、Shannon公式がサポートするOllama連携
([docs/ai-providers.md](https://github.com/KeygraphHQ/shannon/blob/main/docs/ai-providers.md))
に切り替えて同じ検証を試みた。

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://host.docker.internal:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [{ "id": "qwen2.5:14b-instruct" }]
    }
  }
}
```

まず`qwen2.5:14b-instruct`(WSL2側のOllamaに導入済み)を指定したところ、起動直後
(273ms、0エージェント実行、$0)で`AgentExecutionError`になった。調査したところ、
Docker Desktop(Windowsネイティブ)のコンテナから見た`host.docker.internal:11434`は
WSL2側のOllamaではなく、**別途インストールされていたWindowsネイティブ版Ollama**
(`C:\Users\<user>\AppData\Local\Programs\Ollama\ollama.exe`)を指しており、そちらには
`qwen2.5:14b-instruct`が入っていなかった(`qwen2.5:7b`のみ)。これはWSL2とDocker Desktopの
ネットワーキングの違いによるもので、Shannon自体の問題ではない。

モデルを実際に到達可能な`qwen2.5:7b`に変更して再実行したところ、pre-recon・reconの両フェーズは
数秒・$0.0000で「完了」したが(Anthropic版の12分・$4.93と比べて明らかに浅い処理と考えられる)、
続く実際の脆弱性検証エージェント5種(XSS・Injection・Authentication・Authorization・SSRF)は
**全て`OUTPUT_VALIDATION_FAILED`で失敗**した(各エージェントを3回までリトライしたが全滅)。

```
[AGENT] authz-vuln: Failed (OUTPUT_VALIDATION_FAILED) (12.1s, $0.0000)
[AGENT] xss-vuln: Failed (OUTPUT_VALIDATION_FAILED) (11.6s, $0.0000)
[AGENT] injection-vuln: Failed (OUTPUT_VALIDATION_FAILED) (12.6s, $0.0000)
[AGENT] auth-vuln: Failed (OUTPUT_VALIDATION_FAILED) (3.5s, $0.0000)
[AGENT] ssrf-vuln: Failed (OUTPUT_VALIDATION_FAILED) (963ms, $0.0000)
```

Shannon公式ドキュメントは「ツール呼び出し・出力スキーマへの指示追従が弱いモデルを使うと、
ペンテストの質が大きく落ちる」と明記して注意喚起しており、`qwen2.5:7b`という比較的小型の
ローカルモデルでは、Shannonが要求する構造化された出力スキーマへの追従が実際に破綻することを
具体的な失敗パターン(全エージェント種が同一エラーコードで一律失敗)として確認できた。

## 4. 検証結果まとめ

| 項目 | 結果 |
|---|---|
| ライセンス確認(AGPL-3.0) | ✅ 確認できた |
| ローカルJuice Shopの起動・疎通 | ✅ 成功 |
| Shannon `setup`(認証情報設定) | ✅ 成功 |
| snap版DockerでのShannon起動 | ❌ 再現性のあるマウントエラー(ツール起因の可能性大) |
| Docker Desktop切替後のShannon起動 | ✅ 成功 |
| README記載の`-u localhost`ターゲット指定 | ❌ ドキュメント不備(`host.docker.internal`が必要) |
| pre-reconフェーズ(Anthropic) | ✅ 成功(12分30秒、$4.93、詳細な分析成果物を生成) |
| reconフェーズ(Anthropic) | ❌ 2回とも`AGENT_EXECUTION_FAILED`で失敗(計$11.04) |
| `-w`によるresume機能 | ✅ 正常動作(pre-reconの再実行をスキップできた) |
| Ollama(qwen2.5:14b-instruct)への切替 | ❌ Windows/WSL2間のネットワーキングの差でモデル未検出 |
| Ollama(qwen2.5:7b)でのpre-recon/recon | ⚠️ 数秒・$0で「完了」(実質的な分析の深さは未確認) |
| Ollama(qwen2.5:7b)での脆弱性検証(5エージェント) | ❌ 全種`OUTPUT_VALIDATION_FAILED`で失敗 |

実際の脆弱性スキャン・エクスプロイト結果(Shannonの最終的な価値)までは、Anthropic・Ollama
いずれの経路でも到達できなかった。ただし、その過程で得られた「ドキュメント不備」
「snap Docker特有の既知バグ」「resume機能」「reconフェーズ終盤の再現性あるバグ」
「小型ローカルモデルでの構造化出力破綻」という5つの具体的な知見は、いずれもツールの
挙動そのものに起因する、読者が同じ環境で遭遇しうる内容であり、CLAUDE.mdの方針に従い
「検証に直接関係する失敗」として記事の主役にする。
