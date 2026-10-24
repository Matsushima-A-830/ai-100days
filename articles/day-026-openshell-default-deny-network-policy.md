---
title: "NVIDIA OpenShellのdefault-denyネットワークポリシーを実機で検証した"
emoji: "🛡️"
type: "tech"
topics: ["ai", "security", "docker", "agent", "sandbox"]
published: false
---

AIエージェントをサンドボックスで隔離実行するNVIDIA製ランタイム「[OpenShell](https://github.com/NVIDIA/OpenShell)」を実際にインストールし、「ポリシーが無ければ全てのアウトバウンド通信が拒否され、読み取り専用ルールを足すとGETだけ通るようになる」という挙動を、実際のコマンドと構造化ログで確認した。

## OpenShellとは何か

OpenShellは、自律AIエージェントをコンテナ/MicroVM単位のサンドボックスで隔離実行するオープンソースのランタイムである(Apache-2.0、NVIDIA)。宣言的なYAMLポリシーで、ファイルアクセス(Landlock LSM)・システムコール(seccomp)・ネットワーク接続・推論呼び出しをカーネルレベルでdeny-by-default制御し、エージェントは実際の認証情報を直接見ることなく、承認済みのエンドポイント宛の通信にのみ認証情報が付与される。

この連載では当初、クラウドの実行環境でOpenShellを導入しようとしたが、公式インストーラ・PyPI・公式Dockerイメージという3つの標準導入経路すべてが、無人実行環境固有の安全装置・ネットワークポリシーによってブロックされた。これはOpenShell自体の不具合ではなく実行環境側の制約だったため、今回は人間のローカルPC(通常のインターネット接続、WSL2 Ubuntu 24.04.3)で改めて検証した。

## インストール: sudoのパスワード入力が必要だった

公式インストーラをダウンロードして実行すると、GitHub Releaseからネイティブの`.deb`パッケージを取得し、インストールする。

```bash
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh -o /tmp/openshell-install.sh
sh /tmp/openshell-install.sh
```

```
openshell: resolving latest version...
openshell: selected openshell_0.1.5-1_amd64.deb
openshell: installing openshell_0.1.5-1_amd64.deb...
[sudo] password for matsu:
...
openshell: installed openshell package from v0.1.5
✓ Gateway 'openshell' added and set as active
  Endpoint: https://127.0.0.1:17670
```

システムパッケージとしてインストールするため`sudo`の権限が必要で、パスワード入力を求められた。インストールが終わると、ローカルのゲートウェイサービスが自動で起動し、CLIから接続状態を確認できる。

```bash
$ openshell gateway status
Status: Connected
Authentication: Authenticated (mTLS transport)
```

## つまずいた点: 公式の自動デモスクリプトが、デフォルトイメージの前提を欠いていた

OpenShellのリポジトリには、ネットワークポリシーの挙動を1分で体験できる自動デモスクリプト(`examples/sandbox-policy-quickstart/demo.sh`)が同梱されている。まずはこれをそのまま実行してみた。

```
▸ 2/7  Attempting to reach api.github.com — should be DENIED
  $ curl -sS https://api.github.com/zen
  /bin/bash: line 1: curl: command not found
  ✗ Blocked by default-deny policy.
```

一見「ポリシーでブロックされた」ように見えるが、実際はデフォルトのサンドボックスイメージ(`nvcr.io/nvidia/base/ubuntu:24.04`)に`curl`コマンド自体が入っていなかっただけだった。デモスクリプトは`curl`の終了コードが非ゼロであれば無条件に「ブロックされた」と表示するロジックになっており、「コマンドが無い」という失敗と「ポリシーに拒否された」という失敗を区別していない。同梱のREADMEには「`curl`が入ったイメージを使うこと」という前提条件が明記されているが、デモスクリプト自身がその前提を満たすイメージを指定していなかった。

対処として、`curl`が標準で入っている軽量な公開イメージ`curlimages/curl:latest`を明示的に指定し、手順を手動で再現することにした。

## default-deny: ポリシー無しでは何も通らない

```bash
openshell sandbox create --name demo --from curlimages/curl:latest \
  --no-auto-providers --no-tty -- sleep infinity

openshell sandbox exec demo -- curl -sS --max-time 10 https://api.github.com/zen
```

実行すると接続自体が確立できず、`curl`は終了コード7(接続失敗)を返した。ログを見ると、拒否の理由まで構造化された記録として残っていた。

```
NET:OPEN [MED] DENIED /usr/bin/curl(0) -> api.github.com:443 [reason:transparent_tcp_policy_denied]
```

どのバイナリ(`/usr/bin/curl`)が、どの宛先(`api.github.com:443`)への接続を試みて拒否されたかが、1行のログとして確実に残る。

## ポリシーを追加: 無停止でホットリロードされる

読み取り専用のルールを1コマンドで追加する。

```bash
openshell policy update demo \
  --rule-name github_api \
  --binary /usr/bin/curl \
  --add-endpoint api.github.com:443:read-only:rest:enforce \
  --wait
```

```
✓ Policy version 2 submitted (hash: ec35d20221e1)
✓ Policy version 2 loaded (active version: 2)
```

サンドボックスを再起動することなく、数秒でポリシーが反映された。同じ`curl`コマンドを再実行すると、今度は成功する。

```bash
$ openshell sandbox exec demo -- curl -sS --max-time 10 https://api.github.com/zen
Responsive is better than fast.
```

## GETは通るが、POSTはL7で止まる

`read-only`というプリセット名の通り、書き込み系のHTTPメソッドは引き続き拒否される。同じホストに対してPOSTリクエストを送ってみる。

```bash
openshell sandbox exec demo -- curl -sS --max-time 10 -X POST \
  https://api.github.com/repos/octocat/hello-world/issues \
  -H "Content-Type: application/json" -d '{"title":"oops"}'
```

```json
{"error":"policy_denied","policy":"github_api","rule":"POST /repos/octocat/hello-world/issues",
 "detail":"POST /repos/octocat/hello-world/issues not permitted by policy","layer":"l7", ...}
```

興味深いのは、この時`curl`コマンド自体の終了コードは0(成功)だったことだ。TCP接続自体は許可され、OpenShellのプロキシがHTTPレスポンスとして`policy_denied`というJSONボディを返している。ログを見ると、TCP接続レベルの許可とHTTPメソッドレベルの拒否が、別々のイベントとして記録されていた。

```
NET:OPEN  [INFO] ALLOWED /usr/bin/curl(0) -> api.github.com:443 [policy:github_api engine:opa]
HTTP:GET  [INFO] ALLOWED GET https://api.github.com/zen [policy:github_api engine:l7]
NET:OPEN  [INFO] ALLOWED /usr/bin/curl(0) -> api.github.com:443 [policy:github_api engine:opa]
HTTP:POST [MED]  DENIED POST https://api.github.com/repos/octocat/hello-world/issues [policy:github_api engine:l7] [reason:L7_REQUEST deny POST ...]
```

つまりOpenShellは、(1) TCP/ホスト単位の許可(`engine:opa`)と、(2) TLSを終端してHTTPメソッド・パスまで検査するL7レベルの許可(`engine:l7`)という2段階でネットワークアクセスを評価している。`api.github.com`への接続そのものは許可されていても、`read-only`プリセットがGET/HEAD/OPTIONS以外のメソッドを弾くため、同じホストへの書き込み操作だけを選択的に止められることを実機で確認できた。

## まとめ

- クラウドの無人実行環境で3つの標準導入経路すべてをブロックしていた制約は、ローカルPC(通常のインターネット接続、sudo権限あり)には存在せず、OpenShellは公式手順通りにインストール・起動できた。
- 公式の自動デモスクリプトは、デフォルトのサンドボックスイメージに`curl`が入っていないため、そのまま実行すると「ポリシーでブロックされた」という誤った結論を表示する。`curl`入りのイメージを明示的に指定することで正しく再現できた。
- default-deny(全アウトバウンド拒否)→ 読み取り専用ルールの追加(無停止でホットリロード)→ GETは許可・POSTはL7で拒否、という一連の挙動を、実際のコマンド実行と構造化ログの両方で確認した。
- ポリシーはTCP/ホスト単位の許可とHTTPメソッド単位の許可という2段階で評価されており、ホスト全体をアウトバウンド解放しなくても、書き込み系の操作だけを選択的に止められる粒度を持っている。
- 追加の有料APIキーは不要、GPUも不要だった。AIエージェント(OpenRouter連携等)を使ったより発展的な検証は、無料のOpenRouterモデルでも利用登録(アカウント作成・APIキー発行)が必要になるため、今回のスコープには含めていない。

## 出典・ライセンス

- リポジトリ: https://github.com/NVIDIA/OpenShell (Apache-2.0)
- 検証コード・実行ログの全文は[GitHubリポジトリのexperiments/day-026](https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-026)を参照。
