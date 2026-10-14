# Day 016: diagram-design (cathrynlavery/diagram-design)

## 検証対象

https://github.com/cathrynlavery/diagram-design — 指示文だけでエディトリアル調の図解を生成するClaude Code向けagent skill(MIT)。

## 再現手順

1. 公式のplugin marketplace経由のインストールを試す(このクラウド実行環境では拒否される想定、`results.md`参照):
   ```
   claude --print "/plugin marketplace add cathrynlavery/diagram-design"
   ```
2. 拒否された場合、リポジトリを読み取り専用でcloneし、スキルの指示書を直接読む:
   ```
   git clone --depth 1 https://github.com/cathrynlavery/diagram-design.git
   ```
   読んだファイル: `skills/diagram-design/SKILL.md`, `references/style-guide.md`,
   `references/type-flowchart.md`, `references/type-architecture.md`,
   `assets/example-flowchart.html`, `assets/example-architecture.html`
3. 上記の指示書の設計ルール(配色トークン・タイポグラフィ・直交コネクタ・複雑さ予算・taste gate)を
   手で適用し、以下の2ファイルを作成:
   - `diagram-flow.html` — CLAUDE.mdの4段階フローのフローチャート
   - `diagram-architecture.html` — `experiments/day-NNN/`が増えていく構成のアーキテクチャ図
4. ブラウザで開いて崩れがないか確認し、スクリーンショットを撮る:
   ```
   node shot.mjs diagram-flow.html diagram-flow.png
   node shot.mjs diagram-architecture.html diagram-architecture.png
   ```
   (`shot.mjs`はPlaywright経由でこの環境にプリインストールされたChromiumを起動し、
   consoleエラー・pageerrorの有無を出力する簡易スクリプト。本リポジトリにはコミットしていない。)

## 生成物

- `diagram-flow.html` / `diagram-flow.png` — フローチャート
- `diagram-architecture.html` / `diagram-architecture.png` — アーキテクチャ図
- `results.md` — 検証ログ・手動チェックリスト確認・ライセンス確認・図の種類数の確認
