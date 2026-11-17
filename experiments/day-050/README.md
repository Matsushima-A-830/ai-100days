# Day 050 — isair/jarvis

出典: https://github.com/isair/jarvis (`v2.9.0` / commit `9d902577fd7c8d4fe05df7e19c81aaec36c79902`)

## これは何か

クラウドAIサービスを使わず、Ollama/LM Studio/llama.cppなどローカルのモデルサーバーだけで
動く音声対応デスクトップAIアシスタント。音声対話(Whisper/Piper)・個人メモリ
(ローカル日記+知識グラフ)・MCP連携を備える。

本検証では、GUI本体・音声対話・ディクテーションはクラウドRoutine実行環境では確認できない
ため対象外とし、ローカルモデル接続・個人メモリ(日記+知識グラフ)のバックエンドロジックと
同梱テストスイートの実行に絞った。詳細な結果は `results.md` を参照。

## ライセンス全文

`LICENSE`ファイル(著作権者: Baris Sencan)より:

```
Jarvis AI Assistant License

Copyright (c) 2025 Baris Sencan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to use,
copy, modify, merge, publish, and distribute the Software for non-commercial
purposes, subject to the following conditions:

NON-COMMERCIAL USE:
You may use, copy, modify, merge, publish, and distribute the Software for
personal, educational, research, or other non-commercial purposes without
charge, provided that:

1. The above copyright notice and this permission notice appear in all copies.
2. You do not sell, rent, lease, or otherwise commercialise the Software.
3. Any derivative works are also licensed under these same terms.

COMMERCIAL USE:
Commercial use of the Software requires a separate commercial license from
the copyright holder. ...
```

非商用利用(個人・教育・研究目的)は無料、商用利用は著者への別途連絡が必要な独自ライセンス。
本検証は研究目的の非商用利用として実施した。

## 再現手順

```bash
# 1. ソース取得
git clone --depth 1 https://github.com/isair/jarvis.git jarvis-src

# 2. 検証用venv(重量級の音声/TTS/ベクトル検索パッケージは意図的に除外。
#    理由はresults.mdの「1. セットアップ」を参照)
cd experiments/day-050
python3 -m venv .venv
.venv/bin/pip install python-dotenv==1.0.1 flask filelock requests==2.32.3 \
  curl_cffi==0.16.3 "urllib3>=2.8.0,<3" beautifulsoup4 lxml html2text \
  "numpy<2.0.0" pytest==8.3.2 pytest-repeat mcp "pydantic>=2.11,<2.14" \
  rapidfuzz==3.6.1 pynput geoip2 webrtcvad pytesseract Pillow psutil \
  playwright PyQt6 pyyaml

# 3. PyQt6のoffscreenプラットフォームプラグインがlibEGLを要求するため
#    (環境にGPU関連共有ライブラリが無い場合のみ必要):
#    apt-get install -y libegl1 libgl1 libopengl0 libxkbcommon0 libxcb-cursor0

# 4. 同梱ユニットテストの実行(音声/TTS/faiss関連は失敗/収集エラーになる。
#    理由と内訳はresults.mdを参照)
QT_QPA_PLATFORM=offscreen PYTHONPATH=../../../jarvis-src/src \
  .venv/bin/python -m pytest -c ../../../jarvis-src/pytest.ini ../../../jarvis-src/tests -m unit -q

# 5. 知識グラフ関連テストだけに絞った実行(全件成功)
QT_QPA_PLATFORM=offscreen PYTHONPATH=../../../jarvis-src/src \
  .venv/bin/python -m pytest -c ../../../jarvis-src/pytest.ini \
  ../../../jarvis-src/tests/test_graph_memory.py \
  ../../../jarvis-src/tests/test_graph_ops.py \
  ../../../jarvis-src/tests/test_graph_memory_tools.py -m unit -v

# 6. モック無し・LLM無しの手動デモ(このディレクトリの3本)
PYTHONPATH=../../../jarvis-src/src .venv/bin/python demo_recall_gate.py
PYTHONPATH=../../../jarvis-src/src .venv/bin/python demo_graph_memory.py
PYTHONPATH=../../../jarvis-src/src .venv/bin/python demo_diary_search.py
```

`jarvis-src/`(cloneしたリポジトリ本体)はこのディレクトリの外(`/tmp`)に置いており、
`ai-100days`リポジトリにはコミットしていない。再現する場合は手順1で改めてcloneすること。

## ファイル一覧

- `results.md` — 検証結果の詳細(セットアップ・テスト結果の内訳・手動デモの出力・ローカル検証が必要な点)
- `demo_recall_gate.py` / `demo_graph_memory.py` / `demo_diary_search.py` — モック無し・LLM無しの手動デモスクリプト
- `logs_unit_tests.txt` — ユニットテスト実行のFAILED/ERROR全行+最終集計(504行、そのまま)
