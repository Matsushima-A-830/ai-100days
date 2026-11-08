---
title: "Grok Botの代わりに、手元のClaude Code CLIをそのままチャットのバックエンドにしてみた"
emoji: "🐭"
type: "tech"
topics: ["ai", "llm", "claudecode", "oss", "nodejs"]
published: false
---

## 概要

2026-11-07付でGitHub TrendingのTypeScript部門で最多の伸び(+1,986 star/日)を記録していた[milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot) を実際に動かしてみた。

このツールは、xAIのGrok Bot(クローズドソースで、使えるモデルがxAI系に固定されたチャットアプリ)を意識して作られたOSS版チャットアプリで、Apache License 2.0で公開されている(`enterprise/`配下のみ別のsource-availableライセンスで、本番でのenterprise機能利用には有償ライセンスキーが必要)。

一番の特徴は、チャットの裏側で動くエンジンが`claude`・`codex`・`grok`といった手元のエージェントCLIそのものであること。自分のPCやサーバーに既にログイン済みのサブスクリプションをそのまま使い、新しいAPIキーを発行する必要がない。

筆者はいつもClaude Code CLIで検証作業をしているので、「このCLI自身を、別のOSSチャットアプリのバックエンドとしてそのまま流用できるか」を確かめてみた。

## 検証環境と前提

- 出典: https://github.com/milind-soni/OpenMausBot
- npm: https://www.npmjs.com/package/openmausbot (v0.1.148)
- ライセンス: Apache License 2.0(`enterprise/`配下のみ別ライセンス、未使用)
- OS: Ubuntu 24.04.5 LTS
- 有料APIキーは一切使用・追加していない。既にログイン済みのClaude Code CLIをそのまま使っただけ。

まず`npm view`で前提条件を確認した。

```
$ npm view openmausbot engines version
engines = { node: '>=24' }
version = '0.1.148'
```

Node.js 24以上が前提になっている。手元の環境のデフォルトNodeがこれより古い場合は、nvmやfnmなどで24+を用意する必要がある。筆者の検証環境でも、デフォルトのNodeは22系だったため、別途用意されていたNode 24系の実行ファイルを使った。

## インストールとヘッドレス起動

```
$ npm install openmausbot
added 9 packages, and audited 10 packages in 3s
found 0 vulnerabilities
```

インストール自体は数秒で終わる。GUI(デスクトップアプリ)を使わず、ブラウザも開かずにサーバーだけを起動できるオプションがある。

```
$ npx openmausbot serve --no-open --local
bot box: off (not-cloud)
local requests: owner trust (self-hosted default)
openmausbot server on http://127.0.0.1:8799

MausBot 0.1.148 · server "vm"
Listening on 127.0.0.1:8799, reachable from this machine only.
```

`curl http://127.0.0.1:8799/`が`200`を返すことを確認した。デフォルトのbot「MausBot」(役割: Chief of Staff)が最初から1つ用意されている。

## エンジン検出: 既にログイン済みのclaude CLIがそのまま使えるか

ここが今回の本題。`doctor`コマンドで、このサーバーがどのエージェントCLIを「エンジン」として認識しているかを確認した。

```
$ openmausbot doctor
OpenMausBot 0.1.148 ("vm") at http://127.0.0.1:8799: ready
You are: this computer (the owner)
Engines available: claude
```

```
$ openmausbot models
(27種のエンジンが一覧表示され、"available"だったのは
 claude · available · default claude-sonnet-5 · 8 models の1件のみ)
```

27種類のエンジン(chatgpt・codex・grok・droid・cursorなど)が一覧表示される中、実際に「available」と判定されたのは`claude`だけだった。これは、このマシンに既にログイン済みのClaude Code CLIをOpenMausBotが検出した結果であり、筆者は新しいAPIキーも設定ファイルも一切追加していない。

## 実際にタスクを実行させてみる

`run`コマンドでbotに1つジョブを投げ、完了まで待つ。

```
$ openmausbot run MausBot "ワークスペースのホームディレクトリに hello_from_mausbot.txt という \
ファイルを作り、内容を 'OpenMausBot day-041 verification' にしてください。作成後、ファイルの \
内容を教えてください。" --wait job --timeout 50s
Done: MausBot finished

ファイルを作成しました。
内容: `OpenMausBot day-041 verification`
パス: `/root/.openmausbot/task-workspaces/.../hello_from_mausbot.txt`
```

実際にそのパスを`cat`し、内容が一致することを確認した。裏側では間違いなくclaude CLIが起動し、ファイル作成というエージェント的な操作を実行している。

続けて、事前に用意したファイルをシェルコマンドで削除させてみた。

```
$ openmausbot run MausBot "シェルコマンド 'rm /tmp/ombot-test/victim.txt' を実行してファイルを \
削除してください。" --wait job --on-input exit --timeout 50s
Done: MausBot finished
削除しました: `/tmp/ombot-test/victim.txt`
```

`ls`で実際にファイルが消えていることを確認した。

ここで一つ、想定と違う挙動があった。OpenMausBotはシェル実行やファイル編集などの危険な操作について許可/拒否カードで確認を求める、という説明を事前に読んでいたので、ファイル削除の際に何らかの確認が入ると予想していた。しかし実際には、起動ログに出ていた`local requests: owner trust (self-hosted default)`の通り、セルフホストでオーナー本人として使う今回の構成では確認は一切出ず、即座に実行された。許可/拒否カードはおそらくGUI(デスクトップアプリやブラウザUI)側で提示される機能であり、今回のようにCLI単体をオーナーとして動かす経路では提示されない、というのが実際の挙動だった。自分のCLIをそのまま使う以上は理屈として自然な設計だが、ドキュメントの説明だけからは分からなかった点として記録しておく。

## ローカルで実際にGUI(ブラウザUI)を確認してみた

ここまでがRoutine(クラウドの自動実行環境)の検証で、GUI側の挙動は「未確認」として持ち越されていた。ローカルPCで実際にブラウザUIを開いて確かめた。

OpenMausBotの「GUI」は、Electronアプリではなく、同じサーバーがブラウザ向けに配信しているチャットUIだった(`serve`コマンドを`--no-open`なしで実行すると自動的にブラウザが開く)。ペアリングコードでこのブラウザを「オーナー」として認証し、既定のbot「MausBot」(Chief of Staff)を作成して、CLIと同じ「シェルコマンドでファイルを削除してください」という依頼を、今度はチャット欄から直接投げてみた。

結果は同じだった。デフォルト設定(bot設定の「Before MausBot acts」が「Just do it」)では、**GUIであっても確認カードは一切出ず、即座に実行された。** CLIの`owner trust`という理由付けではなく、単純に**bot自体の既定の承認レベルがいきなり「Full access」相当("Just do it")になっている**ことが原因だと分かった(`shared/approval-mode.ts`に`DEFAULT_APPROVAL_MODE = "full"`と明記されている)。つまりCLIとGUIの違いではなく、「新しく作ったbotは最初から承認なしモードで動く」という設計そのものが、確認カードが出なかった理由だった。

### 「Ask me first」に切り替えても、カードは出なかった

では、bot設定を明示的に「Ask me first」(確認を求める)に切り替えれば、GUIでカードが出るはずだ、と考えて試した。

結果は予想と違っていた。**確認カードが表示される代わりに、エラーで処理自体が止まった。**

```
That couldn't be found. It may have been removed.
▼ Details
claude exited 1 before result: Error: MCP tool mcp__ogb__approve (passed via
--permission-prompt-tool) not found. Available MCP tools: none
```

同じ依頼を2回試して、どちらも同じエラーで再現した。OpenMausBotは、Claude Code CLIの`--permission-prompt-tool`という仕組み(ツール実行前に外部プログラムへ可否を問い合わせる機能)を使って確認カードを実装しているようだが、その問い合わせ先であるはずのMCPツール`mcp__ogb__approve`自体が、今回のセットアップでは登録されていなかった(`Available MCP tools: none`)。結果として、claude CLIプロセスは確認を求める前に即座にエラー終了していた。

つまり今回のローカル検証で分かったのは、「確認カードがCLI/GUIで出し分けられている」という話ではなく、**「Ask me first」に切り替えても、Claude Code CLIをエンジンに使う今回のセットアップでは確認カードの仕組みそのものが動いていない**、というより具体的な実際の挙動だった。

### シェルの作業範囲はbotごとにサンドボックス化されている

もう一つ、確認カードとは別の発見があった。bot設定を「Just do it」に戻した状態で、`/home/<user>/`配下の任意の場所にファイルを作らせようとすると、今度はきちんと拒否された。

```
I can't run that — my Bash tool is sandboxed to this Windows/WSL environment's
working folders and has no permission to write to /home/<user>/day041-work/
(got "Permission denied" creating /home). That path isn't reachable from here.
```

つまり、bot自身のシェルツールは、OpenMausBotが用意した専用の作業ディレクトリ(`~/.openmausbot/task-workspaces/...`)に閉じ込められていて、承認レベルが「Just do it」でも、そもそもその外側のファイルには手が届かない、という別のサンドボックス機構が働いていた。CLI検証で成功していた`/tmp/ombot-test/victim.txt`の削除も、おそらくこのサンドボックス境界の設定や実行ユーザーの違いによるものと考えられ、今回のGUI検証の環境では同種の操作が「見えないファイル」として扱われた(存在しないファイルと見分けがつかない形でエラーなく終わる場合と、書き込みの場合は明示的に拒否される場合があった)。

最後に、簡単な質疑応答で1往復の速度も見ておいた。

```
$ time openmausbot run MausBot "1+1は何ですか?短く答えてください。" --wait job --timeout 50s
Done: MausBot finished
2
real	0m2.811s
```

claude CLIの起動から応答・終了まで約2.8秒だった。

## ライセンスについて

ルートはApache License 2.0。`enterprise/`配下のみ別のsource-availableライセンスで、評価目的の閲覧・ビルド・改変は無料だが、本番でenterprise機能を使うには有償ライセンスキーが必要と明記されている。今回検証したサーバー起動・エンジン検出・タスク実行はいずれもこの`enterprise/`を使わないOSS部分の機能で、`OMB_LICENSE_KEY`も設定していない。

## まとめ

- Node 24+が前提という点を除けば、インストールからタスク実行まで特に詰まることなく動いた。
- 新しいAPIキーを一切追加せず、既にログイン済みのClaude Code CLIをOpenMausBotのエンジンとしてそのまま検出・実行できた(ファイル作成・シェルコマンドによる削除・簡単な応答の3種類で確認)。
- 「危険な操作は許可/拒否カードで確認」という説明は、CLIでもGUI(ブラウザUI)でも、既定設定では当てはまらず確認なしに即実行された。原因はCLI/GUIの違いではなく、新規botの既定の承認レベルがいきなり「Full access」相当であること。
- GUIで明示的に「Ask me first」(確認を求める)に切り替えても、確認カードは表示されず、`claude exited 1 before result: Error: MCP tool mcp__ogb__approve (passed via --permission-prompt-tool) not found` というエラーで処理が止まった。今回のセットアップでは、確認カードを実装するためのMCPツール自体が登録されておらず、確認フローそのものが機能していなかった。
- これとは別に、bot自身のシェルツールは専用の作業ディレクトリにサンドボックス化されており、承認レベルに関わらずその外側への書き込みは拒否される(読み取りはエラーなく「ファイルが無い」扱いになることがある)、という独立した安全機構も確認できた。

Grok Botが「閉じたUI・固定モデル」であることへのアンチテーゼとして、手元のエージェントCLIをそのまま差し込めるチャットアプリという設計は理にかなっていると感じた。一方で、「危険操作は確認カードで守られる」という触れ込みは、少なくとも今回のClaude Code CLIバックエンドの構成では実際には機能しておらず、代わりに作業ディレクトリのサンドボックスという別の仕組みが安全側に働いていた。実運用では、承認レベルの表示を鵜呑みにせず、実際にカードが出るかどうかを自分の手で確かめる必要がありそうだ。
