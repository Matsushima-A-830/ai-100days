---
title: "ローカル完結AIスタジオlocally-uncensoredのコーディングエージェントを3B/7B/14Bで試したら、直せたのは14Bだけだった"
emoji: "🧑‍💻"
type: "tech"
topics: ["ai", "llm", "ollama", "localllm", "codingagent"]
published: false
---

## これは何を試した記事か

[PurpleDoubleD/locally-uncensored](https://github.com/PurpleDoubleD/locally-uncensored)(AGPL-3.0-only)は、チャット・画像生成・動画生成・コーディングエージェントを1つのデスクトップアプリにまとめ、ローカルで完結させることを目指したOSSである。
GitHub Trending(TypeScript)で1日に200star以上を集めていた。

名前の「uncensored」は、安全性のための拒否応答を外したモデル(abliteratedモデル)を推奨モデルとして案内していることに由来する。
本記事ではその点は主役にせず、「ローカルLLMだけでチャットとコーディングエージェントがどこまで使えるか」という技術的な検証に絞った。
画像・動画生成はComfyUIと6〜12GB以上のVRAMが前提になるため、今回は対象外とした。

結論を先に書くと、チャットは3Bモデルでも問題なく動いた。
一方、コーディングエージェントに単純なバグ修正をさせると、3Bと7Bは2回とも失敗し、成功したのは14Bだけだった。
アプリ側の仕組み(ファイル読み込み・diff付きの変更提案・承認制のシェル実行・ループ検知)はどのモデルでも正しく動いており、成否を分けたのはモデルの能力だった。

- 出典: https://github.com/PurpleDoubleD/locally-uncensored (AGPL-3.0-only、検証時のHEAD `3dff4291`、package.jsonのversion 3.0.10)
- 日本語記事件数(2026-11-12時点、Zenn/Qiita/note検索): 0件

## 検証環境

| 項目 | 内容 |
|---|---|
| OS | Windows + WSL2 |
| CPU / RAM | AMD Ryzen 7 7700 / 30GiB |
| GPU | NVIDIA GeForce RTX 5060 Ti 16GB |
| Node.js / npm | v26.8.2 / 11.19.1 |
| 推論エンジン | Ollama 0.35.1(インストール済みのモデルを使用) |

本体はTauri(Rust+React)のデスクトップアプリだが、`npm run dev` でブラウザから使える開発モードも用意されている。
今回はこの開発モードで検証した。

## インストールと起動

依存パッケージのインストール時スクリプトは実行しない設定で入れた。

```bash
$ npm ci --ignore-scripts --loglevel=error
added 625 packages, and audited 626 packages in 43s
14 vulnerabilities (4 low, 9 moderate, 1 high)
```

この状態でも開発サーバーは問題なく起動した。

```bash
$ npm run dev
[Python] Resolved: python3
[Ollama] Already running
[Whisper] faster-whisper not installed — STT disabled
[WebSearch] SearXNG not available (connection refused or timeout)
  VITE v8.1.6  ready in 403 ms
  ➜  Local:   http://localhost:5273/
[ComfyUI] Not found. Set COMFYUI_PATH in .env or install ComfyUI.
```

ポートはViteの既定の5173ではなく5273だった(`vite.config.ts` の既定値で、環境変数 `LU_DEV_PORT` で変更できる)。
すでに起動していたOllamaは自動で検出された。
音声認識(faster-whisper)、Web検索(SearXNG)、画像生成(ComfyUI)は未導入だったため、それぞれ無効化されただけで起動は妨げられなかった。

## オンボーディング

初回起動時は4ステップのセットアップ画面が出る。

1. **Engine**: 既定は同梱の「LU Engine」。「Use another engine (Ollama, LM Studio…)」を押すと `1 backend detected — Ollama is running. localhost:11434` と表示され、Ollamaを選べた。
2. **Image & Video**: ComfyUIの導入を勧められるが、スキップした。
3. **Model**: 「Models you already have」にOllamaに入っている5つのモデルがそのまま並んだ。ここでは `qwen2.5-coder:3b-instruct-q4_K_M` を選んだ。
4. **Documents**: 文書チャット用の埋め込みモデル(nomic-embed-text、84MB)の導入を勧められるが、スキップした。

モデル選択画面のおすすめは「Qwen 2.5 7B Abliterated (Starter)」(4.4GiB)と「Qwen 3.5 9B Abliterated — Agent-ready」(5.2GiB)の2つだった。
エージェント用途にはアプリ自身が9B級を推奨していることになる。
なお、Ollamaを選んだ場合でも完了画面の文言は「The LU Engine is ready.」のままで、同梱エンジン前提の表示になっていた。

## チャット: 3Bモデルで十分に動く

`qwen2.5-coder:3b-instruct-q4_K_M` に日本語で質問した。

```
Q: 日本の首都はどこですか?理由を1文で添えて、日本語で答えてください。
A: 日本の首都は東京です。理由は、日本の経済、政治、文化の中心地であるためです。
126 in · 27 out    Context window 162/16K
```

送信から約0.55秒で表示が始まり、約5.6秒で応答が終わった(モデルのロード時間を含む初回応答)。
`ollama ps` で確認すると、モデルは100% GPUで動いていた。

```bash
$ ollama ps
NAME                                ID              SIZE      PROCESSOR    CONTEXT
qwen2.5-coder:3b-instruct-q4_K_M    f72c60cabf62    2.7 GB    100% GPU     16384
```

READMEには「3BモデルならGPU無しでも動く」とあるので、CPUのみの速度も測った。
こちらはアプリを経由せず、同じ質問をOllamaのAPIに直接送り、`num_gpu` でGPU使用の有無を切り替えた参考値である。

```bash
$ curl -s localhost:11434/api/chat -d '{"model":"qwen2.5-coder:3b-instruct-q4_K_M","stream":false,"options":{"num_gpu":0},"messages":[...]}'
num_gpu=0   日本の首都は東京です。 | total 3.67s load 3.07s eval 8 tok 25.8 tok/s
num_gpu=99  日本の首都は東京です。理由は、日本の歴史的と文化的な中心地で、大都市であります。 | total 1.81s load 1.51s eval 28 tok 141.6 tok/s
```

CPUのみ(Ryzen 7 7700)でも約26 tok/sが出ており、3Bモデルでのチャットなら実用的な速度だった。

## コーディングエージェント: 課題の用意

左のサイドバーにある `<>` アイコンがコーディングエージェント(Codeタブ)である。
意図的にバグを入れた小さなPythonプロジェクトを用意した。

```bash
$ cat calc.py
def add(a, b):
    return a - b  # bug: should be a + b


def mul(a, b):
    return a * b

$ cat test_calc.py
from calc import add, mul

assert add(2, 3) == 5, f"add(2, 3) returned {add(2, 3)}"
assert mul(2, 3) == 6
print("all tests passed")

$ python3 test_calc.py
AssertionError: add(2, 3) returned -1
```

コメントに答えまで書いてある、かなり易しい課題である。
エージェントへの指示は全モデル共通で次の1文にした。

```
test_calc.py fails. Read calc.py and test_calc.py, fix the bug in calc.py, then run `python3 test_calc.py` to confirm it passes.
```

作業フォルダは右パネルの「Select folder...」から指定する。
ブラウザ版ではパスを入力するダイアログ(`window.prompt`)が出る方式で、デスクトップ版ではネイティブのフォルダ選択ダイアログになる。

権限モードは既定の「Ask」のままにした。
このモードでは、シェルコマンドは「needs your ok」と表示されて Run / No / Accept without asking の承認待ちになる。
ファイル編集はすぐには反映されず、「Pending」としてdiff付きで溜まり、Apply all / Reject all で反映するかを決める。
操作はPlaywrightで自動化し、承認するのは `python3 test_calc.py` の実行と `calc.py` への編集だけに限定した。

## 結果: 成功したのは14Bだけ

| モデル | 試行 | 結果 | 所要時間 |
|---|---|---|---|
| qwen2.5-coder:3b-instruct-q4_K_M | 2回 | 2回とも失敗。テストの失敗を確認したところで、修正もメッセージも出さずに終了 | 約11秒 |
| qwen2.5:7b-instruct | 2回 | 2回とも失敗。存在しない `src/` を探し続け、Loop guardが停止 | 約10秒 |
| qwen2.5:14b-instruct | 1回 | 成功。`calc.py` を修正してテスト通過、変更内容を要約して終了 | 約15秒 |

### 3B: テストを走らせたところで黙って終わる

3Bは2回とも同じ動きだった。

```
file_read      calc.py
file_read      test_calc.py
shell_execute  python3 test_calc.py
Error (1): AssertionError: add(2, 3) returned -1
4,733 in · 177 out
```

両方のファイルを読み、テストを実行して失敗を確認するところまでは指示どおりに進んだ。
しかしそこで処理が終わり、`file_edit` も、最終的な説明メッセージも出てこなかった。
画面上は正常終了と見分けがつかないため、ステップの中身を開かないと「何もしていない」ことに気づきにくい。

### 7B: 存在しないディレクトリを探してループする

7Bも2回とも同じ動きだった。

```
file_list  /home/matsu/work-day046/code-sandbox/src      → The folder is empty.
file_read  /home/matsu/work-day046/code-sandbox/src/calc.py
file_read  /home/matsu/work-day046/code-sandbox/src/test_calc.py
(同じ3手をもう一度)
⛔ Loop guard halted the run: same tool sequence repeated 3× in a row.
(halted: same tool sequence repeated 3× in a row. The model is looping. Try a stronger model for multi-step code tasks, or rephrase the instruction.)
```

作業フォルダの直下にファイルがあるにもかかわらず、7Bは `src/` 配下にあると思い込み、空のフォルダを見てはまた同じ探索を繰り返した。
アプリのLoop guardが「同じツール呼び出しの並びが3回続いた」ことを検知して止め、「もっと強いモデルを使うか、指示を言い換えてほしい」と案内を出した。
ループで延々とトークンを消費し続けることは防がれていた。

### 14B: 修正してテストを通す

14Bのツール呼び出しは次のとおりだった。

```
file_read      calc.py
file_read      test_calc.py
file_edit      calc.py
               old_string: "return a - b  # bug: should be a + b"
               new_string: "return a + b  # fixed"
               → Pending(ステージのみ、未反映)
shell_execute  python3 test_calc.py
               → Error (1): AssertionError: add(2, 3) returned -1
"The assertion error indicates that the add function is still returning -1 ... Let's confirm the fix in calc.py and re-run the test."
file_edit      calc.py → file_edit: old_string not found in .../calc.py.
shell_execute  python3 test_calc.py → all tests passed
"The test now passes, confirming the fix in calc.py was applied correctly. ..."
10,051 in · 385 out
Applied staged change: /home/matsu/work-day046/code-sandbox/calc.py
```

```bash
$ git diff
-    return a - b  # bug: should be a + b
+    return a + b  # fixed
$ python3 test_calc.py
all tests passed
```

正しい修正を出し、テストを通し、何をしたかを要約して終わった。
`ollama ps` では14Bは `15 GB  7%/93% CPU/GPU` と表示され、16GBのVRAMにほぼ収まった状態で約15秒で完了した。

## 気づいた点: 承認前の編集のままテストが走る

14Bのログには1つ引っかかる点があった。
`file_edit` の直後にテストが走って失敗しているのは、その時点では編集が「Pending」に溜まっているだけで、まだファイルに反映されていなかったためである。
Askモードでは、ファイル編集の承認を待たずにエージェントが次のツール(テスト実行)へ進んでしまう。

14Bはその失敗を見て再度編集を試み、「old_string not found」(その間に反映済みだったため)を受けてテストを再実行し、最終的に成功した。
賢いモデルなら立て直せるが、承認のタイミングによっては余計な往復が発生する。
「編集を見てから承認したい、でも承認前にテストを走らせても意味がない」という状況では、編集の承認が済むまでシェル実行を待つ動作のほうが自然だと感じた。

## ライセンス

- locally-uncensored本体: AGPL-3.0-only(`LICENSE` ファイル全文と `package.json` の `license` フィールドで確認)。改変して配布する場合や、ネットワーク越しにサービスとして提供する場合はソース開示義務が生じる。
- 使用したモデル: Qwen2.5系(Ollama経由で取得済みのもの)。各モデルのライセンスはモデル配布元に従う。

## まとめ

- `npm ci --ignore-scripts` と `npm run dev` だけで、ブラウザ版が起動し、既存のOllamaとモデルを自動で認識した。
- チャットは3Bモデルで問題なく動き、CPUのみでも約26 tok/s(Ollama直接計測)だった。
- コーディングエージェントに単純なバグ修正をさせると、3Bは修正せずに黙って終了、7Bは存在しないディレクトリを探してループし、成功したのは14Bだけだった。
- アプリ側のdiff付きステージング・承認制のシェル実行・Loop guardはどのモデルでも正しく動いた。成否を分けたのはモデルの能力である。
- Askモードでは、承認前の編集のままテストが走るため、1回目のテストは必ず失敗する。

「ローカルLLMだけで完結するコーディングエージェント」は、アプリの側はすでに形になっていた。
ただ、今回の易しい課題ですら7B以下では解けず、エージェント用途ではモデル選び、つまり手元のVRAMがそのまま実用性を決めるという結果になった。
アプリがオンボーディングで9B級を「Agent-ready」として勧め、Loop guardが「より強いモデルを」と案内するのは、作者自身がこの境界を理解しているからだろう。
