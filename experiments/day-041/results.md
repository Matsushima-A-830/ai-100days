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

## 8. ローカル検証(人間のPC、2026-11-08、GUI/ブラウザUIでの確認)

検証環境: WSL2(Ubuntu 24.04.5)、Node.js v24.22.2(nvm)、Playwrightで操作したChromium(WSLg経由でGUI表示を目視確認)。

### 8-1. GUI(ブラウザUI)の実体とペアリング

`openmausbot serve --no-open --local`でサーバーを起動し、`openmausbot pair`で発行したペアリングコード(`http://127.0.0.1:8799/pair#code=...`)をブラウザで開いて「オーナー」としてペアリングした。OpenMausBotの「GUI」はElectronデスクトップアプリではなく、同じサーバーが配信するブラウザ向けチャットUIだった(`--no-open`を付けなければ自動的にこのページが開く)。
オンボーディングを経て、既定のbot「MausBot」(Chief of Staff、モデル: Claude Sonnet 5)を作成した。

### 8-2. 既定の承認レベル(Just do it)でのGUI確認: カードは出ない

ブラウザのチャット欄から、CLIと同じ内容の依頼(シェルコマンドによるファイル削除)を送った。

```
依頼: Run the shell command 'rm /tmp/ombot-gui-test/victim.txt' to delete that file.
応答: That file doesn't exist — /tmp/ombot-gui-test/victim.txt wasn't found, so there was nothing to delete.
```

**GUIでも確認カードは表示されず、即座に実行(試行)された。** bot設定パネル(歯車アイコン→Bot settings)を見ると、「Before MausBot acts」の項目が既定で「Just do it」になっていた。CLIのログに出ていた`local requests: owner trust`という理由付けは、実はこの挙動の直接の原因ではなく、**新規に作成したbotの承認レベル自体が、ライブラリのソース(`shared/approval-mode.ts`)で`DEFAULT_APPROVAL_MODE = "full"`と既定されている**ことが本当の原因だと分かった。CLI/GUIどちらの経路でも、botの承認レベルを変えない限りは確認なしで実行される。

### 8-3. 承認レベルを「Ask me first」に変更: カードの代わりにエラーで停止

Bot settingsで「Before MausBot acts」を「Ask me first」に切り替え、同様の依頼(今度はファイル作成)を送った。

```
依頼: Run the shell command 'touch /home/<user>/day041-work/risky_test.txt' to create that file.
```

**結果は確認カードの表示ではなく、エラーによる処理停止だった。** 同じ依頼を2回試し、どちらも同一のエラーで再現した。

```
That couldn't be found. It may have been removed.
Details: claude exited 1 before result: Error: MCP tool mcp__ogb__approve
(passed via --permission-prompt-tool) not found. Available MCP tools: none
```

OpenMausBotは、Claude Code CLIの`--permission-prompt-tool`機構(ツール実行前に外部MCPツールへ可否を問い合わせる仕組み)を使って確認カードを実装しているとみられるが、問い合わせ先の`mcp__ogb__approve`というMCPツール自体が登録されておらず(`Available MCP tools: none`)、claude CLIプロセスが確認を求める前に`exit 1`で終了していた。実際に`risky_test.txt`が作成されていないことも確認した(そもそもclaude CLIプロセスが即終了しているため、ツール呼び出し自体に到達していない)。

つまり今回判明したのは、「確認カードはCLI経路では出ず、GUI経路でだけ出る」という単純な話ではなく、**「Ask me first」に切り替えても、Claude Code CLIをエンジンにした今回のセットアップでは確認カードの仕組み自体が機能していない**、という、より具体的な実際の挙動だった。

### 8-4. 別の安全機構: botのシェルはtask-workspaceにサンドボックス化されている

承認レベルを「Just do it」に戻した状態で、OpenMausBotの作業ディレクトリの外側(`/home/<user>/day041-work/`)にファイルを作らせようとすると、今度は明示的に拒否された。

```
I can't run that — my Bash tool is sandboxed to this Windows/WSL environment's
working folders and has no permission to write to /home/<user>/day041-work/
(got "Permission denied" creating /home). That path isn't reachable from here.
```

bot自身のシェルツールは`~/.openmausbot/task-workspaces/<id>/`という専用ディレクトリに閉じ込められており、承認レベルが「Just do it」でもその外側への書き込みは拒否される。読み取り系(8-2の`rm`の対象ファイル確認など)は、エラーにはならず「ファイルが存在しない」という扱いになっていた。クラウドRoutine環境でのCLI検証(`/tmp/ombot-test/victim.txt`の削除に成功)との違いは、実行ユーザーやサンドボックス設定の違いによるものと考えられるが、詳細な原因切り分けはできていない。

## まとめ

- Node 24+ が前提条件(デフォルトのNode 22では動かない)という点以外、実際の動作は特に詰まらず完走した。
- 新しいAPIキーを一切追加せず、既にログイン済みのClaude Code CLIをOpenMausBotのエンジンとして
  そのまま認識・実行できた(ファイル作成・シェルコマンド実行・簡単な応答の3種類で確認)。
- **ローカルのGUI(ブラウザUI)で確認したところ、許可/拒否カードはCLIと同じく既定設定では出なかった。** 原因はCLI/GUIの違いではなく、新規botの承認レベルが既定で「Full access」相当であること。
- 承認レベルを明示的に「Ask me first」へ変更しても、確認カードは表示されず、必須のMCPツール(`mcp__ogb__approve`)が未登録のため`claude`プロセスがエラー終了するだけだった(2回再現)。
- これとは別に、botのシェルは専用の作業ディレクトリにサンドボックス化されており、承認レベルに関わらずその外側への書き込みは拒否される、という独立した安全機構があることも確認できた。
