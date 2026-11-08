# Day 041 results — milind-soni/OpenMausBot

出典: https://github.com/milind-soni/OpenMausBot (Apache-2.0。`enterprise/`配下のみ別のsource-availableライセンス)
npm: https://www.npmjs.com/package/openmausbot (version 0.1.148)

検証環境: Ubuntu 24.04.5 LTS (クラウドRoutine実行コンテナ)、Node.js v22.23.4(デフォルト)/ v24.22.1(`/opt/node24`、別途用意されていたもの)。

## 1. 前提条件の確認

```
$ npm view openmausbot engines version description
engines = { node: '>=24' }
version = '0.1.148'
description = 'Run the OpenMausBot server anywhere and pair your devices to it'
```

この実行環境のデフォルトnodeは v22.23.4 で `>=24` を満たさない。
`/opt/node24`(v24.22.1)が別途用意されていたため、以降はこちらの node/npm を `PATH` の先頭に置いて使用した。
(ローカルPCで再現する場合、Node 24+ が入っていなければ nvm/fnm 等で用意する必要がある。)

## 2. インストールと起動

```
$ npm install openmausbot
added 9 packages, and audited 10 packages in 3s
found 0 vulnerabilities
```

`node_modules/openmausbot/cli.js` の中身は `import "./dist-server/openmausbot.js";` の1行だけで、
実体は `dist-server/` 配下にビルド済みで入っている。

`openmausbot --help` は問題なく表示され、`openmausbot doctor --host` でホスト診断も実行できた:

```
$ node node_modules/openmausbot/cli.js doctor --host
ok    Ubuntu 24.04.5 LTS, kernel 6.18.44-fc-v310
ok    x86_64
FAIL  Docker is installed, but its daemon is not running
      fix: sudo systemctl enable --now docker
ok    Unprivileged user namespaces are allowed
ok    seccomp is available
FAIL  Only cgroup v1 is mounted; the bot box needs cgroup v2
      fix: boot with systemd.unified_cgroup_hierarchy=1 (the default since Ubuntu 21.10 and Debian 11)
warn  31 GB free for /root/.openmausbot; a Team server needs 100 GB
warn  /root/.openmausbot is not on an encrypted disk
ok    4 CPUs, 16 GB memory (a team of 20 needs 8 CPUs and 16 GB)
ok    Port 8799 is free for the server
ok    Ports 80 and 443 are free
warn  Could not check the clock
2 problems, 3 warnings.
(exit code 7)
```

Docker未起動・cgroup v1のみという2件のFAILは、このクラウドRoutine実行コンテナ固有の制約
(systemdなしのネストしたコンテナで、cgroup v2・dockerdの常時起動が前提に合わない)であり、
一般的なLinux環境(systemd・cgroup v2・Docker常用)では通常問題にならないと考えられる。
実際、この「bot box」(サンドボックス実行用コンテナ)はクラウド共有サーバー向けの機能で、
後述のとおり自分専用のローカル実行(`--local`)では無効化されて動作に影響しなかった。

## 3. サーバーをヘッドレスで起動

```
$ node node_modules/openmausbot/cli.js serve --no-open --local
bot box: off (not-cloud)
openmausbot webhook receiver on http://127.0.0.1:8800
openmausbot open-source edition (enterprise layer present but OMB_LICENSE_KEY is not set)
local requests: owner trust (self-hosted default)
brand: default
openmausbot server on http://127.0.0.1:8799

MausBot 0.1.148 · server "vm"
data: /root/.openmausbot
browser engine: unavailable (agent-browser is not installed on this machine yet)

Listening on 127.0.0.1:8799, reachable from this machine only.
```

GUI(ブラウザ/Electron)を一切開かずにサーバーが起動し、`curl -s http://127.0.0.1:8799/` が `200` を返した。
デフォルトのbot「MausBot」(役割: Chief of Staff)が最初から1つ用意されていた。

## 4. エンジン検出(claude CLIが認識されるか)

```
$ openmausbot doctor
OpenMausBot 0.1.148 ("vm") at http://127.0.0.1:8799: ready
You are: this computer (the owner)
Engines available: claude
Bots' browser: not available
warning: bots have no built-in browser here: agent-browser is not installed on this machine yet
```

```
$ openmausbot models
(27エンジンが一覧表示され、"available"だったのは claude · available · default claude-sonnet-5 · 8 models の1件のみ。
 他26種はchatgpt/codex/grok/droid/cursor等いずれも"unavailable"。)
```

このRoutine自身が使っている `claude` CLI(既にログイン済み)を、追加の設定・APIキーなしでOpenMausBotが
そのまま検出して「available」と表示した。新しい秘密情報・APIキーは一切追加していない。

## 5. 実際にタスクを実行(claudeエンジン経由)

### 5-1. ファイル作成

```
$ openmausbot run MausBot "ワークスペースのホームディレクトリに hello_from_mausbot.txt というファイルを作り、内容を 'OpenMausBot day-041 verification' にしてください。作成後、ファイルの内容を教えてください。" --wait job --timeout 50s
Done: MausBot finished

ファイルを作成しました。
内容: `OpenMausBot day-041 verification`
パス: `/root/.openmausbot/task-workspaces/83ab7cbf-364d-4196-94e9-262e9436e640/fb169e18-f8d0-4c98-8cd4-06b2e95ce1d5/hello_from_mausbot.txt`
```

実際にそのパスを `cat` して内容が `OpenMausBot day-041 verification` であることを確認した(一致)。

### 5-2. シェルコマンド実行(ファイル削除)

事前に `/tmp/ombot-test/victim.txt` を作成したうえで、以下を依頼した。

```
$ openmausbot run MausBot "シェルコマンド 'rm /tmp/ombot-test/victim.txt' を実行してファイルを削除してください。" --wait job --on-input exit --timeout 50s
Done: MausBot finished
削除しました: `/tmp/ombot-test/victim.txt`
```

`ls /tmp/ombot-test/` で実際にファイルが削除されていることを確認した。

**重要な所見:** today.mdでは「許可/拒否カードの挙動」を確認する想定だったが、
起動ログに出ていた `local requests: owner trust (self-hosted default)` のとおり、
セルフホストでオーナー本人として使っている今回の構成では、ファイル削除のような操作でも
確認カードは出ず、即座に実行された。許可/拒否カードはGUI(デスクトップアプリ/ブラウザUI)側の
機能であり、CLI単体でオーナーとして動かす今回の経路では提示されない、というのが実際の挙動だった。

### 5-3. 単純な応答とレイテンシ

```
$ time openmausbot run MausBot "1+1は何ですか?短く答えてください。" --wait job --timeout 50s
Done: MausBot finished
2
real	0m2.811s
```

claude CLIを裏で呼び出し、1往復(起動〜応答〜終了)が約2.8秒だった。

## 6. ライセンス確認

ルートは Apache License 2.0(`LICENSE`)。`enterprise/` 配下のみ別ライセンスで、
`enterprise/LICENSE` には「評価目的の閲覧・ビルド・改変は無料だが、本番でenterprise機能を使うには
有償ライセンスキーが必要」と明記されている。今回検証したサーバー起動・エンジン検出・run実行は
いずれもこの `enterprise/` を使わないOSS部分の機能であり、`OMB_LICENSE_KEY` も設定していない
(起動ログにも "enterprise layer present but OMB_LICENSE_KEY is not set" と出ている)。
有料APIキーは一切使用・取得していない。

## 7. 後片付け

検証後、`serve` プロセス(親・子2プロセス)を停止し、`/tmp/ombot-test/` と作業用の `sandbox/` ディレクトリを削除した。
`experiments/day-041/` にはこの `results.md` と `README.md` のみを残している(node_modules等はコミットしていない)。

## まとめ

- Node 24+ が前提条件(デフォルトのNode 22では動かない)という点以外、実際の動作は特に詰まらず完走した。
- 新しいAPIキーを一切追加せず、既にログイン済みのClaude Code CLIをOpenMausBotのエンジンとして
  そのまま認識・実行できた(ファイル作成・シェルコマンド実行・簡単な応答の3種類で確認)。
- 許可/拒否カードはCLI単体のオーナー実行では提示されず、確認なしに実行された点は、
  想定(today.mdのメモ)と異なる実際の挙動として記録しておく。
