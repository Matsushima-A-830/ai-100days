---
title: "クラウドAI不要を掲げるJarvisの知識グラフ・日記メモリを、ローカルLLMで手を動かして検証した"
emoji: "🧠"
type: "tech"
topics: ["ai", "llm", "sqlite", "python", "oss"]
published: false
---

## 今日の対象: isair/jarvis

[isair/jarvis](https://github.com/isair/jarvis)は、Ollama・LM Studio・llama.cppなどローカルのモデルサーバーだけで動く音声対応デスクトップAIアシスタントである(独自ライセンス。個人・教育・研究目的の非商用利用は無料、商用利用は著者への別途連絡が必要)。
READMEには「No cloud AI service is required」「No subscription」と明記されており、トレイに常駐して音声で話しかけると答えてくれるGUIアプリがメインの使い方になる。

筆者が今回検証したのは、GitHub上のタグ`v2.9.0`(コミット`9d90257`)である。

今回は、このGUI・音声対話の部分には触れない。
筆者が確かめたかったのは、READMEの前面に出ている音声対話機能の裏側にある、個人メモリ(ローカル日記+知識グラフ)のバックエンド実装が、ドキュメント(`graph.spec.md`)に書かれている仕様のとおりに動くかどうかである。

## なぜ知識グラフに絞ったか

jarvisの個人メモリは二層構造になっている。

- **日記(diary)**: 「何が起きたか」を会話要約として時系列で記録する。FTS5全文検索とベクトル検索を融合したハイブリッド検索を持つ。
- **知識グラフ(knowledge graph)**: 「何を学んだか」を、User/Directives/Worldという3つの固定ブランチの下にツリー状で蓄積する。ノードが一定トークン数を超えると、LLMが2〜5個のカテゴリに自動分割し、重複は統合し、矛盾は新しい記述が古い記述を上書きする。

`graph.spec.md`を読むと、この自動分割・統合・ハルシネーション防止(モデルが暴走して行数を膨らませた書き換えは拒否する)まで、かなり具体的な仕様が書かれている。
実際にコードがそのとおり動くのかを、同梱のテストスイート、自分で書いた小さなスクリプト、そしてOllama上のローカルLLMを使った評価スイートで確認した。

## セットアップで気づいたこと

`requirements.txt`は146行あり、音声認識(`faster-whisper`)・音声合成(`chatterbox-tts`、`piper-tts`)・GUI(`PyQt6`一式)・ベクトル検索(`faiss-cpu`)まで全部入りの重量級構成になっている。
今回は知識グラフ・日記のバックエンドロジックの検証に絞るため、`sounddevice`・`faster-whisper`・`chatterbox-tts`・`piper-tts`・`pygame`・`faiss-cpu`・`PyQt6-WebEngine`はインストールしなかった。

```bash
$ uv venv -p 3.12 .venv
$ VIRTUAL_ENV=.venv uv pip install python-dotenv flask filelock requests curl_cffi \
    urllib3 beautifulsoup4 lxml html2text numpy pytest pytest-repeat mcp \
    pydantic rapidfuzz pynput geoip2 webrtcvad pytesseract Pillow psutil \
    playwright PyQt6 pyyaml
```

`PyQt6`だけは、テストファイルがデスクトップアプリ本体を直接importする構成になっているため入れたが、実行はヘッドレス(`QT_QPA_PLATFORM=offscreen`)にした。
テストスイート自体に、`QApplication`をプロセス全体で1つだけ生成し直し続ける`qapp`フィクスチャが用意されており、「ディスプレイもxvfbも無い環境でも実Qtアプリとして動かす」ことが最初から想定されていた。

## テストスイートを実際に動かした結果

```bash
$ QT_QPA_PLATFORM=offscreen PYTHONPATH=jarvis-src/src \
    .venv/bin/python -m pytest -c jarvis-src/pytest.ini jarvis-src/tests -m unit -q
...
134 failed, 5451 passed, 3 skipped, 190 deselected, 2 warnings, 367 errors in 255.52s (0:04:15)
```

5,451件成功という数字だけ見ると景気がいいが、正直に内訳を書く。
134件の失敗と367件の収集エラーを分類すると、**その全部が、意図的に入れなかった音声/TTS/ベクトル検索パッケージの欠落が原因**だった。
たとえば`faiss`をパラメータに持つテストは、`[faiss]`版と無印(純Python実装の`PythonVectorStore`)版の両方で定義されており、**無印側はすべて成功している**。
知識グラフ・対話メモリ・日記検索そのもののコード(`memory/`配下)に、実際のバグが見つかったわけではない。

知識グラフに関係するテストだけに絞ると、こうなる。

```bash
$ PYTHONPATH=jarvis-src/src .venv/bin/python -m pytest -c jarvis-src/pytest.ini \
    jarvis-src/tests/test_graph_memory.py jarvis-src/tests/test_graph_ops.py \
    jarvis-src/tests/test_graph_memory_tools.py -m unit -v
...
172 passed in 10.59s
```

## LLM無し・モック無しで手を動かして確認した3つのこと

テストスイートはLLM呼び出しをモックしている。
「本物のSQLiteに対して実際に読み書きする」部分は、自分でスクリプトを書いて別に確かめた。

### 1. `recall_gate.should_recall()` — LLMを一切使わない決定的ヒューリスティック

jarvisは、会話が続いているときに毎回日記・知識グラフを検索すると無駄にコストと文脈が膨らむため、「ホットウィンドウ(直近の会話)がすでに答えをカバーしているなら、記憶検索をスキップする」というゲートを持つ。
LLMは一切呼ばず、ツール結果の有無とキーワードの重なり(カバレッジ50%以上)だけで判定する純粋なPythonコードである。

```python
from jarvis.memory.recall_gate import should_recall

should_recall(
    "What's the weather in Tokyo right now?",
    [
        {"role": "user", "content": "What's the weather in Tokyo right now?"},
        {"role": "user", "tool_name": "weather", "content": "Tokyo: 18C, light rain, humidity 72%"},
    ],
)
```

実行結果:

```
- fresh tool result + high overlap -> should SKIP recall
  should_recall() -> False  =>  SKIP recall
- fresh tool result but LOW overlap -> should RECALL
  should_recall() -> True  =>  RECALL
- high overlap but NO tool result -> should RECALL
  should_recall() -> True  =>  RECALL
- empty hot window -> should RECALL (fail open)
  should_recall() -> True  =>  RECALL
```

仕様書(`recall_gate.spec.md`)の「ツール結果があり、かつカバレッジが50%以上のときだけスキップ、それ以外はfail-openでRECALL」というルールどおりに動いた。

### 2. `GraphMemoryStore` — 実SQLiteへのcreate/append/search/top

知識グラフのコア、`GraphMemoryStore`に対して、ブランチへのノード作成・ファクトの追記・キーワード検索・アクセス頻度ランキングを直接呼び出した。

```
bootstrap: 4 nodes (root + 3 fixed branches: ['user', 'directives', 'world'])
create_node -> id=38efb1db... data='user prefers black coffee, no sugar' tokens=8
after 2 appends: tokens=32 (SPLIT_THRESHOLD=1500) over_threshold=False
after bulk append: tokens=4405 over_threshold=True
search_nodes('coffee') -> 2 hits:
  - 'Coffee preference' ...
  - 'Local cafe hours' ...
get_top_nodes(5) -> ['Local cafe hours', 'Coffee preference', 'User', 'Directives', 'World']
```

自動分割(auto-split)自体はLLM呼び出しを伴うためこのスクリプトでは実行していないが、分割が必要かどうかを決める「1500トークンを超えたか」の判定はLLMを使わないローカルなトークン推定(`len(text)/4`のヒューリスティック)で、実際に閾値を超えさせて`over_threshold=True`になることを確認した。

### 3. `Database.search_hybrid` — FTS5キーワード検索

4件の日記エントリ(コーヒー関連2件、関係ない話題2件)を実際に保存し、`coffee`で検索した。

```
search_hybrid(fts_query='coffee', query_vec_json=None) -> 2 hits:
  - [2026-11-14] User mentioned switching from drip coffee to an espresso machine. ...
  - [2026-11-10] User asked how to make cold brew coffee at home, discussed grind size. ...
```

コーヒーと関係ないエントリは正しく除外された。
一つ意外だったのは、`faiss-cpu`も`sqlite-vss`も入れていないのに`has_vector_store`が`True`を返したことだ。
ソースを読むと、埋め込みモデルや`sqlite-vss`が無くても`numpy`さえあれば純Python実装の`PythonVectorStore`にフォールバックする作りになっている。
今回は埋め込みモデル自体を用意していないので、実際の検索はFTS5キーワードのみで行われた。

## ローカルLLM(Ollama + gemma4:e4b)で抽出・マージを動かした

ここまでの確認はLLMを呼ばない範囲に限られていた。
知識グラフの本体である「会話要約からのファクト抽出」「格納先ノードの選択」「既存ノードとのマージ」はすべてLLM呼び出しなので、jarvisのデフォルトチャットモデルである`gemma4:e4b`をOllamaで用意して実際に動かした。
検証環境はRTX 5060 Ti(VRAM 16GB)のWindows PC上のWSL2、Ollama 0.35.1である。

```bash
$ ollama pull gemma4:e4b
$ ollama pull nomic-embed-text
```

### 評価スイートは26ファイルが収集エラーで動かなかった

jarvisには、実LLMを相手にした評価スイート`evals/`(776件)が同梱されている。
ところが公式の実行スクリプト(`scripts/run_evals.sh`)と同じ`python -m pytest evals/`で収集しただけで、26ファイルがエラーになった。

```bash
$ EVAL_JUDGE_MODEL=gemma4:e4b .venv/bin/python -m pytest evals/ --collect-only -q
...
E   ImportError: cannot import name 'requires_judge_llm' from 'conftest' (.../jarvis-src/conftest.py)
...
!!!!!!!!!!!!!!!!!!! Interrupted: 26 errors during collection !!!!!!!!!!!!!!!!!!!
612 tests collected, 26 errors in 1.47s
```

原因は、2026-10-14にリポジトリ直下へ追加された`conftest.py`(テスト中の実オーディオアクセスを禁止するもの)である。
`evals/`配下のうち26ファイルは`from conftest import requires_judge_llm`と書かれており、pytestが先に読み込んだリポジトリ直下の`conftest`に解決されてしまう。
残り32ファイルは`from evals.conftest import ...`と書かれていて問題なく動く。
検証用のcloneで、該当26ファイルのimport行だけを`from evals.conftest import`に置き換えると、776件すべてが収集できた。

```bash
$ grep -rl "^from conftest import" evals | xargs sed -i 's/^from conftest import/from evals.conftest import/'
$ EVAL_JUDGE_MODEL=gemma4:e4b .venv/bin/python -m pytest evals/ --collect-only -q
776 tests collected in 1.17s
```

### 知識グラフ関連の評価: 51件成功

知識グラフに関係する6ファイル(抽出・抽出JSON・マージ・分割容量・ブランチ振り分け・新旧情報の上書き)を、`gemma4:e4b`で実行した。

```bash
$ EVAL_JUDGE_PROVIDER=ollama EVAL_JUDGE_MODEL=gemma4:e4b .venv/bin/python -m pytest -rA \
    evals/test_knowledge_extraction.py evals/test_graph_extraction_json.py \
    evals/test_merge_consolidation.py evals/test_graph_split_capacity.py \
    evals/test_graph_branch_routing.py evals/test_recency_superseding.py
...
SKIPPED [4] evals/test_recency_superseding.py:376: Chat model is parametrised here; only runs once per eval session (large judge phase)
================== 51 passed, 4 skipped in 167.14s (0:02:47) ===================
```

| ファイル | 成功 | 失敗 |
|---|---|---|
| test_knowledge_extraction.py | 19 | 0 |
| test_graph_extraction_json.py | 3 | 0 |
| test_merge_consolidation.py | 11 | 0 |
| test_graph_split_capacity.py | 4 | 0 |
| test_graph_branch_routing.py | 6 | 0 |
| test_recency_superseding.py | 8 | 0 |

スキップされた4件は、大きなジャッジモデルで評価するフェーズ専用のテストで、テストコード側の設計どおりである。

### モック無しで会話2回分を知識グラフに流し込む

評価スイートとは別に、`graph_ops.update_graph_from_dialogue()`を実LLMで直接呼ぶスクリプト(`demo_live_graph_update.py`)を書いた。
1回目の会話要約には「東京在住・Goのバックエンドエンジニア・ブラックコーヒー派・箇条書きで答えてほしい」という恒久的な情報と、「今日は晴れだった」という一時的な情報を混ぜた。
2回目は「先週末に大阪へ引っ越した」「ブラックコーヒーをやめてオーツミルクラテを飲み始めた」という、1回目と矛盾する情報である。

```bash
$ MODEL=gemma4:e4b PYTHONPATH=jarvis-src/src .venv/bin/python demo_live_graph_update.py
model=gemma4:e4b

[2026-11-10] update_graph_from_dialogue -> stored=4 skipped=0 (2.0s)
  + 'The user lives in Tokyo' -> User
  + 'The user works as a backend engineer using Go' -> User
  + 'The user prefers black coffee with no sugar' -> User
  + 'Always answer in short bullet points' -> Directives
graph now:
- Root
  - Directives: Always answer in short bullet points
  - User: The user lives in Tokyo | The user works as a backend engineer using Go | The user prefers black coffee with no sugar
  - World

[2026-11-15] update_graph_from_dialogue -> stored=0 skipped=0 (1.7s)
graph now:
- Root
  - User: The user lives in Osaka | The user works as a backend engineer using Go | The user drinks oat milk lattes
  - Directives: Always answer in short bullet points
  - World
```

天気の話は「一時的な情報」として捨てられ、応答スタイルの指示は`Directives`ブランチに振り分けられた。
2回目の会話では、`Tokyo`の行が`Osaka`に、ブラックコーヒーの行がオーツミルクラテに書き換えられ、Goエンジニアという変わっていない情報はそのまま残った。
`graph.spec.md`にある「矛盾は新しい記述が古い記述を上書きする」がそのとおりに動いている。
同じスクリプトを3回実行し、3回とも同じグラフになった。

一つ引っかかったのは、2回目の戻り値が`stored=0`になっていることだ。
グラフの中身は確かに更新されているのに、「新しく保存したファクト」は0件と報告される。
ソースを読むと、マージ後のノードに抽出時の文言がそのまま残ったファクトだけを`stored`として数える作りになっていた。
今回は`gemma4:e4b`が「The user moved to Osaka」を「The user lives in Osaka」に言い換えて既存行を書き換えたため、カウントに入らなかったと考えられる。
データが失われたわけではないが、戻り値のログだけを見て「覚えてくれなかった」と判断すると見誤る。

## まとめ

- 同梱のユニットテストは5,451件が成功し、残る失敗・エラーは全て意図的に入れなかった音声/TTS/ベクトル検索パッケージの欠落が原因で、知識グラフ・日記のコードのバグではなかった。
- LLMを使わない3つの部分(recall gate・分割閾値判定・FTS5検索)は、モックなしの実SQLiteに対する自作スクリプトで仕様どおりに動くことを直接確認できた。
- 実LLM相手の評価スイートは、`v2.9.0`時点で26ファイルが`conftest`のimport衝突で収集エラーになる。import行を直すと、知識グラフ関連の51件は`gemma4:e4b`ですべて成功した。
- モック無しで会話2回分を流し込むと、一時的な情報の除外・ブランチ振り分け・矛盾する情報の上書きまで仕様どおりに動いた。ただし上書きは戻り値上`stored=0`と報告される。

「クラウド不要」を掲げるツールの記憶の仕組みが、手元のGPU1枚とOllamaだけで、仕様書どおりに動くところまで自分の手で確かめられた。

## 参考

- isair/jarvis: https://github.com/isair/jarvis (独自ライセンス。非商用利用は無料)
- 知識グラフの仕様: https://github.com/isair/jarvis/blob/main/src/jarvis/memory/graph.spec.md
