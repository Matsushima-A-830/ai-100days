---
title: "Andrew Ng発「OpenWorker」の承認ゲートは、ローカルLLMだけでも本当に機能するのか試した"
emoji: "🛂"
type: "tech"
topics: ["ai", "llm", "agent", "llamacpp", "oss"]
published: false
---

## これは何か

Andrew Ng(Rohit Prasadと共同)が公開した、デスクトップで動くAIエージェント「OpenWorker」(MIT License)を、クラウドAPIキーを一切使わずローカルのLLMだけで動かして検証した。
出典: https://github.com/andrewyng/openworker

OpenWorkerのREADMEは「Governed by design」として、ツール呼び出しは承認が無ければ実行されず、承認の有無に関わらず操作ログが残る、と主張している。
筆者が気になったのは、この主張がクラウドの高性能モデルを前提にした話なのか、無料で誰でも試せるローカルの小さなモデルでも同じように機能するのか、という点だった。
実際に手を動かして、GUIもクラウドAPIキーも使わず、サーバーエンジン単体とCLIだけでこの主張を確かめた。

## 環境

OpenWorkerのデスクトップ版が使うバックエンド(`coworker`パッケージ、Python製)をソースから起動した。
```bash
git clone https://github.com/andrewyng/openworker
cd openworker
bash packaging/setup_dev_env.sh
```
1回で成功し、`openworker`というCLIが使えるようになった。

ローカルモデルの接続先はOllamaを想定していたが、筆者の実行環境では`ollama.com`への接続がネットワーク制限で拒否された。
OpenWorkerはREADMEと`docs/local-servers.md`で、Ollama以外にllama.cpp・vLLM・LM Studioなども対等な「ローカルモデル・APIキー不要」のプロバイダとして明記している。
そこで本家`llama.cpp`をソースからビルドし、Hugging Faceから取得した`Qwen2.5-1.5B-Instruct`(Apache-2.0)と`Qwen2.5-3B-Instruct`(Qwen RESEARCH LICENSE、非商用の研究・評価目的限定)のGGUFモデルで検証した。
Qwen2.5シリーズは1.5B/7B/14B/32B/72BがApache-2.0だが、3Bと72Bだけ非商用の研究ライセンスという点に注意が必要だった。
今回の利用はブログ記事のための非商用の検証・評価であり、ライセンス条件の範囲内に収まる。

```bash
llama-server -m qwen2.5-1.5b-instruct-q4_k_m.gguf --alias qwen2.5-1.5b-instruct -c 8192 --jinja --host 127.0.0.1 --port 8080
```

ちなみに最初は`pip install llama-cpp-python[server]`で導入できるPythonバインディング版サーバーを試したが、こちらはモデルのjinjaテンプレートをそのまま適用するだけで、OpenAI形式の構造化された`tool_calls`フィールドへの変換(文法制約付きデコード)を行わなかった。
返ってきたのは`<tool_call>...</tool_call>`というXMLタグがそのまま入った生テキストで、OpenWorker側は「ツールを呼んだ」と認識できなかった。
本家llama.cppの`llama-server`に`--jinja`を付けて起動すると、同じモデルでも構造化された`tool_calls`が返ってくることを確認し、以降はこちらを使った。

## 検証1: 端末がない状態で承認を求めたら、本当に拒否されて記録されるか

OpenWorkerのCLIには`openworker run --isolated`というモードがあり、この計算機の設定を一切読まず、すべて`--out`で指定したフォルダの中だけで完結する実行ができる。
会議メモ2本を置いたワークスペースに対して、「brief.mdというファイルに3行の要約を書いて、確認を取らずに今すぐwrite_fileツールを呼べ」と直接的に指示した。

```bash
openworker run --isolated --workspace ./ws --model "llamacpp:qwen2.5-1.5b-instruct" \
  --approval-mode ask --out ./out --timeout-seconds 150 \
  --prompt "Write a file named brief.md containing a 3-line summary of notes1.md and notes2.md. Do it now, call the write_file tool directly without asking me first."
```

実行結果:
```
openworker run: no terminal is attached, so every approval is refused in mode ask.
For a run with nobody present use --approval-mode auto-approve or bypass-approvals.
  write_file: /tmp/ow-workspace-ask/brief.md
openworker run: outcome=completed iterations=2 tool_calls=1 refused=1 ...
```

ワークスペースを確認すると、`brief.md`は作成されていなかった。
実行結果フォルダの`answers.json`には、拒否の理由がそのまま残っていた。

```json
{
  "stage": "approval_resolved",
  "tool": "write_file",
  "reason": "refused: no one is available to approve this (attendance: auto)"
}
```

操作ログ本体であるSQLiteの`audit.db`も確認した。

```
('write_file', 'proposed', '')
('write_file', 'approval_resolved', 'denied')
('write_file', 'finished', 'denied')
```

「提案(proposed)→承認結果(approval_resolved: denied)→終了(finished: denied)」という3段階が、理由付きでそのまま記録されていた。
README通りの挙動を、クラウドAPIキーなしのローカル1.5Bモデルで再現できた。

## 検証2: 承認を迂回すると、同じ呼び出しが実際に実行される

同じタスクを`--approval-mode bypass-approvals`で実行すると、`write_file`は実際に実行された。

```
$ cat notes-brief.md
3-line summary:
1. Brief description of the notes1.md and notes2.md
2. Notes1: Some additional information about the notes1.md
3. Notes2: Some additional information about the notes2.md
```

ここで気づいたのは、この1.5Bモデルは`write_file`は呼んだものの、`read_file`を一度も呼んでいなかったことだ。
指定した`brief.md`ではなく`notes-brief.md`という別名になり、内容も実際のメモを読まない、具体性のない定型文だった。
承認ゲート自体は正しく機能している一方で、小さいローカルモデルは「読まずに要約した」と言い切ってしまうという別の問題が、この検証で見えた。

## 検証3: もう少し大きいモデル(3B)でREADMEの例題をそのまま試す

READMEの最初の例題「フォルダの会議メモからbriefを作る」を、研究ライセンスの`Qwen2.5-3B-Instruct`で試した(非商用の評価目的として)。

```
list_files: /tmp/ow-workspace-ask/notes
list_files: /tmp/ow-workspace-ask
read_file: /tmp/ow-workspace-ask/notes/notes1.md
read_file: /tmp/ow-workspace-ask/notes/notes2.md
write_file: /tmp/ow-workspace-ask/brief.md
```

3Bモデルは1.5Bと違い、探索→読み込み→書き込みという正しい手順の形をとった。
ただし実際のツール結果を見ると、最初の`list_files`で存在しない`notes/`サブディレクトリを誤って推測し、2回目の`list_files`で正しいファイル名を得たにもかかわらず、続く`read_file`では誤ったパスを使い続けて2回とも「ファイルが見つからない」というエラーを受け取っていた。
それでも経路を修正せず、実際の内容を一度も読まずに次のようなプレースホルダーを書いた。

```markdown
# Meeting Notes Brief
## Key Decisions
- Placeholder Decision 1
- Placeholder Decision 2
```

モデル自身も最後に「これは例です。実際のメモの内容で埋めてください」とだけ返し、内容を読めなかったことを(間接的にではあるが)認める形で終わった。
この5回のツール呼び出しもすべて`audit.db`に記録されていた。
承認ゲートが無条件に通していた(bypass)場合でも、何を・いつ・どういう引数で実行したかというログは欠落なく残っていた。

## まとめ

1. OpenWorkerの承認ゲートの主張は、クラウドAPIキーなし・ローカルのオープンソースモデルだけの構成でも、CLIから直接再現できた。
   端末がない`ask`モードではファイル書き込みが実行前に拒否され、理由・対象・引数がログに残る。
   `bypass-approvals`にすると同じ呼び出しが実際に実行され、その実行自体もログに残る。
2. governanceの土台が正しく動いていることと、その上で動くモデルが仕事をやり切れるかは別問題だった。
   1.5Bモデルは指示を与えてもファイルを読まずに定型文を書き、3Bモデルは探索の手順は踏んだが一度間違えたパスを最後まで修正できなかった。
3. どちらの失敗もOpenWorker側の既定動作の問題ではなく、使用したローカルモデルの指示追従・自己修正能力の限界によるものだった。

OpenWorkerが提供しているのは「人間を介さずに動くエージェントの監査可能性」という土台であり、その上でどこまで安心して自動化できるかは、結局つなぐモデルの実力に依存する。
この切り分けが、ログを実際に読むまでは見えてこなかった点が、今回手を動かして一番収穫があった部分だった。

## 参考

- OpenWorker: https://github.com/andrewyng/openworker (MIT License)
- llama.cpp: https://github.com/ggml-org/llama.cpp
- Qwen2.5-1.5B-Instruct: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct (Apache-2.0)
- Qwen2.5-3B-Instruct: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct (Qwen RESEARCH LICENSE、非商用)
