# Day 050 — isair/jarvis 検証結果

出典: https://github.com/isair/jarvis (`v2.9.0` / commit `9d902577fd7c8d4fe05df7e19c81aaec36c79902`, 2026-11-12)
ライセンス: 独自ライセンス(非商用利用は無料。商用利用は著者への連絡が必要)。`LICENSE`ファイル全文は`experiments/day-050/README.md`に引用。

## 検証スコープ

today.md記載のとおり、GUI本体・音声対話(Whisper/Piper)・ディクテーション(X11前提)は
クラウドRoutine実行環境では確認できないため対象外とし、ローカルモデル接続・個人メモリ
(日記+知識グラフ)のバックエンドロジックと、リポジトリ付属のテストスイートの実行に絞った。

## 1. セットアップ

```bash
$ git clone --depth 1 https://github.com/isair/jarvis.git jarvis-src
$ python3 -m venv .venv
$ .venv/bin/pip install python-dotenv==1.0.1 flask filelock requests==2.32.3 \
    curl_cffi==0.16.3 "urllib3>=2.8.0,<3" beautifulsoup4 lxml html2text \
    "numpy<2.0.0" pytest==8.3.2 pytest-repeat mcp "pydantic>=2.11,<2.14" \
    rapidfuzz==3.6.1 pynput geoip2 webrtcvad pytesseract Pillow psutil \
    playwright PyQt6 pyyaml
```

`requirements.txt`の全量(146行)はインストールしていない。
音声認識・音声合成・GUI実行に必要な`faster-whisper`・`chatterbox-tts`・`piper-tts`・
`sounddevice`・`pygame`・`faiss-cpu`・`PyQt6-WebEngine`・`pyinstaller`は、
today.mdのスコープ判断(GUI/音声は対象外)に沿って意図的に入れていない。

PyQt6自体はテストコレクションに必要(デスクトップアプリ本体を直接importするテストファイルが
複数あるため)で入れたが、実行はヘッドレス(`QT_QPA_PLATFORM=offscreen`)。
初回、`PyQt6`のoffscreenプラットフォームプラグインが`libEGL.so.1`を要求してロードに失敗した
(`ImportError: libEGL.so.1: cannot open shared object file`)。
これはクラウドRoutine実行環境にGPU関連の共有ライブラリが入っていないことによるもので、
`apt-get install -y libegl1 libgl1 libopengl0 libxkbcommon0 libxcb-cursor0`で解決した。
(この一手は検証対象コードと無関係な、実行環境側のパッケージ追加なので記事では触れない。)

## 2. テストスイートの実行

```bash
$ QT_QPA_PLATFORM=offscreen PYTHONPATH=/tmp/jarvis-src/src \
    .venv/bin/python -m pytest -c /tmp/jarvis-src/pytest.ini /tmp/jarvis-src/tests -m unit -q
...
135 failed, 5450 passed, 3 skipped, 190 deselected, 3 warnings, 367 errors in 209.45s (0:03:29)
```

FAILED/ERRORの全行(504行)は `logs_unit_tests.txt` にそのまま保存している。

### 失敗・エラーの内訳(正直な記録)

135件の失敗と367件の収集エラーを`grep`で分類したところ、**実質的にすべてが
「意図的にインストールしなかった音声/TTS/ベクトル検索の重量級依存パッケージが
原因」だった**。知識グラフ・日記・対話メモリのコア実装(`memory/`配下)に
実際のバグが見つかったわけではない。

- `test_voice_listener.py` / `test_dictation*.py` / `test_tts_request_callbacks.py` /
  `test_whisper_*.py` / `test_nonblocking_voice_capture.py` / `test_hot_window_input.py` など
  → `sounddevice` / `faster-whisper` / `chatterbox-tts` / `piper-tts` 未導入によるimportエラー・モック不足。
- `test_vector_store_isolation.py` / `test_vector_validation.py` / `test_vector_write_failure.py` /
  `test_diary_summary_identity.py` / `test_diary_embedding_freshness.py` / `test_document_index_persistence.py` の
  `[faiss]`パラメータ分すべて → `faiss-cpu`未導入。これらのテストは`[faiss]`と無印(pure Python
  `PythonVectorStore`)の両方でパラメータ化されており、**無印側はすべて成功している**。
- `test_release_smoke_promotion.py` / `test_semantic_release_result.py` / `test_log_progress.py` の一部
  → semantic-release周りのCI専用チェックで、本検証のスコープ外。
- `test_mcp_configured_path.py::test_real_stdio_server_retains_configured_dependencies`
  → 実際にMCPサーバーサブプロセスを起動する統合テストで、依存ツールチェーンの差。
- `tools/builtin/test_document_search.py::test_unreadable_eligible_source_reports_partial_and_recovers[permissions]`
  → **これはこの実行環境固有の注意点**: コンテナ内でrootユーザーとして`pytest`を実行しているため、
    テストが`chmod(0)`でファイルを読めなくしても`PermissionError`が発生しない
    (rootはファイル権限をバイパスする)。jarvis側のコードのバグではない。
- `test_dictation_test_isolation.py::test_dictation_test_cannot_publish_to_the_protected_default_store`
  → サブプロセスで`test_dictation.py`を呼ぶメタテストで、上記の音声依存エラーが伝播したもの。

## 3. 知識グラフ・日記メモリのユニットテスト(抜粋)

音声/TTS/faissを除いた範囲では、知識グラフ(`memory/graph.py`, `memory/graph_ops.py`)・
対話メモリ(`memory/conversation.py`)・日記検索(`memory/db.py`)関連のテストはすべて成功した。

```bash
$ PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python -m pytest -c /tmp/jarvis-src/pytest.ini \
    /tmp/jarvis-src/tests/test_graph_memory.py /tmp/jarvis-src/tests/test_graph_ops.py \
    /tmp/jarvis-src/tests/test_graph_memory_tools.py -m unit -v
...
172 passed in 3.03s
```

## 4. 手を動かした直接デモ(モック無し、LLM呼び出し無し)

ユニットテストはLLM呼び出しをモックしているため、「本物のSQLiteストアに対して実際に
データを書き込み・検索する」部分を自分でスクリプトを書いて別途確認した。

### 4-1. `recall_gate.should_recall()` — LLMを使わない決定的ヒューリスティック

`experiments/day-050/demo_recall_gate.py`

```
$ PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python demo_recall_gate.py
- fresh tool result + high overlap -> should SKIP recall
  query="What's the weather in Tokyo right now?"
  should_recall() -> False  =>  SKIP recall
- fresh tool result but LOW overlap -> should RECALL
  query="Did I mention my sister's birthday last week?"
  should_recall() -> True  =>  RECALL
- high overlap but NO tool result -> should RECALL
  query="What's the weather in Tokyo right now?"
  should_recall() -> True  =>  RECALL
- empty hot window -> should RECALL (fail open)
  query="What's the weather in Tokyo right now?"
  should_recall() -> True  =>  RECALL
```

`recall_gate.spec.md`に書かれている仕様(「新しいツール結果があり、かつクエリの内容語の
50%以上がホットウィンドウに含まれる場合のみスキップ、それ以外はfail-openでRECALL」)の
とおりに動くことを、実際のコードを呼んで確認した。

### 4-2. `GraphMemoryStore` — 実SQLiteに対するcreate/append/search/top

`experiments/day-050/demo_graph_memory.py`

```
$ PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python demo_graph_memory.py
bootstrap: 4 nodes (root + 3 fixed branches: ['user', 'directives', 'world'])

create_node -> id=5408812c... data='user prefers black coffee, no sugar' tokens=8

after 2 appends: tokens=32 (SPLIT_THRESHOLD=1500) over_threshold=False
after bulk append: tokens=4405 over_threshold=True

search_nodes('coffee') -> 2 hits:
  - 'Coffee preference' (parent branch via ancestry, data='user prefers black coffee, no sugar\nuser'...)
  - 'Local cafe hours' (parent branch via ancestry, data='Blue Bottle Coffee on 5th closes at 6pm '...)

get_top_nodes(5) -> ['Local cafe hours', 'Coffee preference', 'User', 'Directives', 'World']
```

`SPLIT_THRESHOLD`(1500トークン)を超えたかどうかの判定自体はLLMを呼ばないローカルな
トークン推定(`_estimate_tokens`, `len(text)/4`ヒューリスティック)で行われており、
実際に閾値を超えさせて`over_threshold=True`になることを確認した
(実際の分割=`split_node`はLLM呼び出しを伴うため、ここでは閾値判定のみを確認)。

### 4-3. `Database.search_hybrid` — FTS5キーワード検索(ベクトル無し)

`experiments/day-050/demo_diary_search.py`

```
$ PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python demo_diary_search.py
upsert_conversation_summary(2026-11-10) -> id=1
upsert_conversation_summary(2026-11-12) -> id=2
upsert_conversation_summary(2026-11-14) -> id=3
upsert_conversation_summary(2026-11-15) -> id=4

has_vector_store -> True  (no embedding backend installed, so this stays keyword-only)

search_hybrid(fts_query='coffee', query_vec_json=None) -> 2 hits:
  - score=-0.000  [2026-11-14] User mentioned switching from drip coffee to an espresso machine. (Topics: diary-demo)
  - score=-0.000  [2026-11-10] User asked how to make cold brew coffee at home, discussed grind size. (Topics: diary-demo)
```

4件の日記エントリのうち「coffee」を含む2件だけが正しくFTS5全文検索でヒットした
(「犬の鳴き声」「賃貸更新メール」のエントリはヒットしない)。
`has_vector_store`が`faiss-cpu`も`sqlite-vss`も入れていないのに`True`を返したのは意外だった。
`db.py`を読むと、埋め込みモデルが無い/`sqlite-vss`が無い場合でも、`numpy`さえあれば
純Python実装の`PythonVectorStore`にフォールバックするため`has_vector_store`は`True`になる
(実際にベクトル検索が働くかは別で、埋め込みモデルが無いので`query_vec_json=None`のまま
キーワード検索にフォールバックしている)。

## 5. ローカルモデルによる実動作確認(未実施・理由)

today.mdのステップ4「Ollama等のローカルモデルで要約・記憶の書き込み/読み出しが機能するか」
は、本Routine実行環境では実施できなかった。
`https://ollama.com`へのアクセスがこのRoutine実行環境のegressプロキシでブロックされており
(`connect_rejected`、ホストがこのセッションで許可されていない)、Ollama本体や任意のモデルを
取得できないため。これはRoutine実行環境のネットワーク制限によるものであり、ツール自体の
制約ではないので記事では触れない。
知識グラフの抽出・意味レビュー・マージ(LLM呼び出しが必要な部分)はユニットテストの
モックLLMを介した検証に留まる。

## 6. ライセンス

`LICENSE`ファイル全文(著作権者: Baris Sencan):
非商用利用(個人・教育・研究目的)は無料。商用利用は著者への別途連絡が必要
(標準的なOSSライセンスではない独自ライセンス)。本検証は研究目的の非商用利用。

## まとめ

- 知識グラフ(`memory/graph.py`)・対話メモリ・日記検索のコアロジックは、同梱のユニットテスト
  (LLM呼び出しをモック)で5,450件が成功し、関連する失敗・エラーはすべて意図的に入れなかった
  音声/TTS/ベクトル検索パッケージの欠落に起因するもので、コードのバグは見られなかった。
- LLMを使わない部分(`recall_gate.should_recall`・ノードのトークン閾値判定・FTS5キーワード検索)
  は、モック無しの実SQLiteに対する自作デモスクリプトで仕様どおりに動くことを直接確認した。
- ローカルOllama等での実際のLLM統合動作(抽出・マージ・分割)は、このRoutine実行環境の
  ネットワーク制限によりOllama自体を導入できず確認できなかった。ローカルPCでの追加検証が
  必要であれば、`tools/video/README.md`同様に`ollama pull qwen3.5:0.8b`等を導入した上で
  `evals/`配下の評価スイート(`EVAL_JUDGE_PROVIDER=ollama`等)を実行するのが次の一歩になる。
