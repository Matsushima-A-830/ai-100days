# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 011
- 選んだ候補(backlog.mdのタイトルかURL): diagram-design — 指示文だけでエディトリアル調の図解を自動生成するClaude Code向けagent skill — https://github.com/cathrynlavery/diagram-design
- 補足メモ(あれば):
  - MITライセンス。Claude Code自身にスキルとして追加するだけで動作確認できる。追加の有料APIキーは不要、GPUも不要。
  - 導入は `/plugin marketplace add cathrynlavery/diagram-design` → `/plugin install diagram-design@diagram-design`(Claude Code向け)。PNG書き出しにはPlaywright+Chromiumが必要だが、SVG/HTMLでの確認だけなら不要。
  - 検証の軸は「本リポジトリ自身の構成図やexperiments/day-NNNの処理フローを、このスキルで指示文だけから自動生成できるか」。生成されたHTML+SVGを手書き/Mermaid表現と見た目でBefore/After比較し、ブラウザで崩れていないか確認すること。
  - 本チャレンジのX投稿用シェアカード(`posts/cards/day-NNN.html`)もHTML+インラインSVG形式のため、相性や応用可能性があれば触れてよい。
  - 日本語記事は確認した範囲でZenn/Qiita/note共に0件(2026-10-08時点、backlog.md参照)。

状態: 設定済み
