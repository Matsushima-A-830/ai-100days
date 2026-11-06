# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 040
- 選んだ候補(backlog.mdのタイトルかURL): NVIDIA/auto-ontology — https://github.com/NVIDIA/auto-ontology
- 補足メモ(あれば):
  - 出典: https://github.com/NVIDIA/auto-ontology (Apache-2.0。2026-10-31頃公開、2026-11-04/11-06とGitHub Trending Pythonで連日言及、累計8.9k star超)。backlog.mdには2026-11-04付と2026-11-06付で同一リポジトリのエントリが重複して載っているので、両方を本Dayの候補として参照してよい。
  - 概要: データベースのメタデータ(テーブル・カラム等)からビジネス用語・テーブル関係・レビュー済みSQL属性を含む「セマンティックオントロジー層」を自動構築し、AIエージェントが自然言語の質問を根拠(provenance)付きのSQLに翻訳できるようにするNVIDIA製OSSフレームワーク。Web UI・MCPサーバー(読み取り専用ツール)・CLI・REST APIを備え、PostgreSQL/Snowflake/DuckDB等のSQLエンジンに対応する(Next.jsフロントエンド+FastAPIバックエンド+PostgreSQL/pgvector、Docker Compose/Helmでデプロイ)。NVIDIAは社内検証で「オントロジー作成時間を90%削減」と主張(ベンダー自身の報告で第三者未検証)。
  - APIキーについての方針: 既定の推論はbuild.nvidia.comの**無料枠**APIキー(`nvapi-...`、`DEFAULT_MODELS_API_KEY`)を使ったホスト型NIM推論が前提であり、2026-11-04付backlogエントリの調査でも「追加の有料APIキーは不要」と確認済み。CLAUDE.mdの「有料APIキーが必須の候補は選ばない」方針に抵触しないよう、**有料プランへの登録や課金が発生する設定は行わず、build.nvidia.comの無料枠signupで取得できるnvapi-キーの範囲内でのみ検証すること**。途中で有料枠への誘導やクレジットカード登録が必須になった場合は、それ以上進めずCLAUDE.mdのRoutine環境エスカレーション手順に従って人間に判断を委ねる。
  - 検証スコープ・手順:
    1. まずこのRoutine実行環境でDocker/Docker Composeが使えるか確認する。使えない場合はCLAUDE.mdの「書かない(Routine環境の制約)」に該当するため、記事等には書かずPRの説明文冒頭に「ローカル検証が必要」と明記し、再現手順(リポジトリのREADMEに沿ったセットアップコマンド)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。
    2. Dockerが使える場合は、6時間以内に収めるため構成をDuckDB(サーバー不要・軽量)1エンジンに絞り、PostgreSQL/Snowflake等の重い構成は試さない。
    3. build.nvidia.comで無料枠のnvapi-キーを取得し(課金設定はしない)、`DEFAULT_MODELS_API_KEY`として設定した上でオントロジー生成〜MCPサーバー経由の自然言語→SQL変換までの一連の流れを動かす。
    4. 自分で用意した簡単なサンプルDB(DuckDB、数テーブル程度)に対し、オントロジーを使わない素朴なtext-to-SQL(LLMに直接スキーマを渡すだけ)と、auto-ontology経由の結果を同じ質問で比較し、誤ったテーブル/カラム参照の有無をBefore/Afterとして記録する。
    5. 実行コマンド・出力・エラー・所要時間はすべてそのままresults.mdに記録する。失敗した場合も失敗として正直に書く。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-04/11-06時点、backlog.md参照)。
  - 記事化の切り口: 「AIエージェントが誤ったテーブル/カラムを参照してSQLを生成してしまう問題」を、オントロジー無し/有りのBefore/Afterで具体的に見せる。NVIDIA公式発のOSSというニュース価値も添える。Docker環境構築がRoutine環境で完了しなかった場合は、その制約には触れずローカル検証の結果が出てから反映する。

状態: 設定済み
