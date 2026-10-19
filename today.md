# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 022
- 選んだ候補(backlog.mdのタイトルかURL): shiyu-coder/Kronos — https://github.com/shiyu-coder/Kronos
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-19分のネタ候補PR〈#76、backlog.md追記、マージ待ち〉内の候補の1つ)。
  - 出典: https://github.com/shiyu-coder/Kronos (2026-10-19時点GitHub Trending Pythonで+355star/日、累計41.6k star。AAAI 2026採択)。MITライセンス。
  - 概要: 世界45取引所・120億件超のK線(OHLCV)データで事前学習した、金融ローソク足専用の基盤モデル。専用トークナイザでOHLCVを階層的な離散トークンに変換し、自己回帰Transformerを事前学習する2段構成で、ゼロショットの価格系列予測でRankICが既存の時系列基盤モデルより93%高いと報告。Kronos-mini(4.1M)・Kronos-small(24.7M)・Kronos-base(102.3M)はHugging Face Hubで重み公開、Kronos-large(499.2M)は非公開。
  - 検証範囲: Python 3.10+環境でrequirements.txtを導入し、Hugging Face Hubから`NeoQuasar/Kronos-Tokenizer-base`+`NeoQuasar/Kronos-small`(または最小構成の`Kronos-mini`)をダウンロード。`KronosPredictor`に自分で選んだ銘柄(例: BTC/USDT等、無料で取得できる公開OHLCVデータ)の直近K線データを入力して予測させ、予測チャートと実際の値動きをBefore/After的に記録する。公式デモ(shiyu-coder.github.io/Kronos-demo)との突き合わせも行う。
  - 追加の有料APIキーは不要(Hugging Face Hubから直接ダウンロードする公開モデルのみ使用)。GPUは必須ではない(`device`パラメータでCPU指定も可能と見られるが、実際にノートPC相当のCPUで実用的な速度で推論できるかはKronos-miniから着手して確認すること。GPUが使えず極端に遅い場合は検証に直接関係する失敗としてCLAUDE.mdの基準に沿って記録してよい)。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-19時点、backlog.md参照。中国語の紹介記事〈磐创AI由来、新浪財経転載〉はあるが日本語の一次検証記事は未検出)。
  - 記事化の切り口: 「金融K線専用の基盤モデルに自分で選んだ銘柄の値動きを予測させてみた」というBefore/After比較を軸に、予測チャートと実際の値動きの差分・RankIC等の定量評価を見せる。「予測は確率的サンプルであり投資判断の唯一の根拠にしてはいけない」という公式の免責を記事にも明記すること。

状態: 設定済み
