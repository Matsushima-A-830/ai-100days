# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 006
- 選んだ候補(backlog.mdのタイトルかURL): Heavy-Tailed Memory Traces in Long-Horizon Language Agents — エージェント記憶のロングテール問題とCore-Tail World Model(論文) — https://arxiv.org/abs/2610.00010 (コード: https://github.com/Hik289/world-model-self-organized-criticality)
- 補足メモ(あれば): 本家の実験(合成グラフ世界でのLLMポリシー)は外部LLM API(OpenAI互換エンドポイント)のAPIキーが前提の実装になっているため、当面の方針(有料APIキー不要)に沿って以下の縮小版で検証すること。
  - 合成グラフ世界の生成コードと、ランク依存の単一指数τでプロンプト予算を配分するCore-Tail World Model(CTWM)のメモリコントローラ本体はそのまま再利用する(どちらも純PythonでAPI不要)。
  - 「LLMに次の遷移を予測させる」部分だけを、外部APIを呼ぶ代わりにClaude Code自身(実装Routine自身)が予測器として代替する。具体的には、1ステップごとに「現在の状態・予算内に絞ったメモリ・予測すべき次の遷移」をプロンプトとしてファイルに書き出し→Claude Codeがそれを読んで予測を書き戻す、を手動ループで数十ステップ分繰り返す。
  - 規模は小さめの合成グラフ(数十ノード程度)・ステップ数30〜50程度・τを2パターン(baseline均等配分 vs CTWM推奨値)に絞ってよい。
  - 測る指標は論文と同じ「プロンプト予算(文字数で代替可)」と「テール(レアな状態)の予測誤差」。baselineメモリとCTWMメモリでBefore/After比較する。
  - results.mdには「外部LLM APIの代わりにClaude Code自身を予測器として使った縮小版の概念実証であり、論文のベンチマーク数値そのものの再現ではない」ことを明記する。
  - 日本語記事はZenn/Qiita/note共に0件(2026-10-03時点)で差別化しやすい。コードはMITライセンス。

状態: 設定済み
