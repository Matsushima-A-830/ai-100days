# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 057
- 選んだ候補(backlog.mdのタイトルかURL): Search From the Start: Search-Native Pretraining for Language Models(QueryLM) — https://arxiv.org/abs/2611.26809
- 補足メモ(あれば):
  - 出典: 論文 https://arxiv.org/abs/2611.26809 (EPFL/University of Toronto、Colin Raffel等。2026-11-23付研究PR〈#196、本稿執筆時点で未マージ〉でbacklog.mdに追記予定の候補)。公開モデル群: https://huggingface.co/collections/Kausp11/search-native-pretraining (Apache-2.0)。プロジェクトページ: https://kaustubhp11.github.io/querylm
  - 概要: 事後学習(SFT/RL)だけでなく事前学習の段階から、モデル自身に検索クエリを発行させ取得した証拠を使わせる「search-native」な学習手法を提案。360M〜3.3Bパラメータの複数サイズでQueryLMモデルと通常ベースライン(standard)を学習・公開し、同じFLOPs予算で比較した結果、1.4B相当のQueryLMが3.3Bの通常ベースラインの知識QA性能に匹敵/上回ると報告している。
  - 選定理由: モデル重みがApache-2.0で公開されており追加の有料APIキー不要。最小のquerylm-wiki-360m(361.8Mパラメータ、BF16で約0.7GB)はノートパソコンのCPUでも推論比較が可能で、6時間以内に完結しやすい。「同じ計算量なら検索ネイティブな小型モデルの方が大きい通常モデルに勝つ」という分かりやすいBefore/After軸を作れる。
  - APIキー・前提条件についての方針: 追加の有料APIキーは不要。モデル重みはHugging Faceから直接取得(Apache-2.0)。GPU不要、CPUでの推論比較を主軸にする。モデルカードに「Not a product」「research artifact」と明記されている点は記事中でも断りを入れる。
  - 検証スコープ・手順(案):
    1. `querylm-wiki-360m`(QueryLM)と同サイズの`standard-wiki-360m`(通常ベースライン)をHugging Faceから取得する。
    2. 同じ知識QA系のプロンプト(Wikipedia由来の事実質問など)を両モデルに与え、応答の正確さ・検索クエリ発行の有無を比較する。
    3. 論文が使う外部検索インデックス/ツールのフル再現は行わず、QueryLMが実際にどのようなクエリ文字列を生成するか・それをどう使っているように見えるかという定性的な観察に絞る。
    4. 可能であれば`-sft-search`サフィックス付きモデル(search-SFT版)との違いも簡単に比較する。
    5. 論文の「1.4B相当が3.3Bに匹敵/上回る」という定量結果はフル再現せず、縮小版の定性的な検証を主役にする。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-23時点、backlog.md追記候補〈PR #196〉参照。検索した範囲では論文名・QueryLMいずれも日本語記事は未検出)。
  - 記事化の切り口: 「事前学習の段階から検索を組み込んだ小型モデルは、実際にどんなクエリを発行し、同サイズの通常モデルと比べて何が変わるのか」を実際の出力例で見せる。「Not a product」と明記された研究用アーティファクトを一人で検証するという立ち位置も記事のフックにする。

状態: 設定済み
