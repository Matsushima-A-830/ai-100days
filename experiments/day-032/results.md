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
