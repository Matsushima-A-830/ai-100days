# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 029
- 選んだ候補(backlog.mdのタイトルかURL): Panniantong/Agent-Reach — https://github.com/Panniantong/Agent-Reach
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-26分のネタ候補PR〈#99、backlog.md追記〉内の候補の1つ)。
  - 出典: https://github.com/Panniantong/Agent-Reach (本日GitHub Trending Pythonで+723star/日)
  - 概要: Twitter/Reddit/YouTube/GitHub/Bilibili/小紅書など15以上のプラットフォームを、プラットフォームごとの有料API契約無しに1つのCLIから読み取り・検索できるようにする、AIエージェント向けの「インターネットへのアクセス」ツール(MIT)。読み取り専用で投稿・コメント等の書き込みは行わない設計。
  - **重要な制約(必読、実装Routineは着手前に必ず確認すること)**: Reddit/Twitter/小紅書等の一部チャンネルはブラウザのログインセッションの再利用を前提としており、Routineのクラウド実行環境ではログイン済みブラウザが無いため動作しない可能性が高い。これはCLAUDE.mdの「Routine環境の制約」に該当するため、記事・X投稿案・note原稿では触れず、ログイン不要で動くチャンネル(GitHub・Bilibili等、`agent-reach doctor`で確認できる範囲)に限定して検証すること。ログイン前提チャンネルが導入自体でブロックされた場合は、CLAUDE.mdの手順に従い「ローカル検証が必要」である旨をPR本文冒頭に明記し再現コマンドを添えてエスカレーションする(今回はキー不要チャンネルのみで6時間以内の検証が成立する見込みのため、まずはそちらを優先する)。
  - 検証スコープの指示(この優先順位で進める):
    1. まず`agent-reach doctor`等でキー/ログイン不要なチャンネル(GitHub・Bilibili等)を確認する。
    2. 通常のWeb検索/curl等でそのまま読めないページ(ログイン必須ではないが構造化されていない、動画の書き起こしが必要、等)を1〜2件選び、Agent-Reach経由で読み取れるかをBefore(Agent-Reach無し)/After(Agent-Reach有り)で比較する。
    3. 音声書き起こし系チャンネル(YouTube等)はGroq/OpenAIキーが必要なため、今回は追加キー無しで動くテキスト系チャンネルに絞る。GPUは不要。
    4. ログイン前提チャンネルについては、クラウド環境での制約を`results.md`に「Routine環境の制約により未検証」として1〜2行だけ残し、記事本体では扱わない。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-26時点、backlog.md参照。aipicks.jp等の紹介記事はあるが実際に検証した日本語の一次記事は未検出)。

状態: 設定済み
