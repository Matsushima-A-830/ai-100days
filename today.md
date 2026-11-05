# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 039
- 選んだ候補(backlog.mdのタイトルかURL): vercel-labs/agent-browser & agent-desktop — https://github.com/vercel-labs/agent-browser / https://github.com/vercel-labs/agent-desktop
- 補足メモ(あれば):
  - 出典: https://github.com/vercel-labs/agent-browser (Apache-2.0) / https://github.com/vercel-labs/agent-desktop (Apache-2.0)。本日(2026-11-05)GitHub Trendingでagent-desktopが新着ながら2,173star/日。
  - 概要: スクリーンショットやピクセル認識ではなく、ブラウザ/OSのアクセシビリティツリーをテキスト/JSON化し、各要素に`@e1`のような参照(ref)を振ってAIエージェントに操作させるVercel Labs製のRust CLI。agent-browserはブラウザ操作用(Chrome DevTools Protocol経由、Playwright MCP比で約90%少ないトークン消費を主張)、agent-desktopはmacOS/Windows/Linuxのデスクトップ操作用(OSのアクセシビリティAPI経由)。どちらもAPIキー・GPU不要で、Claude Code自身をエージェント(ドライバー)として使える。backlog.md記載時点(2026-11-05)で日本語記事はZenn/Qiita/note全て0件を確認済み。
  - 検証スコープ・手順:
    1. agent-browserをnpm等で導入し(`npm install -g agent-browser`→`agent-browser install`でChrome for Testingを取得。失敗する場合はこの実行環境に既に入っているPlaywright用Chromium〈/opt/pw-browsers/chromium〉を使う設定を試す)、Claude Code自身から`agent-browser open`→`agent-browser snapshot`→refを指定した操作、という一連のコマンドで実際のWebページ(検索・フォーム入力など)を操作する。
    2. 同じページ操作をPlaywright(素のHTML取得や既存のPlaywright MCP)で行った場合と比べ、agentに渡すsnapshot/コンテキストの文字数・トークン数を具体的に測り、Vercel Labsの「約90%少ない」という主張に対する自分の実測値として記録する(公式ベンチマークとは別物と明記)。
    3. agent-desktopは、まず導入と`agent-desktop status`でこの実行環境(ヘッドレスのクラウドコンテナ)のプラットフォーム判定・権限状況を確認する。ディスプレイ/ウィンドウマネージャが無いためアクセシビリティAPI経由の操作が動かない場合、これはCLAUDE.mdの「書かない(Routine環境の制約)」に該当するRoutine実行環境固有の制約なので、記事・X投稿案・note原稿では触れず、PRの説明文冒頭に「ローカル検証が必要」と明記し再現手順(インストール〜`agent-desktop status`〜簡単な操作コマンド)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。
    4. agent-desktopがこの環境のGUI無しでも動く部分(`agent-desktop status`でのプラットフォーム判定など)があれば、それは通常どおり実行・記録してよい。
    5. 実行コマンド・出力・エラー・所要時間はすべてそのままresults.mdに記録する。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-05時点、backlog.md参照)。
  - 記事化の切り口: 「スクリーンショットではなくアクセシビリティツリーでAIエージェントがブラウザ/デスクトップを操作する」という新しいアプローチを、実際にClaude Code自身から動かして見せる。主役はagent-browserによるブラウザ操作のBefore/After(トークン消費量の実測比較)とし、agent-desktopのGUI操作部分がRoutine環境で検証できなかった場合はその旨を記事には書かず、ローカル検証の結果が出てから反映する。

状態: 設定済み
