# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 048
- 選んだ候補(backlog.mdのタイトルかURL): microsoft/PyRIT — https://github.com/microsoft/PyRIT
- 補足メモ(あれば):
  - 出典: https://github.com/microsoft/PyRIT (MIT。2024年2月公開だが、2026-11-13付研究PR〈#162〉で取り上げた時点で本日GitHub Trending Pythonに再浮上していた)。本エントリはbacklog.md側では2026-11-14付の記載(「microsoft/PyRIT — Microsoft製、生成AIの脆弱性を自動で突くレッドチーミングツールキット」)。
  - 概要: Microsoft社内のAI Red Teamが実際に使っていたツールを公開した、生成AIシステムの脆弱性(ハルシネーション・バイアス・ハラスメント等の禁止コンテンツ生成)を自動で突くためのレッドチーミングフレームワーク。CLIスキャナー・ブラウザGUI(CoPyRIT)・Pythonフレームワーク(`PromptSendingOrchestrator`等)の3形態を持ち、OpenAI/Azure OpenAI/Anthropic/Hugging Face/Ollama/Groq/OpenRouter等の複数プロバイダや、HTTP/WebSocket/Playwright経由の任意エンドポイントに攻撃プロンプトを送れる。Microsoftは「人間によるレッドチームの代替ではない」と明記している。
  - 検証スコープの絞り方と選定理由: 本リポジトリの「当面は有料APIキー必須の候補を選ばない」方針に沿い、攻撃対象(target)をクラウドAPIではなくローカルOllamaの小型モデルに設定して検証する。これにより追加の有料APIキーは不要。GPUも必須ではない(小型モデルであればCPUでも動作見込み)。
  - APIキー・前提条件についての方針: `pip install pyrit`でインストール可能(Python 3.10〜3.13対応、公式ドキュメントより)。攻撃対象をローカルOllamaにする限り追加の有料APIキーは不要。MITライセンスのため再配布・改変の制約は軽い。
  - 検証スコープ・手順:
    1. ローカルにOllamaを導入し、小型モデル(例: `qwen2.5:0.5b`や`llama3.2:1b`等)を`ollama pull`する。
    2. `pip install pyrit`でPyRITを導入する(Python 3.10以上が前提)。
    3. Pythonスクリプトで、Ollama向けのターゲットクラス(PyRITのバージョンによりクラス名が異なる可能性があるため、インストール後に`python -c "import pyrit; help(pyrit)"`やパッケージ内のtargetsモジュールを確認して正確なクラス名・引数を確認すること)を使い、`PromptSendingOrchestrator`に渡してローカルOllamaモデルへ攻撃プロンプト(例: PyRIT付属のデータセットにある軽微なjailbreakテンプレートや、自作の無害な「禁止コンテンツ風だが実際は無害なテストプロンプト」)を送る。
    4. レスポンスをPyRITのスコアラー(`SelfAskRefusalScorer`等、スコアラー自体がLLM呼び出しを必要とする場合は同じローカルOllamaモデルをスコアラーにも流用する)で評価し、「拒否されたか/突破されたか」を記録する。スコアラーが別途APIキーを要求する設計になっている場合は、スコアラー呼び出しは省略し、人間目視でのレスポンス内容確認に代替する。
    5. 実行コマンド・出力・エラー・所要時間はすべてそのままresults.mdに記録する。
    6. PyRITのインストールやOllamaのモデルDLがRoutine実行環境のネットワーク制約でブロックされる場合、または公式ドキュメントサイト(microsoft.github.io/PyRIT, azure.github.io/PyRIT)がこの実行環境からDNS解決できず正確なAPI仕様を確認できない場合は、CLAUDE.mdの「書かない(Routine環境の制約)」に該当する可能性が高い。その場合は記事等には書かず、PRの説明文冒頭に「ローカル検証が必要」と明記し、再現手順(上記コマンドと、確認できなかったAPI仕様の詳細)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-14時点、backlog.md参照。検索範囲ではZenn/Qiita/noteでの紹介・検証記事は未検出。@IT〈atmarkit.itmedia.co.jp〉に2024年2月付けの日本語紹介記事が1件あるのみ)。
  - 記事化の切り口: 「自分のローカルLLM(Ollama)に定型的な攻撃プロンプトを自動生成して送り、どこまで防御できるか」というBefore/After比較を主役にする。本チャレンジで既に扱ったAgent Skillのセキュリティスキャン系(SkillSpector等)とは異なり、「モデル自体への攻撃耐性」を評価する切り口であることを明記する。クラウドAPIではなくローカルモデルを対象にした理由(有料APIキー不使用の方針)も記事に正直に書く。

状態: 設定済み
