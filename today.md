# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 047
- 選んだ候補(backlog.mdのタイトルかURL): lidge-jun/opencodex — https://github.com/lidge-jun/opencodex
- 補足メモ(あれば):
  - 出典: https://github.com/lidge-jun/opencodex (MIT。本日GitHub Trending TypeScriptで+55star/日)。本エントリはbacklog.md側では2026-11-13付研究PR(#159、本記事作成時点で未マージ)に記載されている。backlog.mdへの反映が先にマージされていなくても、本todayエントリの情報だけで検証に着手できるよう以下に詳細を再掲する。
  - 概要: OpenAI Codex・Claude Code・Claude Desktop・Grok Build等のコーディングエージェントと、Claude/Gemini/Grok/DeepSeek/ローカルOllama等の各モデルプロバイダーの間に立つローカルゲートウェイ(「汎用プロバイダープロキシ」)。Responses API・Chat Completions API・Anthropic Messages APIの各形式を相互変換し、エージェント側のベースURLを`http://localhost:10100/v1`に向けるだけで任意のプロバイダに接続できる。`provider/model`形式でのモデル指定や、複数プロバイダへのフェイルオーバー/重み付きラウンドロビン(「コンボ」)にも対応。
  - 検証スコープの絞り方と選定理由: ローカルOllamaにルーティングすれば追加の有料APIキー・GPU無しで検証できるため、本リポジトリの「当面は有料APIキー必須の候補を選ばない」方針に合致する候補として選んだ。一方で公式の免責事項として、Anthropic等は非公式プロキシ経由のアカウントを停止する可能性があると明記されている。そのため本検証では**実際のClaude Code/Codexの製品アカウント(サブスクリプションログイン)は使わず**、ローカルOllamaモデルへのルーティングと、Anthropic Messages API形式のリクエストをcurl等で直接叩いて変換・転送が正しく行われるかの確認に絞る。アカウントリスクを伴う「`ocx claude`で実際の製品ログインを通す」検証はスコープ外とし、その理由を記事にも明記する。
  - APIキー・前提条件についての方針: ローカルOllamaモデルのみを使う限り追加の有料APIキーは不要。GPUも必須ではない(小型モデルならCPU動作可能)。MITライセンスのため再配布・改変の制約は軽い。
  - 検証スコープ・手順:
    1. ローカルにOllamaを導入し、小型モデル(例: `qwen2.5:0.5b`や`llama3.2:1b`等、Routine実行環境のネットワーク・ディスク制約に収まるもの)を`ollama pull`する。
    2. `npm install -g --allow-scripts=bun @bitkyc08/opencodex`でopencodexを導入し、`ocx start`でプロキシ+ダッシュボード(localhost:10100)を起動する。
    3. ダッシュボードまたは設定ファイルで、プロバイダとしてローカルOllamaを登録する。
    4. Anthropic Messages API形式のリクエストをcurl等でプロキシ(`http://localhost:10100/v1`相当のエンドポイント)に送り、Ollamaの小型モデルへ正しく転送され、期待する形式のレスポンスが返ってくるかを確認する(実際のClaude Code/Codex本体は起動しない)。
    5. 可能であれば、同じモデルに対してOpenAI Chat Completions形式・Responses形式でもリクエストを送り、プロキシが複数のAPI形式を相互変換できているかを比較する。
    6. 実行コマンド・出力・エラー・所要時間はすべてそのままresults.mdに記録する。
    7. もしOllamaのインストールやモデルDLがRoutine実行環境のネットワーク制約でブロックされる場合は、CLAUDE.mdの「書かない(Routine環境の制約)」に該当するため、記事等には書かずPRの説明文冒頭に「ローカル検証が必要」と明記し再現手順(上記コマンド)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-13時点、backlog.md参照。検索範囲では本リポジトリ名でのZenn/Qiita/note記事は未検出)。
  - 記事化の切り口: 「本来は有料API契約が前提になりがちなコーディングエージェントを、ローカルOllamaモデルにルーティングして動かす」というBefore(クラウドAPI必須)/After(ローカルモデルへのプロキシ経由ルーティング)の比較構成にする。アカウントリスクを避けるため実際の製品ログインは使わず、API形式の変換・転送という本質的な機能に絞って検証したことと、その理由(Anthropic等の非公式プロキシに関する利用規約リスク)を正直に明記する。

注意:
  - backlog.mdへの反映元であるPR #159はまだマージされていない。順序としては先にPR #159をマージすることを推奨するが、today.mdの内容はPR #159の有無に関わらず実装Routineが参照できる。

状態: 設定済み
