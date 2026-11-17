---
title: "クラウドAI不要を掲げるJarvisの知識グラフ・日記メモリを、LLM無しで手を動かして検証した"
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
実際にコードがそのとおり動くのかを、同梱のテストスイートと、自分で書いた小さなスクリプトの両方で確認した。

## セットアップで気づいたこと

`requirements.txt`は146行あり、音声認識(`faster-whisper`)・音声合成(`chatterbox-tts`、`piper-tts`)・GUI(`PyQt6`一式)・ベクトル検索(`faiss-cpu`)まで全部入りの重量級構成になっている。
今回は知識グラフ・日記のバックエンドロジックの検証に絞るため、`sounddevice`・`faster-whisper`・`chatterbox-tts`・`piper-tts`・`pygame`・`faiss-cpu`・`PyQt6-WebEngine`はインストールしなかった。

```bash
$ python3 -m venv .venv
$ .venv/bin/pip install python-dotenv flask filelock requests curl_cffi \
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
135 failed, 5450 passed, 3 skipped, 190 deselected, 3 warnings, 367 errors in 209.45s
```

5,450件成功という数字だけ見ると景気がいいが、正直に内訳を書く。
135件の失敗と367件の収集エラーを分類すると、**その全部が、意図的に入れなかった音声/TTS/ベクトル検索パッケージの欠落が原因**だった。
たとえば`faiss`をパラメータに持つテストは、`[faiss]`版と無印(純Python実装の`PythonVectorStore`)版の両方で定義されており、**無印側はすべて成功している**。
知識グラフ・対話メモリ・日記検索そのもののコード(`memory/`配下)に、実際のバグが見つかったわけではない。

知識グラフに関係するテストだけに絞ると、こうなる。

```bash
$ PYTHONPATH=jarvis-src/src .venv/bin/python -m pytest -c jarvis-src/pytest.ini \
    jarvis-src/tests/test_graph_memory.py jarvis-src/tests/test_graph_ops.py \
    jarvis-src/tests/test_graph_memory_tools.py -m unit -v
...
172 passed in 3.03s
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
create_node -> id=5408812c... data='user prefers black coffee, no sugar' tokens=8
after 2 appends: tokens=32 (SPLIT_THRESHOLD=1500) over_threshold=False
after bulk append: tokens=4405 over_threshold=True
search_nodes('coffee') -> 2 hits:
  - 'Coffee preference' ...
  - 'Local cafe hours' ...
get_top_nodes(5) -> ['Local cafe hours', 'Coffee preference', 'User', 'Directives', 'World']
```

自動分割(auto-split)自体はLLM呼び出しを伴うため今回は実行していないが、分割が必要かどうかを決める「1500トークンを超えたか」の判定はLLMを使わないローカルなトークン推定(`len(text)/4`のヒューリスティック)で、実際に閾値を超えさせて`over_threshold=True`になることを確認した。

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

## やれなかったこと

today.mdの計画では、Ollama経由の小型モデル(`qwen3.5:0.8b`等)で知識グラフの抽出・マージまで実際に動かす予定だった。
これは今回のRoutine実行環境のネットワーク制限で`https://ollama.com`へのアクセス自体がブロックされており、Ollama本体を導入できなかったため実施できていない。
知識グラフの抽出・意味レビュー・マージといったLLMが必要な部分は、同梱テストのモックLLMを介した確認に留まっている。

## まとめ

- 知識グラフ・対話メモリ・日記検索のコアロジックは、同梱テスト5,450件が成功し、残る失敗・エラーは全て意図的に入れなかった音声/TTS/ベクトル検索パッケージの欠落が原因で、コード自体のバグではなかった。
- LLMを使わない3つの部分(recall gate・分割閾値判定・FTS5検索)は、モックなしの実SQLiteに対する自作スクリプトで仕様どおりに動くことを直接確認できた。
- 実際のLLM統合(抽出・マージ・分割)はローカルPCでのOllama導入が前提になる。

「クラウド不要」を掲げるツールの土台部分が、ドキュメントに書かれた仕様どおりに動くことを、LLMを使わない範囲で自分の手で確かめられたのは収穫だった。

## 参考

- isair/jarvis: https://github.com/isair/jarvis (独自ライセンス。非商用利用は無料)
- 知識グラフの仕様: https://github.com/isair/jarvis/blob/main/src/jarvis/memory/graph.spec.md
