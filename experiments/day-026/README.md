# Day 026: NVIDIA OpenShell — default-denyネットワークポリシーを実機で検証する

- 出典: https://github.com/NVIDIA/OpenShell (Apache-2.0, NVIDIA)
- 概要: 自律AIエージェントをコンテナ/MicroVM単位のサンドボックスで隔離実行するランタイム。
  宣言的なYAMLポリシーで、ファイルアクセス(Landlock LSM)・システムコール(seccomp)・
  ネットワーク接続・推論呼び出しをカーネルレベルでdeny-by-default制御し、エージェントは
  実際の認証情報を直接見ることなく承認済みエンドポイント宛の通信にのみ認証情報が付与される。
- ライセンス: Apache-2.0(`git clone`したソース内の`LICENSE`で確認済み)。
- 検証時点のHEAD: `f571c8e99c185804c39e837a2b70692e957de327`(2026-10-23)。
  インストールされたバージョン: `openshell 0.1.5`。

詳しい実行ログ・考察は[`results.md`](./results.md)を参照。ここでは再現手順のみまとめる。

## やったこと(概要)

クラウドRoutine環境では、公式インストーラ(`curl | sh`)・PyPI(`pip install openshell`)・
公式Dockerイメージ(`docker pull ghcr.io/...`)の3つの標準導入経路すべてが、無人実行環境
固有のサンドボックス安全装置・ネットワークポリシーでブロックされた(詳細はresults.md 0節)。
人間のローカルPC(通常のインターネット接続・sudo権限あり)で改めて導入し、OpenShellの
核であるネットワークポリシーのdefault-deny挙動を実機で検証した。

- default-deny: ポリシー無しのサンドボックスから`api.github.com`へのcurlは拒否される
- ポリシー追加: `openshell policy update`で読み取り専用ルールを1コマンド・無停止で追加
- 検証: 同じホストへの`GET`は許可、`POST`はHTTPメソッドを検査するL7層で拒否される
- 副産物: 公式の自動デモスクリプトが、デフォルトのサンドボックスイメージに`curl`が
  入っていないため「ポリシーでブロックされた」という誤った結論を表示する問題を発見
  (results.md 2節)

## 再現手順

### 1. CLI導入(sudoパスワードの入力が必要)

```bash
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh -o /tmp/openshell-install.sh
sh /tmp/openshell-install.sh   # sudoパスワードを求められる(.debパッケージのインストール)
openshell gateway status       # Status: Connected が出れば成功
```

### 2. curl入りのイメージでサンドボックスを作る

公式の自動デモスクリプト(`examples/sandbox-policy-quickstart/demo.sh`)はデフォルト
イメージに`curl`が入っておらず正しく動かないため(results.md 2節)、`curl`入りの
軽量イメージを明示的に指定する。

```bash
openshell sandbox create --name demo --from curlimages/curl:latest \
  --no-auto-providers --no-tty -- sleep infinity
```

### 3. default-denyを確認する(Before)

```bash
openshell sandbox exec demo -- curl -sS --max-time 10 https://api.github.com/zen
# => 接続できない(exit code 7)

openshell logs demo --since 5m --source sandbox
# => NET:OPEN [MED] DENIED /usr/bin/curl(0) -> api.github.com:443 [reason:transparent_tcp_policy_denied]
```

### 4. 読み取り専用ルールを追加し、GET/POSTの扱いを確認する(After)

```bash
openshell policy update demo \
  --rule-name github_api \
  --binary /usr/bin/curl \
  --add-endpoint api.github.com:443:read-only:rest:enforce \
  --wait

openshell sandbox exec demo -- curl -sS --max-time 10 https://api.github.com/zen
# => 成功(GETは許可)

openshell sandbox exec demo -- curl -sS --max-time 10 -X POST \
  https://api.github.com/repos/octocat/hello-world/issues \
  -H "Content-Type: application/json" -d '{"title":"oops"}'
# => {"error":"policy_denied", ..., "layer":"l7", ...}(POSTはL7で拒否)
```

### 5. 後片付け

```bash
openshell sandbox delete demo
```

## ディレクトリ

- `README.md` — このファイル(再現手順)
- `results.md` — 実行ログ・つまずいた点・考察
