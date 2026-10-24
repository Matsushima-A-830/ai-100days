# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 027
- 選んだ候補(backlog.mdのタイトルかURL): IQuestLab/IQuest-Q1 — https://huggingface.co/papers/2610.30949
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-24分のネタ候補PR〈#91、backlog.md追記〉内の候補の1つ)。
  - 出典: https://huggingface.co/papers/2610.30949 (モデル: https://huggingface.co/IQuestLab/IQuest-Q1 、コード: github.com/IQuestLab/IQuest-Q1。本日〈2026-10-24〉Hugging Face Daily Papers上位掲載)
  - 概要: ソフトウェア開発・汎用タスク実行・長期推論・サイバーセキュリティ等のCLI/エージェント作業に重点を置いた疎MoE基盤モデル(総パラメータ約320B、トークンあたり有効化15B、コンテキスト524,288トークン、BF16公開)。SWE-Bench Pro 57.5、Terminal-Bench 2.1で83.2、CyberGym 84.5などのベンチマークを報告。vLLM/SGLangでのデプロイ(`--tp-size 8`等、8GPU構成前提)が想定されている。
  - **重要な制約(必読、実装Routineは着手前に必ず確認すること)**: backlog.md調査時点でHugging Faceページのライセンスは独自ライセンス「iquest-q1」の表記のみで、商用利用可否等の条文詳細は未確認。Hosted Inference ProviderやHugging Face Spaces上の無料デモは無く、自前でvLLM/SGLangサーバーを立てる必要があり、BF16重みは約640GB相当・8GPU構成が前提とされている。個人が6時間以内に手元(ローカルPC含む)で実機推論を動かすのは非現実的であり、CLAUDE.mdの「動かしていないものを動いたと書かない」原則に直結する。これはRoutine実行環境固有の制約ではなく、ツール自体の性質(モデルサイズ・公開範囲)による制約なので、CLAUDE.mdの「書く(検証に直接関係する失敗)」に該当し、記事・X投稿案・noteの本題として正直に書いてよい(ローカル検証へのエスカレーション対象ではない)。
  - 検証スコープの指示(この優先順位で進める):
    1. Hugging Face上のモデルカード・リポジトリのLICENSEファイルを実際に読み、商用利用可否・再配布条件等のライセンス条文を正確に記事に明記する。
    2. 量子化版(GGUF等)やSpaces上の軽量デモ、Inference API経由の提供が新たに出ていないか再確認する。見つかれば実際に試して結果を`results.md`に記録する。
    3. 2が無ければ、実機推論の実行は行わず「動いた」と書かない。ベンチマーク数値(SWE-Bench Pro/Terminal-Bench 2.1/CyberGym)の紹介と、ライセンス不明点・8GPU要件という「試せなかった理由」を正直に書く、ニュース解説中心のスコープに切り替える。published: falseのドラフトとして人間の判断に委ねる。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-24時点、backlog.md参照。中国語〈量子位系記事の転載〉の紹介記事はあるが日本語の一次検証記事は未検出)。

状態: 設定済み
