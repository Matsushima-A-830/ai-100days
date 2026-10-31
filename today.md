# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 033
- 選んだ候補(backlog.mdのタイトルかURL): Broken on Arrival — https://arxiv.org/abs/2609.05881 (コード: https://github.com/aditi-p31/quantcheck)
- 補足メモ(あれば):
  - 出典: https://arxiv.org/abs/2609.05881 (現行タイトル"Non-Functional Quantized LLM Artifacts in Public Model Registries and How to Catch Them"。コード・監査データセット: https://github.com/aditi-p31/quantcheck 〈v3.4、コードはMIT・データセットはCC BY 4.0〉)
  - 概要: Ollama公式ライブラリ305件+Hugging Face上の人気コミュニティ量子化GGUFアーティファクト22件、計327件にHumanEval+ベースの機能検査を実行した論文。164タスクのフル実行では、Ollama公式タグのうち7件(`qwen2.5-coder:3b-instruct`のq2_K/q3_K_S/q3_K_M/q3_K_L、`phi3.5:3.8b-mini-instruct-q2_K`、`llama3.2:1b-instruct`のq2_K/q3_K_S)が164問中0〜6問しか解けない「機能しない」状態だったと報告している。
  - **重要な訂正経緯(記事の主役にすべき点)**: この論文は初版(v1)で「サイレントに壊れたファイル」と診断していたが、v3で訂正されている。著者がQwen2.5-Coder-3B系・phi3.5系をオリジナルのチェックポイントから再ビルドしたところビット単位で一致する正規の(無calibrationの)低bit量子化だった。つまりファイル自体は壊れておらず、「無calibrationの低bit量子化によって性能が実質ゼロまで崩壊する」現象だった。importance matrix(calibration)を使った量子化に変えると同じ3Bモデルの一部タグで0→76〜113問(164問中)まで回復したという。phi3.5の欠陥主張自体は2026-09-10付でOllama側Issue(ollama/ollama#18252)上で撤回されている。llama3.2-1B系2タグは著者による再ビルド検証が未実施で原因未特定。
  - 検証スコープ・手順:
    1. ローカル(または検証環境)にOllamaをインストールし、`ollama --version`で動作確認する(論文はv0.32.6で検証。異なるバージョンでも構わないが、results.mdにバージョンを記録する)。
    2. Python 3.9+の仮想環境を用意し、`https://github.com/aditi-p31/quantcheck` をクローン。READMEに従い依存関係(EvalPlus 0.3.1等)をインストールする。
    3. 論文が「機能しない」と報告したタグのうち最低1つ(例: `qwen2.5-coder:3b-instruct-q2_K`。正確なOllamaタグ名はREADME/監査データセットで確認すること)を`ollama pull`し、同じモデルの「機能する」とされる比較対象タグ(例: 同モデルのq4_K_M等、より高精度な量子化)も1つpullする。
    4. `harness/audit.py --only <TAG> --results-dir <DIR>` で両タグに対しスモークテスト(15タスク)を実行し、`rerun-2026-10/scripts/rescore_census.py`でスコアリングする。CPU推論のみでよい(GPU不要)。時間が許せば164タスクのフル実行も検討するが、6時間に収まらない場合は15タスクのスモークテストの結果のみでよい。
    5. 「ダウンロードはできてロードもでき、トークンも生成されるのに、低bit量子化タグの方は正解率が実質ゼロに近い」という現象を実際に再現できたかを`results.md`に記録する。再現できなかった場合(Ollama側が既に該当タグを差し替えている可能性がある等)も正直にその旨を書く。
    6. 記事・X投稿案・noteでは、v1の「壊れたファイル」という診断を事実として書かないこと。「ファイルは正規品だが無calibration量子化で性能が崩壊した」という訂正後の内容と、その訂正の経緯自体を主役にする。
    7. GPU不要。追加の有料APIキー不要(ローカルOllama推論のみ)。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-30時点、backlog.md参照)。

状態: 設定済み
