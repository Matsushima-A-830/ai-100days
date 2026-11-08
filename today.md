# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 042
- 選んだ候補(backlog.mdのタイトルかURL): ranxianglei/billion-context — https://github.com/ranxianglei/billion-context
- 補足メモ(あれば):
  - 出典: https://github.com/ranxianglei/billion-context (MIT License。ただしユーザー向けプロダクトでの表示にはbillion-context〈および該当する場合はacp-kernel〉へのクレジット表記を求める追加条項あり。2026-11-08付でGitHub Trending TypeScriptで+460star/日)。本エントリはbacklog.md側では2026-11-08付研究PR(#143、本記事作成時点で未マージ)に記載されている。backlog.mdへの反映が先にマージされていなくても、本todayエントリの情報だけで検証に着手できるよう以下に詳細を再掲する。
  - 概要: 既存のコーディングエージェントとそのモデルAPIの間に立つプロキシとして会話を逐次的・可逆的に圧縮し、プロンプトキャッシュを保ったまま小さいコンテキスト窓で長時間セッションを扱えるとするツール。ハード切り捨てではなく、モデル自身が何を・いつ圧縮するか判断する設計で、`compress`/`decompress`/`search_context`/`acp_status`の4ツールを注入する。README自身の計測ではContextBenchで約58%、LongMemEval-Sで約71%のコスト削減、圧縮自体のコストはキャッシュ健全性の2%以下、健全なセッションでは95〜97%のプレフィックスキャッシュヒット率を維持すると主張している。
  - 導入方法の選択肢: (1) `npm install -g billion-context --prefix=~/.local` でグローバル導入し`bili`コマンドを使う(Node.js 20以上、組み込みSQLiteエンジンにはNode 22以上が必要)、(2) ネイティブプラグインとして`bili plugin install <client>`(pi/omp/opencode/dsh/kimi/hermes/zcode等に対応)、(3) ランチャーとして`bili claude`のように対象CLIをラップしてプロキシと同時起動、(4) 手動でプロキシだけ起動(`bili`、デフォルトポート8787)し、クライアント側のbase URLを`http://localhost:8787/bili/`に向ける。Dockerイメージも用意されているが、コンテナに認証機能が無い旨の注意書きがあるため信頼できるネットワーク内でのみ使う。
  - APIキー・前提条件についての方針: モデル呼び出し自体はプロキシを挟むだけで、本Routine環境が既に持っているClaude Code CLIの契約をそのまま使う想定のため追加の有料APIキーは不要、GPUも不要。`bili claude`で本Routine自身が使っているClaude Code CLIを直接ラップできるかを最初に試す、自己言及的な検証にする。
  - 検証スコープ・手順:
    1. 本Routine実行環境のNode.jsバージョンを確認し、`npm install -g billion-context --prefix=~/.local`(または通常のグローバルインストール)でインストールできるか確認する。
    2. `bili claude` で本Routine自身が使っているClaude Code CLIをラップしてプロキシ経由に起動できるか試す。うまくいかない場合は(3)の手動方式(`bili`でプロキシだけ起動し、`curl http://localhost:8787/__bili/health`で稼働確認後、base URLを向けた簡易スクリプトで同じモデルを呼ぶ)を試す。
    3. 起動できた場合、意図的に長い複数ターンの会話(同じ大きめのファイル・ログを読み込ませた上で質問を繰り返すなど)をプロキシ経由/直接の両方で実行し、`acp_status`や`__bili/health`から取得できるトークン数・キャッシュヒット率等の指標を比較する。README自身が主張する「5倍のトークン削減」「ContextBench約58%・LongMemEval-S約71%のコスト削減」は大規模ベンチマーク前提の数値のため、完全な再現は目指さず、自作の縮小版シナリオでの概念実証(圧縮あり/無しでのトークン数・応答の一貫性のBefore/After比較)に絞る。
    4. もし(a)ネストしたCLI起動やローカルプロキシのポート開放がこのRoutine実行環境固有の制約(ネットワーク制限・プロセス権限等)で失敗する、または(b)Node.jsバージョンが要件を満たせない場合は、CLAUDE.mdの「書かない(Routine環境の制約)」に該当するため記事等には書かず、PRの説明文冒頭に「ローカル検証が必要」と明記し、再現手順(上記npm/bili/curlコマンド)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。
    5. 実行コマンド・出力・エラー・所要時間はすべてそのままresults.mdに記録する。失敗した場合も、それがツール自体に起因する失敗なのかRoutine環境固有の制約なのかを区別した上で正直に書く。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-08時点、backlog.md参照。検索した範囲では日本語の紹介・検証記事は未検出)。
  - 記事化の切り口: 本Routine自身が使っているClaude Code CLIをそのままラップし、長い検証セッションの中でコンテキスト圧縮の効果(トークン数・応答の一貫性)をBefore/Afterで見せる自己言及的な検証。「エージェントの記憶・コンテキスト圧縮」という本チャレンジで頻出のテーマだが、既存エージェントに後付けできる実用プロキシという切り口で差別化する。

状態: 設定済み
