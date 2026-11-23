---
title: "「100行のAIエージェント」mini-swe-agentにローカルLLMで1行のバグを直させたら、27回中4回しか直らなかった"
emoji: "🐚"
type: "tech"
topics: ["ai", "llm", "agent", "ollama", "python"]
published: false
---

## これは何を試した記事か

SWE-benchやSWE-agentを作ったチームが公開している[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)(MIT)を、手元のOllamaで動くローカルLLMにつないで試した記事である。
mini-swe-agentは、ツールをbashだけに絞り、LLMの返答に含まれるコマンドを実行して結果を会話に足していくだけの、とても小さなコーディングエージェントだ。
READMEは「エージェントクラスは100行ほど」「SWE-bench Verifiedで74%超」とうたっている。

題材には、このチャレンジのリポジトリ自身を使った。
前日(Day 55)に書いた採点スクリプト `regrade.py` に1行だけバグを仕込み、mini-swe-agentに「直して」と頼んだ。
モデルを4種類、設定を3通り変えて、それぞれ3回ずつ実行した。

- 出典: https://github.com/SWE-agent/mini-swe-agent (MIT License)
- 検証バージョン: mini-swe-agent 2.4.6(PyPI)、litellm 1.110.2

## 環境

| 項目 | 内容 |
|---|---|
| GPU | NVIDIA GeForce RTX 5060 Ti(16GB) |
| OS | Windows + WSL2(Ubuntu 24.04) |
| LLMサーバー | Ollama 0.35.1 |
| コマンドの実行先 | mini-swe-agentの `docker` 環境(`python:3.12-slim`、`--network none`) |

使ったモデルは次の4つで、いずれもOllamaのQ4_K_M量子化版である。

| モデル | パラメータ数 | ライセンス |
|---|---|---|
| qwen2.5:7b-instruct | 7.6B | Apache-2.0 |
| qwen2.5:14b-instruct | 14.8B | Apache-2.0 |
| gemma4:e4b | 7.5B(実効4B) | Apache-2.0 |
| qwen2.5-coder:3b-instruct | 3.1B | Qwen Research License |

AnthropicやOpenAIのAPIキーは手元に無いので、mini-swe-agentにはローカルモデルだけをつないだ。
比較のため、同じ課題をClaude Code(`claude -p`)にも1回だけ解かせた。

## 仕込んだバグと課題

`regrade.py` は、掛け算の回答文から「最後の数値」を取り出して採点するスクリプトである。
その1行を、最初の数値を取るように書き換えた。

```diff
-        last = nums[-1].replace(",", "") if nums else ""
+        last = nums[0].replace(",", "") if nums else ""
```

`438 × 70 = 30,660` のように式ごと答えた回答では、最初の数値は438になるので不正解扱いになる。
バグ入りの状態で実行すると、ループ3回と4回の正解数が1問ずつ少なく出る。

```
$ python3 regrade.py out_loops_copy.json
loops=1: digits-concat 1/20, last-number 1/20
loops=2: digits-concat 19/20, last-number 19/20
loops=3: digits-concat 17/20, last-number 17/20
loops=4: digits-concat 10/20, last-number 10/20
```

エージェントには、期待値(1/20、19/20、18/20、11/20)と「元のJSONは上書きされるのでコピーで実行すること」を英語の課題文で伝えた。
実行後に、修正された `regrade.py` を新しいJSONのコピーで動かし、期待値と完全に一致したときだけ「直った」と判定した。
上限は30ステップ・15分とした。

## インストールと実行

インストールは1行で済んだ。

```bash
$ uv pip install mini-swe-agent
$ mini --help
This is mini-swe-agent version 2.4.6.
```

LLMにbashを自由に打たせることになるので、コマンドはネットワークを切ったDockerコンテナの中で実行させた。
mini-swe-agentには `docker` 環境が同梱されていて、設定ファイルに次のように書くだけで切り替えられた。

```yaml
environment:
  environment_class: docker
  image: python:3.12-slim
  cwd: /repo
  run_args: ["--rm", "--network", "none", "--user", "1000:1000", "-v", "<作業コピー>:/repo"]
model:
  model_name: "ollama_chat/qwen2.5:14b-instruct"
  cost_tracking: ignore_errors
  model_kwargs:
    api_base: "http://localhost:11434"
```

```bash
$ MSWEA_CONFIGURED=true mini -y --exit-immediately -c mini.yaml -c trial.yaml -t "$(cat task.txt)" -o traj.json
```

初回起動時はAPIキーを聞く対話式の設定ウィザードが立ち上がるため、非対話で回すには `MSWEA_CONFIGURED=true` が必要だった。
ローカルモデルには料金情報が無いので、`cost_tracking: ignore_errors` も入れないとコスト計算でエラーになる。

## 結果: 直せたのはgemma4:e4bだけだった

| 条件 | モデル | 修正成功 | 元JSONを上書き | 所要時間の中央値 |
|---|---|---|---|---|
| ツール呼び出し・既定コンテキスト | qwen2.5:14b | 0/3 | 0/3 | 104秒 |
| ツール呼び出し・16k | qwen2.5:7b | 0/3 | 0/3 | 56秒 |
| ツール呼び出し・16k | qwen2.5:14b | 0/3 | 0/3 | 557秒 |
| ツール呼び出し・16k | qwen2.5-coder:3b | 0/3 | 0/3 | 13秒 |
| ツール呼び出し・16k | gemma4:e4b | **2/3** | 0/3 | 31秒 |
| テキスト形式・16k | qwen2.5:7b | 0/3 | 3/3 | 113秒 |
| テキスト形式・16k | qwen2.5:14b | 0/3 | 0/3 | 242秒 |
| テキスト形式・16k | qwen2.5-coder:3b | 0/3 | 1/3 | 34秒 |
| テキスト形式・16k | gemma4:e4b | **2/3** | 0/3 | 24秒 |
| (参考)Claude Code | claude-opus-5-5 | 1/1 | 0/1 | 約14秒 |

ローカルモデルの27回のうち、バグを直せたのは4回で、すべてgemma4:e4bだった。
Qwen2.5は3B・7B・14Bのどれも、21回中1回も直せなかった。
Claude Codeは4ターン・約14秒で、同じ1行の修正を返した。

うまくいったgemma4:e4bの実行は、たった4手で終わっている。

```
[1] $ cat experiments/day-055/regrade.py
[2] $ sed -i 's/last = nums\[0\].replace(\",\", \"\") if nums else \"\"/last = nums\[-1\].replace(\",\", \"\") if nums else \"\"/' experiments/day-055/regrade.py
[3] $ cp experiments/day-055/out_loops.json experiments/day-055/out_loops_copy.json && python experiments/day-055/regrade.py experiments/day-055/out_loops_copy.json
loops=1: digits-concat 1/20, last-number 1/20
loops=2: digits-concat 19/20, last-number 19/20
loops=3: digits-concat 17/20, last-number 18/20
loops=4: digits-concat 10/20, last-number 11/20
[4] $ echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
```

コードを読み、1行直し、コピーで確かめて提出するという、課題文が求めたとおりの流れだった。
失敗した23回では、失敗の仕方がいくつかに分かれた。

## つまずき1: Ollamaの既定コンテキストでは、指示が会話から消えた

最初は設定を何も変えずにqwen2.5:14bを動かし、5回目のAPI呼び出しでフォーマットエラーが3回続いて終了した。
`ollama ps` を見ると、コンテキスト長は4096トークンになっていた。

```
$ ollama ps
NAME                    ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen2.5:14b-instruct    7cdf5a0187d5    9.5 GB    100% GPU     4096       4 minutes from now
```

Ollamaのログには、プロンプトが4096トークンに達した時点で前半の2045トークンを捨てた記録が残っていた。

```
slot   operator(): id  0 | task 3457 | new prompt, n_ctx_slot = 4096, n_keep = 4, task.n_tokens = 3996
slot   operator(): id  0 | task 3457 | slot context shift, n_keep = 4, n_left = 4091, n_discard = 2045
```

mini-swe-agentの既定のプロンプトは、作業手順やコマンドの書き方の説明でそれなりに長い。
そこに22KBのJSONを `cat` した出力が加わって4096トークンを超え、ツールの使い方を書いたシステムプロンプトごと切り捨てられていた。
既定のコンテキストで3回試すと、3回ともこの直後にツールを呼ばなくなって終わった。
`model_kwargs` に `num_ctx: 16384` を足すと、`ollama ps` のCONTEXTは16384になった。

## つまずき2: Qwen2.5はツール呼び出しの形式から外れた

コンテキストを広げても、qwen2.5-coder:3bは3回とも最初の3回のAPI呼び出しでフォーマットエラーが続き、コマンドを1つも実行せずに終わった。
qwen2.5:7bも3回とも同じ `RepeatedFormatError` で終わった。
画面ログを見ると、モデルはコマンドをツール呼び出しではなく、返答の本文にコードブロックとして書いていた。

```
No tool calls found in the response. Every response MUST include at least one tool call.
```

READMEには「LMのツール呼び出し機能さえ必要ない」とあり、本文中の ```` ```mswea_bash_command ```` ブロックからコマンドを拾うテキスト形式の設定(`mini_textbased.yaml`)が同梱されている。
こちらに切り替えるとフォーマットエラーはほとんど出なくなったが、Qwenはそれでも1回も直せなかった。

## つまずき3: `cd` が次のコマンドに引き継がれない

mini-swe-agentは、コマンドを1つずつ別のサブシェルで実行する。
そのため `cd` は次のコマンドに引き継がれず、既定のプロンプトにもその旨が書かれている。
qwen2.5:14bは、一度は `cd` を付けて正しく実行できたのに、その後のコマンドで自分がどこにいるかを見失った。

```
[4] $ python3 regrade.py out_loops_copy.json
python3: can't open file '/repo/regrade.py': [Errno 2] No such file or directory
[5] $ cd experiments/day-055 && python3 regrade.py out_loops_copy.json
loops=3: digits-concat 17/20, last-number 17/20
[13] $ cp experiments/day-055/regrade.py .
[15] $ python3 regrade.py out_loops_copy.json
FileNotFoundError: [Errno 2] No such file or directory: 'out_loops_copy.json'
```

最後はリポジトリ直下にコピーした `regrade.py` を書き換え続けて30ステップの上限に達し、本物の `regrade.py` は一度も変わらなかった。

## つまずき4: エスケープし忘れたsedが、何も言わずに何もしなかった

いちばん印象に残ったのは、gemma4:e4bの成否を分けたのがsedの書き方だったことである。
成功した4回は、どれも `nums\[0\]` と角括弧をエスケープしていた。
失敗した2回は、どちらも `nums[0]` とそのまま書いていた。

正規表現の `[0]` は「0という1文字」を表すので、`nums[0]` というパターンは `nums0` という文字列にしかマッチしない。
しかもsedは、マッチしなくても終了コード0で何も出力しない。
手元で確かめると、そのとおりだった。

```
$ printf 'last = nums[0].replace(",", "") if nums else ""\n' > t.py
$ sed -i 's/last = nums[0].replace(",", "") if nums else ""/last = nums[-1].replace(",", "") if nums else ""/' t.py; echo "rc=$?"; cat t.py
rc=0
last = nums[0].replace(",", "") if nums else ""
$ sed -i 's/last = nums\[0\].replace(",", "") if nums else ""/last = nums[-1].replace(",", "") if nums else ""/' t.py; echo "rc=$?"; cat t.py
rc=0
last = nums[-1].replace(",", "") if nums else ""
```

失敗した1回は、この空振りのsedを2回打ったあと、スクリプトを実行し直さずに提出した。
もう1回は、実行して `last-number 17/20` と直っていない結果を見たにもかかわらず提出した。
Qwen2.5も同じエスケープ忘れを3回の実行で書いていた。
bashだけで編集するエージェントにとって、エラーを出さずに空振りするコマンドは、エラーよりも厄介な相手だった。

## つまずき5: 「元のJSONは触らないで」が守られなかった

課題文には「`regrade.py` は渡したJSONを上書きするので、コピーで実行すること」と書いた。
それでも、テキスト形式のqwen2.5:7bは3回とも元の `out_loops.json` に対して実行し、上書きしてしまった。
qwen2.5-coder:3bの1回は、1手目で元のJSONに対して実行し、2手目で提出して終わった。

```
[1] $ python experiments/day-055/regrade.py experiments/day-055/out_loops.json
loops=3: digits-concat 17/20, last-number 17/20
[2] $ echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
```

直っていないのに提出(`Submitted`)して終わった実行は、全体で5回あった。
エージェントの終了ステータスが「提出済み」でも、それは「直った」という意味ではなかった。

## 「100行」は本当か

v2.4.6の `agents/default.py` は190行で、docstring・コメント・空行を除くと151行だった。
コマンドを実行する `environments/local.py` は92行(コードは76行)である。
中身は「LLMに問い合わせる」「返答の中のコマンドを実行する」「出力をメッセージに足す」の繰り返しで、出力の1行目が `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` になったら終わる。
読めばすぐに全体が分かる小ささで、だからこそ今回のような失敗の原因も、軌跡のJSONを読むだけで追えた。

## まとめ

- mini-swe-agent 2.4.6は `pip install` だけで入り、Dockerのネットワーク無しコンテナでコマンドを実行させる構成もYAML数行で組めた。
- 1行のバグ修正を、ローカルモデル4種×3条件×3回の計27回試し、直せたのは4回で、すべてgemma4:e4bだった。Qwen2.5(3B・7B・14B)は21回中0回だった。Claude Codeは1回で直した。
- Ollamaを既定のまま使うとコンテキストが4096トークンで、システムプロンプトが切り捨てられた。`num_ctx` を指定する必要があった。
- 失敗の中身は、ツール呼び出し形式からの逸脱、`cd` が引き継がれないことでの迷子、エスケープ忘れで空振りするsed、元ファイルの上書きだった。
- 直っていないのに「提出」して終わった実行が5回あり、エージェントの完了報告はそれだけでは信用できなかった。

SWE-bench Verifiedの74%超という数字は、強いモデルと組み合わせたときのものである。
同じ100行のエージェントでも、つなぐモデルによって、1行の修正ができるかどうかがここまで変わった。

## 出典・ライセンス

- mini-swe-agent: https://github.com/SWE-agent/mini-swe-agent (MIT License)
- Qwen2.5 7B/14B Instruct: Apache License 2.0、Qwen2.5-Coder 3B Instruct: Qwen Research License(Ollama経由で使用)
- Gemma 4 E4B: Apache License 2.0(Ollama経由で使用)
- 検証ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-056
