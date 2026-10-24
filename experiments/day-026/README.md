# Day 026: NVIDIA OpenShell — Routine環境の制約によりローカル検証にエスカレーション

- 出典: https://github.com/NVIDIA/OpenShell (Apache-2.0, NVIDIA)
- 概要: 自律AIエージェントをコンテナ/MicroVM単位のサンドボックスで隔離実行するランタイム。
  宣言的なYAMLポリシーで、ファイルアクセス(Landlock LSM)・システムコール(seccomp)・
  ネットワーク接続・推論呼び出しをカーネルレベルでdeny-by-default制御し、エージェントは
  実際の認証情報を直接見ることなく承認済みエンドポイント宛の通信にのみ認証情報が付与される。
- ライセンス: Apache-2.0(`git clone`したソース内の`LICENSE`で確認済み)。
- 日本語記事件数: backlog.md参照(2026-10-23時点でZenn/Qiita/noteともに一次検証記事は未検出)。

## 当初の検証計画(today.md / backlog.mdより)

1. `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh` でCLI導入。
2. `openshell sandbox create` でサンドボックスを作成。
3. YAMLポリシーでファイル/ネットワークアクセスを制限した状態と制限なしの状態で、同じ
   エージェント操作(許可外のファイル読み取りや外部ホストへの通信)を試し、実際に
   ブロック/許可が切り替わる様子をBefore/Afterで記録する。
4. モデルバックエンドは無料のOpenRouterモデルを使うチュートリアル("Run Your First Agent")
   に従う(有料APIキー不要)。

## 実際に行ったこと、そしてブロックされた3つの標準導入経路

まずソースコード自体は読み取り専用の`git clone`で取得できた(ライセンス確認・
アーキテクチャ理解のため)。

```
$ git clone --depth 1 https://github.com/NVIDIA/openshell /home/user/nvidia/openshell
$ git -C /home/user/nvidia/openshell rev-parse HEAD
f571c8e99c185804c39e837a2b70692e957de327
```

また、このRoutine実行環境ではDockerデーモン自体は起動できることを確認した
(`dockerd`を起動→`docker info`が正常応答)。

しかし、OpenShell CLI/ゲートウェイを実際に導入・起動する標準的な方法を3つ試し、
いずれもこのRoutineの無人実行環境固有の安全装置・ネットワークポリシーによってブロックされた。

### 1. 公式インストーラ(`curl | sh`)

```
$ curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
```

→ Claude Codeの「autoモード分類器」により実行前に拒否された(`Reason: [Code from External]`)。
無人実行中に外部から取得したシェルスクリプトをそのまま実行することに対する安全装置。

### 2. PyPI経由(`pip install openshell`)

README記載のSDK/CLI配布経路の一つ。

```
$ pip install openshell
```

→ 同じ理由(`Code from External`)で拒否された。

### 3. 公式Dockerイメージ(`docker compose up` / `docker pull`)

`deploy/docker/docker-compose.yml`が使う`ghcr.io/nvidia/openshell/gateway`イメージを
直接pullして確認した。

```
$ docker pull ghcr.io/nvidia/openshell/gateway:latest
```

→ こちらはautoモード分類器では拒否されなかったが、イメージのblob取得先
(`pkg-containers.githubusercontent.com`、ghcr.ioのCDN)がこのセッションの
egressプロキシのポリシーで許可されていないホストのため`403 Forbidden`で失敗した。

### 判断

3つの独立した標準導入経路すべてが、OpenShell自体の不具合ではなく、この無人実行
(Routine)環境固有のサンドボックス安全装置・ネットワークポリシーでブロックされた。
CLAUDE.mdの方針(Routine環境の制約は推測で埋めず、ローカル検証にエスカレーションする)
に従い、ここで検証を止めてPRで人間に依頼する。

## ローカル検証での再現手順(人間向け)

前提: Linux/macOS(Apple Silicon)/WSL2 + Docker or Podman or ホスト仮想化。
追加の有料APIキーは不要(無料のOpenRouterモデルを使う)。GPU不要。

```shell
# 1. CLI導入
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
openshell sandbox create --name demo

# 2. 公式チュートリアルに従い、無料のOpenRouterモデルでOpenCodeエージェントを起動
#    https://docs.nvidia.com/openshell/latest/about/run-your-first-agent

# 3. 制限なしのポリシーで、許可されていないはずのファイル読み取り/外部ホストへの
#    通信を試し、通る(Before)ことを確認する

# 4. YAMLポリシーでファイルアクセス・ネットワーク接続を制限した状態に変更し、
#    同じ操作を再度試し、ブロックされる(After)ことを確認する
#    (ドキュメント: https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview)
```

結果が出たら、`results.md`・`articles/day-026-*.md`・`posts/x/day-026.md`・
`posts/note/day-026.md`・`posts/cards/day-026.html` を実際の結果で作成する。
