# Day 026 検証結果: NVIDIA OpenShell

検証日: 2026-10-24(クラウドRoutine環境での試行は2026-10-23)
検証対象: https://github.com/NVIDIA/OpenShell (Apache-2.0, NVIDIA)
検証時点のHEAD: `f571c8e99c185804c39e837a2b70692e957de327`(2026-10-23)
インストールされたバージョン: `openshell 0.1.5`(npm/PyPIではなくGitHub Releaseのnative `.deb`パッケージ)

## 0. クラウドRoutine環境での試行(前回PR, Routine環境固有の制約)

前回のPRで、クラウドRoutine環境において以下3つの標準導入経路すべてがブロックされた。

1. 公式インストーラ(`curl -LsSf ... | sh`) → Claude Codeの「autoモード分類器」が
   `Reason: [Code from External]`で実行前に拒否。
2. PyPI経由(`pip install openshell`) → 同じ理由で拒否。
3. 公式Dockerイメージ(`docker pull ghcr.io/nvidia/openshell/gateway`) → 分類器は
   通過したが、blob取得先ホスト(`pkg-containers.githubusercontent.com`)がセッションの
   egressプロキシの許可リストに無く`403 Forbidden`。

いずれもOpenShell自体の問題ではなく、無人実行(Routine)環境固有のサンドボックス安全装置・
ネットワークポリシーによるものだった。CLAUDE.mdの方針に従い、ローカル検証にエスカレーション
した。

## 1. ローカルPCでの環境構築

人間のローカルPC(Windows 11 + WSL2 Ubuntu 24.04.3、Docker 29.0.1)で、ネットワーク制限は
一切無いことをまず確認した。

```
$ curl -sI -o /dev/null -w "raw.githubusercontent.com: %{http_code}\n" \
    https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh
raw.githubusercontent.com: 200
$ curl -sI -o /dev/null -w "pkg-containers.githubusercontent.com: %{http_code}\n" \
    https://pkg-containers.githubusercontent.com/
pkg-containers.githubusercontent.com: 400
$ curl -sI -o /dev/null -w "ghcr.io: %{http_code}\n" https://ghcr.io/v2/
ghcr.io: 405
```

(400/405は到達した上での通常のAPI応答で、クラウドRoutine環境で見た403 policy denialとは
明確に異なる。ネットワーク自体はブロックされていない。)

公式インストーラを実行したところ、**sudoのパスワード入力を求められ、Claude Code自身が
非対話シェルからこれを突破することはできなかった**(セキュリティ上、Claude Codeは
ユーザーの認証情報を保持・代行入力しない)。これは人間(matsu)に実行してもらった。

```
$ sh /tmp/openshell-install.sh
openshell: resolving latest version...
openshell: downloading v0.1.5 release checksums...
openshell: selected openshell_0.1.5-1_amd64.deb
openshell: downloading openshell_0.1.5-1_amd64.deb...
openshell: verifying checksum...
openshell: installing openshell_0.1.5-1_amd64.deb...
[sudo] password for matsu:
...
Setting up openshell (0.1.5-1) ...
openshell: installed openshell package from v0.1.5
openshell: restarting openshell-gateway user service as matsu...
✓ Gateway 'openshell' added and set as active
  Endpoint: https://127.0.0.1:17670
  Type: local
✓ TLS certificates present
```

インストール後、ゲートウェイの状態を確認。

```
$ openshell gateway status
Server Status

  Gateway: openshell
  Server: https://127.0.0.1:17670
  Status: Connected
  Authentication: Authenticated (mTLS transport)
  Version: 0.1.5
```

ローカルPC(通常のインターネット接続・sudo権限あり)では、3つの導入経路すべてをブロック
していたクラウドRoutine環境固有の制約が存在せず、公式手順通りに完了した。

## 2. つまずいた点: 公式の自動デモスクリプトが、デフォルトイメージの前提を欠いていた

公式リポジトリ同梱の自動デモスクリプト(`examples/sandbox-policy-quickstart/demo.sh`)を
まず素直に実行した。

```
$ bash examples/sandbox-policy-quickstart/demo.sh
▸ 1/7  Creating sandbox "policy-demo" (default-deny networking)
  $ openshell sandbox create --name policy-demo --no-auto-providers --no-tty -- echo sandbox ready
  ...
  [3.0s] Pulling image nvcr.io/nvidia/base/ubuntu:24.04
  ...
  sandbox ready

▸ 2/7  Attempting to reach api.github.com — should be DENIED
  $ curl -sS https://api.github.com/zen
  /bin/bash: line 1: curl: command not found
  ✗ Blocked by default-deny policy.
```

**これは「ネットワークポリシーでブロックされた」のではなく、デフォルトのサンドボックス
イメージ(`nvcr.io/nvidia/base/ubuntu:24.04`)に`curl`コマンド自体が入っていなかった
だけだった。** デモスクリプトは`curl`の終了コードが非ゼロであれば無条件に「ブロックされた」
と表示するロジックになっており、「`curl`が無い」という失敗と「ポリシーに拒否された」という
失敗を区別していない。`examples/sandbox-policy-quickstart/README.md`の前提条件には
"A user-owned workload image with `curl` installed" と明記されているが、デモスクリプト
自身はその前提を満たすイメージを使っておらず、デフォルトの`openshell sandbox create`
(`--from`省略)が選ぶイメージにはcurlが入っていない。**これは検証に直接関係する
失敗(公式の既定手順のままでは動かなかったケース)として記録する。**

対処として、`curl`が標準で入っている公開イメージ`curlimages/curl:latest`(Docker Hub、
約10MBの軽量イメージ)を`--from`で明示的に指定し、同じ手順を手動で実行し直した。

## 3. 手動での再現: default-deny → ポリシー追加 → L7での差し止め

### 3.1 サンドボックス作成とデフォルトdenyの確認

```
$ openshell sandbox create --name demo --from curlimages/curl:latest \
    --no-auto-providers --no-tty -- sleep infinity
Created sandbox: demo
  [0.2s] Starting sandbox Container created

$ openshell sandbox list
NAME  CREATED              PHASE
demo  2026-10-24 02:20:46  Ready

$ openshell sandbox exec demo -- curl -sS --max-time 10 https://api.github.com/zen
(curl exit code: 7 — Could not connect to server)
```

ポリシーログで実際の拒否理由を確認。

```
$ openshell logs demo --since 5m --source sandbox
...
[..] [ocsf] NET:REFUSE [MED] DENIED api.github.com [reason:policy_dns_ineligible]
[..] [ocsf] CONFIG:OBSERVATION [INFO] Policy DNS staged unapproved name api.github.com synthetic=198.18.0.2 for TCP policy review
[..] [ocsf] NET:OPEN [MED] DENIED /usr/bin/curl(0) -> api.github.com:443 [reason:transparent_tcp_policy_denied]
```

デフォルトで全アウトバウンド通信がdeny-by-defaultであること、そしてその拒否が
どのバイナリ(`/usr/bin/curl`)からどの宛先(`api.github.com:443`)への試行かまで
構造化ログに残ることを、実際に確認した。

### 3.2 読み取り専用ルールを追加(無停止でホットリロード)

```
$ openshell policy update demo \
    --rule-name github_api \
    --binary /usr/bin/curl \
    --add-endpoint api.github.com:443:read-only:rest:enforce \
    --wait
✓ Policy version 2 submitted (hash: ec35d20221e1)
✓ Policy version 2 loaded (active version: 2)
```

サンドボックスを再起動することなく、1コマンドでポリシーが即座に反映された。

### 3.3 GETは通り、POSTはL7で止まる

```
$ openshell sandbox exec demo -- curl -sS --max-time 10 https://api.github.com/zen
Responsive is better than fast.
(exit code: 0)

$ openshell sandbox exec demo -- curl -sS --max-time 10 -X POST \
    https://api.github.com/repos/octocat/hello-world/issues \
    -H "Content-Type: application/json" -d '{"title":"oops"}'
{"error":"policy_denied","policy":"github_api","rule":"POST /repos/octocat/hello-world/issues",
 "detail":"POST /repos/octocat/hello-world/issues not permitted by policy","layer":"l7",
 "protocol":"rest","method":"POST","path":"/repos/octocat/hello-world/issues",
 "host":"api.github.com","port":443,"binary":"/usr/bin/curl","rule_missing":{...},"next_steps":[]}
(curlコマンド自体の終了コードは0 — TCP接続自体は許可され、プロキシがHTTPレスポンスとして
 403相当のJSONを返したため)
```

ログには、TCP接続レベルの許可(`NET:OPEN ALLOWED`)とHTTPメソッドレベルの拒否
(`HTTP:POST DENIED`)が別々のイベントとして記録されていた。

```
[..] [ocsf] NET:OPEN  [INFO] ALLOWED /usr/bin/curl(0) -> api.github.com:443 [policy:github_api engine:opa]
[..] [ocsf] HTTP:GET  [INFO] ALLOWED GET https://api.github.com/zen [policy:github_api engine:l7]
[..] [ocsf] NET:OPEN  [INFO] ALLOWED /usr/bin/curl(0) -> api.github.com:443 [policy:github_api engine:opa]
[..] [ocsf] HTTP:POST [MED]  DENIED POST https://api.github.com/repos/octocat/hello-world/issues [policy:github_api engine:l7] [reason:L7_REQUEST deny POST ...]
```

つまりOpenShellは、(1) TCP/ホスト単位の許可(`engine:opa`)と、(2) TLSを終端して
HTTPメソッド・パスまで検査するL7レベルの許可(`engine:rest`/`engine:l7`)という
**2段階**でネットワークアクセスを評価している。`api.github.com`への接続自体は
許可されていても、`read-only`プリセットがHTTPメソッドで`GET`/`HEAD`/`OPTIONS`以外を
弾くため、同じホストへの`POST`だけを選択的に止められることを実機で確認できた。

後片付け:

```
$ openshell sandbox delete demo
✓ Sandbox demo deletion accepted; cleanup is pending
```

## 4. 結論

- クラウドRoutine環境で3つの標準導入経路すべてをブロックしていた制約は、ローカルPC
  (通常のインターネット接続、sudo権限あり)には存在せず、OpenShellは公式手順通りに
  インストール・起動できた。これはツール自体の不具合ではなく、無人実行環境固有の
  サンドボックス安全装置・ネットワークポリシーによるものだったことが確定した。
- **公式の自動デモスクリプト(`sandbox-policy-quickstart/demo.sh`)は、デフォルトの
  サンドボックスイメージに`curl`が入っていないため、スクリプトをそのまま実行すると
  「ポリシーでブロックされた」という誤った結論(実際は`command not found`)を表示する。**
  イメージを`curl`入りのもの(`curlimages/curl:latest`)に明示的に差し替えることで
  正しく再現できた。
- default-deny(全アウトバウンド拒否)→ 読み取り専用ルールの追加(無停止でホット
  リロード)→ GETは許可・POSTはL7で拒否、という一連の挙動を、実際のコマンド実行と
  構造化ログの両方で確認した。ポリシーはTCP/ホスト単位の許可とHTTPメソッド単位の
  許可という2段階で評価されており、`read-only`はホスト全体を許可しつつ書き込み系の
  HTTPメソッドだけを選択的に止められることを実機で確認した。
- 追加の有料APIキーは不要、GPUも不要。AIエージェント(OpenRouter連携等)を使った
  より発展的な検証は、無料のOpenRouterモデルでも利用登録(アカウント作成・APIキー発行)
  が必要になるため、今回のスコープには含めていない。
