---
title: "AWS公式のマルチエージェントCLI「CAO」でClaude Codeに仕事を委任させたら、フォルダ信頼確認で60秒止まった"
emoji: "🧭"
type: "tech"
topics: ["ai", "claudecode", "llm", "tmux", "aws"]
published: false
---

## これは何を試した記事か

AWS Labsが公開している[cli-agent-orchestrator](https://github.com/awslabs/cli-agent-orchestrator)(以下CAO、Apache-2.0)を、Claude Codeをワーカーにして実際に動かしてみた記事である。
CAOは、Claude Code・Codex CLI・Kiro CLIなど、すでに認証済みのAIコーディングCLIを「provider」として束ねるオーケストレーションフレームワークである。
supervisorエージェントが、各CLIをtmux上の独立したセッションとして立ち上げ、タスクを委任する。
各ワーカーは、自分のネイティブな認証・機能をそのまま保ったCLIプロセスとして起動される。

今回は、supervisorもworkerもClaude Codeにして、「supervisorが自分では書かずに、workerにファイルを書かせる」ところまでを確かめた。

- 出典: https://github.com/awslabs/cli-agent-orchestrator (Apache-2.0)
- AWS Open Source Blog: https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse
- 検証コミット: `a21ad13b6b00c494c991a8edc133ae72d2935da1`(CAO 2.5.4)

## 環境

| 項目 | 内容 |
|---|---|
| OS | Windows + WSL2(Ubuntu 24.04.3、Linux 6.6)、一般ユーザー |
| tmux | 3.4 |
| Claude Code CLI | 2.1.329(普段から対話的に使っているもの) |
| CAO | 2.5.4(`uv tool install`) |

## インストールからサーバー起動まではすんなり動いた

READMEの手順どおりに進めると、追加の有料APIキーもGPUも不要で、ここまでは問題なく動いた。

```
$ uv tool install git+https://github.com/awslabs/cli-agent-orchestrator.git@a21ad13b6b00c494c991a8edc133ae72d2935da1
...
Installed 4 executables: cao, cao-mcp-server, cao-ops-mcp-server, cao-server
$ cao --version
cao, version 2.5.4

$ cao install code_supervisor
✓ Agent 'code_supervisor' installed successfully

$ cao-server
INFO:     Uvicorn running on http://127.0.0.1:9889 (Press CTRL+C to quit)
```

`cao profile list` を見ると、`code_supervisor` に加えて `developer` / `reviewer` / `memory_manager` など、最初から使えるbuilt-inプロファイルが揃っていた。

## 本題: supervisorにworkerへの委任をさせる

空のワークスペースを用意し、Claude Codeをproviderにしてsupervisorを起動した。
タスクは「2つの俳句ファイルを、自分では書かずにworkerに委任して作らせる」というものにした。

```bash
cao launch --agents code_supervisor --provider claude_code \
  --working-directory /home/matsu/cao-workspace --headless --auto-approve \
  "Create two files in this directory using a worker agent: notes-a.md with a haiku about the ocean, and notes-b.md with a haiku about mountains. Delegate both file-writing subtasks to a worker agent (use handoff or assign), do not write the files yourself directly. Report back which worker(s) you used and what they produced."
```

起動時には、supervisorに許可されるツールが表示される。

```
Agent 'code_supervisor' launching on claude_code:
  Allowed:  @cao-mcp-server, fs_read, fs_list
  Blocked:  Agent, Bash, BashOutput, CronCreate, ... Edit, ... Write
  Delegates: ALL TOOLS (unrestricted)
```

supervisor自身はファイルを書けず、CAOのMCPツールで仕事を渡すことしかできない作りになっている。

## 1回目: `[Errno 95] Operation not supported`

最初の実行は、セッション作成の段階で失敗した。

```
Error: cao-server refused the launch (500): Failed to create session: [Errno 95] Operation not supported
```

CAOは設定・DB・ログを `~/.aws/cli-agent-orchestrator` に置き、tmuxペインの出力を名前付きパイプ(FIFO)経由で読む。
筆者のWSL環境では `~/.aws` がWindows側の `/mnt/c/Users/.../.aws` へのシンボリックリンクになっていて、Windowsのドライブ上では `mkfifo` が使えない。
同じディレクトリでファイルロックやSQLiteは動き、`mkfifo` だけが `[Errno 95]` になることを確かめた。

CAOのホームは環境変数 `CAO_HOME_DIR` で変えられるので、Linux側に移した。

```bash
$ export CAO_HOME_DIR=$HOME/.cao-home
$ cao install code_supervisor && cao-server
```

## 2回目: 60秒でタイムアウトした

同じ `cao launch` を実行すると、今度はセッションまでは作られたが、60秒でタイムアウトした。

```
Session created: cao-89d6ac99
Terminal created: code_supervisor-0214
Error: Initial message was not delivered to terminal f1b4af67 (provider_init_error): Worker f1b4af67 failed to initialize: Claude Code initialization timed out after 60s
```

tmuxセッションは残っていたので、`tmux capture-pane` で中を覗いた。

```
$ ... claude --dangerously-skip-permissions --session-id ... --disallowedTools Write
────────────────────────────────────────
 Accessing workspace:
 /home/matsu/cao-workspace
 Quick safety check: Is this a project you created or one you trust? ...
 ❯ No, exit
   Yes, I trust this folder
 Enter to confirm · Esc to cancel
```

Claude Codeは、新しく作ったワークスペースに対して「このフォルダを信頼しますか」という確認を出して止まっていた。
CAOは `--dangerously-skip-permissions` を渡しているが、このフラグはフォルダ信頼確認を省略しない。

## 原因: 起動判定の正規表現がUbuntuのMOTDに一致した

CAOはこの確認を想定していて、`providers/claude_code.py` の `_handle_startup_prompts()` に、画面に `Yes, I trust this folder` が出たらDown→Enterを送って承認する処理がある。
それなのに承認されなかったので、`cao-server` のログを見た。

```
20:11:28,898 send_keys: cao-89d6ac99:code_supervisor-0214 - keys length: 1216
20:11:29,230 Claude Code started without prompts
20:11:29,230 wait_until_status [f1b4af67]: waiting for {waiting_user_answer, idle, completed}, timeout=60s
20:12:29,261 wait_until_status [f1b4af67]: timeout waiting for {waiting_user_answer, idle, completed}
20:12:29,261 Deferred init for terminal f1b4af67 failed: TimeoutError('Claude Code initialization timed out after 60s').
```

claudeコマンドを送ってからわずか0.33秒で「started without prompts(確認画面なしで起動した)」と判定している。
該当箇所のコードは次のとおりである。

```python
if re.search(r"Welcome to|Claude Code v\d+", clean_output):
    logger.info("Claude Code started without prompts")
```

`Welcome to` はClaude Codeの起動バナーを見つけるための条件だが、tmuxペインの先頭にはログインシェルが出したUbuntuのメッセージ(MOTD)が残っていた。

```
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.6.87.2-microsoft-standard-WSL2 x86_64)
...
This message is shown once a day. To disable it please create the
/home/matsu/.hushlogin file.
```

この `Welcome to Ubuntu` に一致したため、信頼確認が描画される前に「起動完了」と判定して処理を抜け、自動承認が一度も実行されなかった。
UbuntuのMOTDは1日1回しか表示されないので、その日最初に開いたtmuxペインでだけ起きる条件である。
MOTDが出ない状態で、未信頼のフォルダをCAOが自動承認できるかは今回試していない。

## 3回目: フォルダを信頼済みにすると委任まで動いた

フォルダ信頼確認は、監視なしで動くエージェントにそのフォルダでの読み書き・実行を許すかどうかの判断である。
CAOに自動承認させるのではなく、筆者が別の端末で一度 `claude` を起動し、自分で「Yes, I trust this folder」を選んだ。

```bash
$ cd ~/cao-workspace && claude   # 「Yes, I trust this folder」を選んで /exit
```

そのうえで同じ `cao launch` を実行すると、今度は最後まで動いた。

```
Session created: cao-48b9ed18
Terminal created: code_supervisor-52d4
I handed both files to one worker, the developer agent (Claude Code, terminal 18a265d6). It finished in about 24 seconds
and the terminal was shut down afterwards. I opened both files myself and they contain what the worker reported.
```

```
$ cat ~/cao-workspace/notes-a.md
Salt wind on the waves
the tide pulls the moon's pale light
back to the dark deep
$ cat ~/cao-workspace/notes-b.md
Granite shoulders rise
snow keeps the old silence there
clouds bow at the peak
$ cao session list
SESSION                   CONDUCTOR    STATUS          TERMINALS
cao-48b9ed18              5f80ddc4     completed       1
```

`cao-server` のログから流れを追うと、次のようになっていた。

| 時刻 | 出来事 |
|---|---|
| 20:15:59.9 | supervisor(`code_supervisor`)のtmuxセッションを作成 |
| 20:16:05.2 | supervisorが入力待ちになる(起動成功) |
| 20:16:12.7 | supervisorにタスクを送信 |
| 20:16:18.2 | supervisorがworker用のtmuxウィンドウ `developer-5fe4` を作成 |
| 20:16:29.3〜20:16:38.3 | workerがタスクを処理 |
| 20:16:42.0 | workerのウィンドウを削除 |
| 20:16:47.3 | supervisorが完了 |

launchから完了まで約47秒で、ファイルを書いたのはsupervisorではなく `developer` プロファイルのworkerだった。
supervisorは、タスク用のファイルを書くツールが無いので指示を委任メッセージに直接書いたこと、短いテキストなので `reviewer` へのレビュー依頼を省いたことも報告してきた。

## 注意: CAOは `~/.claude/settings.json` を書き換える

`cao-server` のログには、launchのたびに次の行が出ていた。

```
Set skipDangerousModePermissionPrompt in ~/.claude/settings.json
```

CAOは、ユーザー全体のClaude Code設定に `"skipDangerousModePermissionPrompt": true` を追加する。
これは `--dangerously-skip-permissions` で起動したときの確認画面を、CAO経由に限らずすべてのClaude Codeで省略する設定である。
筆者の設定には元々無かったので、検証後に削除した。

## まとめ

- CAO 2.5.4のインストール・プロファイル登録・サーバー起動は、READMEの手順どおりに動いた。
- WSLで `~/.aws` がWindows側にあると、FIFOが作れず `[Errno 95]` で失敗した。
- `CAO_HOME_DIR` をLinux側にすると回避できた。
- 新しいワークスペースではClaude Codeのフォルダ信頼確認が出て、CAOの自動承認がUbuntuのMOTD(`Welcome to Ubuntu`)に起動判定を横取りされ、60秒でタイムアウトした。
- フォルダを自分で信頼済みにしておくと、supervisorがworkerへファイル作成を委任し、約47秒で完了した。
- CAOは `~/.claude/settings.json` に `skipDangerousModePermissionPrompt` を追加するので、気になる場合は検証後に戻す。

複数のエージェントを無人で動かす道具では、「このフォルダを信頼するか」のような確認を誰がいつ済ませるかが、そのまま動くかどうかを左右する。
今回は、その確認を人間が先に済ませておく形で、委任の動きを確かめられた。

## 出典・ライセンス

- cli-agent-orchestrator: https://github.com/awslabs/cli-agent-orchestrator (Apache-2.0、commit `a21ad13`)
- AWS Open Source Blog: https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse
- 検証ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-053
