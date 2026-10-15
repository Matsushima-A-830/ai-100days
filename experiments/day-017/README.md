# Day 017: K-Dense-AI/scientific-agent-skills

## 検証対象

https://github.com/K-Dense-AI/scientific-agent-skills — 生物学・化学・医学・物理・工学・データ解析等にまたがる177種のAgent Skills集(MIT、旧Claude Scientific Skills)。

## 再現手順

1. 事前にユーザーの明示的な許可を得た上で(`npx skills add`はauto mode classifierの対象のため)、
   APIキー不要の2スキルを導入:
   ```
   npx skills@latest add K-Dense-AI/scientific-agent-skills -s statistical-analysis -s literature-review -a claude-code -y
   ```
   WSLのUNCパス上では失敗したため(`results.md`2節参照)、Windowsローカルの一時ディレクトリで
   実行し、`installed-skills/`配下にコピーした。
2. `statistical-analysis`の検証: 外れ値を含む小規模2群データを用意し、
   `claude -p`でスキル無し/有りの2条件で同じ質問を投げてBefore/After比較した。
   - Before: `--allowedTools ''`(テキスト推論のみ) → `before-no-skill.json`
   - After: `--allowedTools 'Read Bash Glob Write'`(スキルの`assumption_checks.py`を
     実際に実行させる) → `after-with-skill.json`、生成されたスクリプトは`analysis.py`
   - 検証用Python環境はスキルの指示通り`uv`で構築: `.venv-statistics/`
     (`pingouin==0.7.0`, `scipy==1.18.1`, `statsmodels==0.15.0`, `pandas`, `matplotlib`)
3. `literature-review`の検証: 2で使った外れ値テーマについて、PubMed/arXivの公開APIのみを
   使った簡易文献調査を実際に行わせた:
   ```
   claude -p "... literature-review skillの指示に従い WebFetch でPubMed/arXivを直接検索 ..." \
     --allowedTools 'Read Bash Glob Write WebFetch' --output-format json \
     > after-literature-review.json
   ```
   出力は`literature-search-output.md`。選定論文のうち2件を別途`WebFetch`で開き、
   実在性と内容の一致を確認した。

## 生成物

- `results.md` — ライセンス確認・スキル数確認・環境起因の失敗(WSL UNCパス問題)・
  statistical-analysisのBefore/After比較・literature-reviewの検証結果
- `before-no-skill.json` / `after-with-skill.json` / `analysis.py` — statistical-analysis検証の生ログ
- `after-literature-review.json` / `literature-search-output.md` — literature-review検証の生ログと出力
- `installed-skills/` — 実際に導入された`statistical-analysis`・`literature-review`のスキル本体
  (`SKILL.md`・`scripts/`・`references/`)
- `.venv-statistics/` — 検証用Python仮想環境(リポジトリにはコミットしない)
