# Day 049 results — andrewyng/openworker

出典: https://github.com/andrewyng/openworker (MIT License)
検証対象: `git clone` した2026-11-16時点のmainブランチ(コミット時点のHEAD)

## 環境・インストール

```
$ git clone https://github.com/andrewyng/openworker /tmp/openworker-src
$ cd /tmp/openworker-src
$ bash packaging/setup_dev_env.sh
Using /usr/local/bin/python3.13 (3.13.18)
...
Ready: /tmp/openworker-src/.venv
  server: /tmp/openworker-src/.venv/bin/openworker-server --cwd /path/to/your/project --port 8765
```

バックエンド(`coworker`パッケージ、Python製)のセットアップは1回で成功した
(詳細ログは `setup_dev_env.log`)。`.venv/bin/openworker` というCLIが使えることを確認。

## today.mdの計画との差分(Ollama→llama.cppへの変更)

today.mdの計画ではローカルにOllamaを導入する想定だったが、この実行環境では
`ollama.com`への接続がネットワークポリシーで拒否された
(`curl -I https://ollama.com` → `403 Forbidden`、プロキシのログで
`"kind": "connect_rejected", "host": "ollama.com:443"` を確認)。
これはCLAUDE.mdの「書かない(Routine環境の制約)」に該当する、検証対象ツール自体とは
無関係な制約である(Day 012・Day 048と同種)。

OpenWorkerはREADME・`docs/local-servers.md`で **Ollama以外にllama.cpp/vLLM/LM Studio等も
「ローカルモデル・APIキー不要」の対等なプロバイダとして明記**しており、OpenWorker自身の
Mac向けガイド付きセットアップ(`coworker/providers/llamacpp_setup.py`)も「`llama-server`を
自分で起動したら、OpenWorkerはそれを使う」という設計になっている。
そのため、Ollamaへのエスカレーションは不要と判断し、**llama.cppに差し替えて検証を続行した**。

```
$ git clone --depth 1 https://github.com/ggml-org/llama.cpp /tmp/llama.cpp
$ cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON
$ cmake --build build -j4 --target llama-server
（約3分でビルド完了）
$ /tmp/llama.cpp/build/bin/llama-server --version
version: 1.0.0-dev (build 1, commit 9fba51d)
```

なお`pip install llama-cpp-python[server]`で導入できるPythonバインディング版サーバーも
最初に試したが、モデル自身のjinjaチャットテンプレートを素のまま適用するだけで
OpenAI形式の`tool_calls`フィールドへの構造化パース(grammar-constrained decoding)を
行わず、`<tool_call>...</tool_call>`というXMLタグが`content`に生のテキストとして
返ってきてしまい、OpenWorker側の`tool_calls`判定(`call.get("tool_calls")`)に
掛からなかった。本家llama.cppの`llama-server`(`--jinja`付き)はツール呼び出し用の
文法制約付きデコードと構造化パースを内蔵しており、これは期待通り`tool_calls`を返した
(下記)。この違いはllama.cpp公式ドキュメントにも明記されている既知の仕様で、
Routine環境の制約ではなく、ツール選定上の正しい判断である。

```
$ curl http://127.0.0.1:8080/v1/chat/completions ... (--chat_format chat_template.default, llama-cpp-python版)
{"message":{"content":"<tool_call>\n{{\"name\": \"get_weather\", ...}}\n</tool_call>"}}  # tool_callsフィールドは空

$ curl http://127.0.0.1:8080/v1/chat/completions ... (本家 llama.cpp llama-server --jinja)
{"choices":[{"finish_reason":"tool_calls","message":{"tool_calls":[{"function":{"name":"get_time","arguments":"{\"city\": \"Paris\"}"}}]}}]}
```

## 使用モデルとライセンス

- `Qwen/Qwen2.5-1.5B-Instruct-GGUF`(`qwen2.5-1.5b-instruct-q4_k_m.gguf`, 約1.1GB)
  — **Apache-2.0**。商用利用も可能。
- `Qwen/Qwen2.5-3B-Instruct-GGUF`(`qwen2.5-3b-instruct-q4_k_m.gguf`, 約2.1GB)
  — **Qwen RESEARCH LICENSE AGREEMENT(非商用・研究/評価目的のみ)**。
  同じQwen2.5シリーズでも1.5B/7B/14B/32B/72B系は Apache-2.0 だが、**3Bと72Bだけ
  非商用の研究ライセンス**という点に注意(HuggingFaceのモデルカードのtagsで
  `license:apache-2.0` / `license:other` の違いを確認した)。
  本検証はブログ記事のための非商用の検証・評価目的であり、ライセンス条件内に収まる。
- どちらもHugging Faceの公開・非gatedリポジトリから取得。追加の有料APIキーは一切不要。

両モデルとも `huggingface.co` から直接ダウンロードできた(この実行環境では到達可能)。

## 検証1: 承認フロー — 端末がない状態で`--approval-mode ask`はツール呼び出しを拒否して記録するか

OpenWorkerのREADMEは「Unattended runs never self-approve: their asks park in an inbox
until a human answers.」と主張している。これをCLIの`openworker run`で直接検証した。

```
$ .venv/bin/openworker run --isolated \
    --workspace /tmp/ow-workspace-ask \
    --model "llamacpp:qwen2.5-1.5b-instruct" \
    --approval-mode ask \
    --out /tmp/ow-out-ask2 \
    --timeout-seconds 150 \
    --prompt "Write a file named brief.md containing a 3-line summary of notes1.md and notes2.md. Do it now, call the write_file tool directly without asking me first."

openworker run: no terminal is attached, so every approval is refused in mode ask.
For a run with nobody present use --approval-mode auto-approve or bypass-approvals.
  write_file: /tmp/ow-workspace-ask/brief.md
(...モデルが混乱した応答を続ける...)
openworker run: outcome=completed iterations=2 tool_calls=1 refused=1 tokens_in=208 tokens_out=209 cost=None wall=22s out=/tmp/ow-out-ask2
```

実際に`brief.md`は作成されなかった(ワークスペースに残ったのは`notes1.md`/`notes2.md`のみ)。
`answers.json`には拒否の理由が構造化データとして残る(`logs/ask2-answers.json`に保存):

```json
{
  "stage": "approval_resolved",
  "tool": "write_file",
  "arguments": "{\"path\": \"/tmp/ow-workspace-ask/brief.md\", ...}",
  "reason": "refused: no one is available to approve this (attendance: auto)"
}
```

SQLiteの`audit.db`(操作ログ本体)も確認した(`logs/ask2-audit.txt`):

```
('2026-11-16 01:21:58', 'write_file', 'proposed', '')
('2026-11-16 01:21:58', 'write_file', 'approval_resolved', 'denied')
('2026-11-16 01:21:58', 'write_file', 'finished', 'denied')
```

→ **README通りの挙動を確認できた。** 人間の端末が接続されていない`ask`モードでは、
ファイル書き込みのツール呼び出しは実行される前に拒否され、「提案された
(proposed)→承認結果が出た(approval_resolved: denied)→終了(finished: denied)」という
3段階がすべてSQLiteの監査ログとJSONの両方に、理由付きでそのまま記録されていた。
実際にファイルは一切変更されなかったことも`ls`で確認済み。

## 検証2: 同じタスクを`--approval-mode bypass-approvals`で実行するとどうなるか

承認を明示的に迂回するモードでは、同じ`write_file`呼び出しが実際に実行された。

```
$ .venv/bin/openworker run --isolated ... --approval-mode bypass-approvals ...
  write_file: /tmp/ow-workspace-ask/notes-brief.md
openworker run: outcome=completed iterations=2 tool_calls=1 refused=0 ...

$ cat /tmp/ow-workspace-ask/notes-brief.md
3-line summary:
1. Brief description of the notes1.md and notes2.md
2. Notes1: Some additional information about the notes1.md
3. Notes2: Some additional information about the notes2.md
```

ここで気づいた点: 1.5Bモデルは`write_file`は呼んだが、**`read_file`は一度も呼ばなかった**
(`messages.json`で確認。tool_callsは`write_file`1回のみ)。指示した`brief.md`という
ファイル名にもならず`notes-brief.md`になり、内容も`notes1.md`/`notes2.md`の実際の内容を
一切読まずに書かれた、具体性のない定型文だった。承認フロー自体は正しく機能している一方、
**1.5Bという小さいローカルモデルは、ファイルを読まずに「要約した」と言い切ってしまう**
という信頼性の問題が、まさにこの検証で可視化された。

## 検証3: もう少し大きいローカルモデル(3B)でREADME本来の例題を試す

README「Try your first task」の例題("Read the meeting notes in this folder...")を、
1.5Bより大きい`Qwen2.5-3B-Instruct`(前述の通り研究ライセンス、非商用評価目的で使用)で
実行した。

```
$ .venv/bin/openworker run --isolated \
    --workspace /tmp/ow-workspace-ask \
    --model "llamacpp:qwen2.5-3b-instruct" \
    --approval-mode bypass-approvals \
    --out /tmp/ow-out-3b \
    --timeout-seconds 200 \
    --prompt "Read the meeting notes in this folder. Create a one-page brief with the key decisions, open questions and next steps. Save it as brief.md."

  list_files: /tmp/ow-workspace-ask/notes
  list_files: /tmp/ow-workspace-ask
  read_file: /tmp/ow-workspace-ask/notes/notes1.md
  read_file: /tmp/ow-workspace-ask/notes/notes2.md
  write_file: /tmp/ow-workspace-ask/brief.md
openworker run: outcome=completed iterations=6 tool_calls=5 refused=0 tokens_in=5560 tokens_out=651 wall=185s
```

3Bモデルは1.5Bと違い、`list_files`→`list_files`→`read_file`→`read_file`→`write_file`
という**正しいエージェント的な探索の形**を取った。ただし実際のツール結果(`logs/run3b-trajectory.json`)
を見ると:

```
list_files("/tmp/ow-workspace-ask/notes")  → {"error": "not a directory: /tmp/ow-workspace-ask/notes"}
list_files("/tmp/ow-workspace-ask")        → ["notes1.md", "notes2.md"]
read_file("/tmp/ow-workspace-ask/notes/notes1.md") → {"error": "not a file: ...notes/notes1.md"}
read_file("/tmp/ow-workspace-ask/notes/notes2.md") → {"error": "not a file: ...notes/notes2.md"}
write_file("/tmp/ow-workspace-ask/brief.md", "...")
```

2回目の`list_files`で正しいファイル名(`notes1.md`, `notes2.md`、ワークスペース直下)を
得たにもかかわらず、続く`read_file`では最初に誤って推測した`notes/`という
存在しないサブディレクトリ付きのパスを使い続け、2回とも「ファイルが見つからない」
というエラーを受け取った。それでもモデルは経路を修正せず、実際の内容を一度も読まずに
`brief.md`を書いた。書かれた内容は:

```markdown
# Meeting Notes Brief
## Key Decisions
- Placeholder Decision 1
- Placeholder Decision 2
## Open Questions
- Placeholder Open Question 1
- Placeholder Open Question 2
## Next Steps
- Placeholder Next Step 1
- Placeholder Next Step 2
```

モデル自身の最終応答も「This serves as an example, if you would like to fill it in
with actual notes from the meeting.」と、**内容が読めなかったことを(間接的にではあるが)
自分で認める**形で終わった。具体的な事実を存在しないかのように断定してしまう1.5Bの
挙動よりは安全側だが、タスクとしては失敗している。

この一連の出来事(`proposed`→`started`→`finished: ok`)も`audit.db`に
全5ツール呼び出し分すべて記録されていた(`logs/run3b-audit.txt`)。
**承認ゲート自体は無条件で許可(bypass)されていたが、何を・いつ・どういう引数で
実行したかというログは、成功した呼び出しについても欠落なく残っていた。**

## まとめて分かったこと

1. **承認ゲートの主張(README「Governed by design」)は、ローカルのオープンソースモデル
   だけ・有料APIキーなしの構成でも、CLIから直接再現できた。** 端末がない`ask`モードでは
   ファイル書き込みが実行前に拒否され、拒否の理由・対象ファイル・引数が`audit.db`と
   `answers.json`の両方にそのまま残る。`bypass-approvals`にすると同じ呼び出しが
   実際に実行され、その実行自体もログに残る。この「ゲートの有無に関わらずログは残る」
   という設計は、今回のような小さい検証でもそのまま確認できた。
2. **governanceの土台が正しく動いていることと、その上で動くモデルが仕事をやり切れるかは
   別問題。** 1.5Bモデルはタスクの自然文指示だけでは`write_file`すら呼ばないことがあり
   (検証ログでは`tool_calls=0`で「やります」とだけ言って終了した実行例もあった)、
   明示的に「今すぐツールを呼べ」と指示してようやく1回ツールを呼んだが、ファイルを
   読まずに定型文を書いた。3Bモデルは探索の手順自体は踏んだが、パスを一度間違えたまま
   最後まで修正できず、結局プレースホルダーを書いて終わった。
3. どちらの失敗も、OpenWorker・llama.cpp側の既定動作やこの実行環境固有の制約ではなく、
   **使用したローカルモデル(1.5B/3B)の指示追従・自己修正能力の限界**によるもので、
   読者が同じ構成(ローカルCPU・小さいモデル)で再現しうる、検証対象に直接関係する結果である。

## 範囲外(今回は検証していない)

- デスクトップGUI(Tauriシェル)・自動更新。ヘッドレスのCLI(`openworker run`)・サーバーAPI
  単体に絞った。
- Slack/GitHub/メール/カレンダー等の外部コネクタ(別途認証情報が必要なため)。
- NVIDIA OpenShellサンドボックス(GPU前提の別機能のため)。
- Harness SDK(TypeScript)側の最小サンプル。時間の都合でPythonエンジン側(Desktop Appと
  同じ`coworker`)の検証を優先し、SDK側は見送った。

## 再現手順

詳細は`README.md`の再現手順、または`setup.sh`を参照。
