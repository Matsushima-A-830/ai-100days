# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 016
- 選んだ候補(backlog.mdのタイトルかURL): diagram-design — 指示文だけでエディトリアル調の図解を自動生成するClaude Code向けagent skill — https://github.com/cathrynlavery/diagram-design
- 補足メモ(あれば):
  - 自然言語の指示だけで自己完結HTML+インラインSVGのエディトリアル調図解(アーキテクチャ図・シーケンス図・ER図・タイムライン・Sankey図・Wardley map等40種類超)を生成するAIコーディングエージェント向けagent skill(MIT)。Mermaid風の「コードから図を起こす」方式ではなく、既存の関係性に統一されたデザイン規則(1色のアクセント・1pxの罫線・4pxグリッド等)を当てはめる「後処理型デザインシステム」という位置づけ。対象Webサイトの配色・フォントを読み取ってブランドに合わせるオンボーディング機能や、draw.io/Mermaid/Excalidrawからの読み込みにも対応。
  - 導入は `npx skills add cathrynlavery/diagram-design` または Claude Codeなら `/plugin marketplace add cathrynlavery/diagram-design` → `/plugin install diagram-design@diagram-design`。
  - **検証の軸は「本リポジトリ自身の構成図をこのスキルで自動生成し、見た目・精度を評価する」こと。** 具体的には以下を`results.md`に残す:
    - 本リポジトリのCLAUDE.mdに書かれている全体フロー(朝のリサーチRoutine→人間のtoday.md反映→昼の実装Routine→夜の人間確認・公開、という4段階の流れ)を、このスキルに説明させて図解(フローチャートまたはシーケンス図)を生成させる。実際に使った指示文とスキルが選んだ図の種類・生成までのやり取りをログとして残す。
    - `experiments/day-NNN/` が増えていく構成(ディレクトリ構造)も別の図(アーキテクチャ図など)として生成させ、2種類の図を作る。
    - 生成されたHTMLファイルをブラウザで開いて崩れていないか確認し、スクリーンショットを撮る(Routine実行環境にブラウザが無い場合は、HTML/SVGとして構文的に破綻していないかを目視で確認し、その旨をCLAUDE.mdの「Routine環境の制約」に従って正直に記録する)。
    - ライセンス表記(MIT、LICENSEファイルの実在)を確認する。
    - 40種類超(READMEの表記と実際のギャラリーの数に食い違いがあるとの報告もあるため、実際に確認した数を書く)の図の種類のうち、今回使ったものがどの種類かを明記する。
  - backlog.mdには本リポジトリに関する候補メモが2件ある(2026-10-08付と2026-10-13付、どちらも同じリポジトリ)。両方の内容を踏まえてよい。
  - 日本語記事は確認した範囲でZenn/Qiita/note共に0件(2026-10-13時点、backlog.md参照)。海外の解説コラム記事はあるが日本語の一次検証記事ではない。
  - GPU不要、追加の有料APIキー不要。PNG書き出しのみPlaywright/Chromiumが必要だが、SVG/HTMLでの確認だけなら不要。

状態: 設定済み
