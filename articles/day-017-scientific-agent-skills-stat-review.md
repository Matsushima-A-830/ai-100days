---
title: "科学研究向けAgent Skills集を試す: 統計スキルは「結論」ではなく「裏付けの質」を変えた"
emoji: "🔬"
type: "tech"
topics: ["ai", "llm", "python", "statistics", "oss"]
published: false
---

筆者は海外のAI関連ニュースを毎日1本検証して発信するチャレンジの17日目として、[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)(MIT、旧Claude Scientific Skills)を検証した。生物学・化学・医学・物理・データ解析など幅広い研究分野をカバーするAgent Skills集で、実際に数えたところ177種のスキルが収録されていた。

結論から書く。**`statistical-analysis`スキルは、スキル無しの状態でもClaude Code自身がすでに統計的に正しい結論に到達できていた。スキルが変えたのは「結論」ではなく、実際にコードを実行して得られる検定統計量・効果量・信頼区間・感度分析という「裏付けの質」だった。** 派手な正解/不正解の差ではなく、査読に耐えるレポートになるかどうかという、地味だが実務的には重要な差が見えた検証になった。

## 検証対象と検証範囲

CLAUDE.mdの「当面は有料APIキーが必須の候補を選ばない」方針に従い、177種のうち追加APIキー不要な`statistical-analysis`(Pingouin/SciPy/statsmodels/PyMCベース)と`literature-review`(PubMed/arXiv等の公開API使用)の2スキルに絞って検証した。

導入コマンド自体(`npx skills add K-Dense-AI/scientific-agent-skills`)は、Claude Codeの`auto mode classifier`が外部コード実行として一旦ブロックする対象だったため、実行前に人間に許可を取った。さらに、このリポジトリがWSLのUNCパス(`\\wsl.localhost\...`)上にあるため、Windows版Node.js経由での`skills` CLIのインストールが`EPERM: operation not permitted, mkdir 'C:\Windows\.claude'`で失敗するという、再現性のある環境起因の問題にも遭遇した。原因はCLIの内部処理がUNCパスを扱えず、CMD.EXEの既知の挙動でカレントディレクトリが`C:\Windows`にフォールバックしたことだった。Windowsのローカルパス(非UNC)で実行すると問題なく成功したため、そちらで導入してからファイルをコピーして検証を続けた。

## 検証1: statistical-analysisスキルのBefore/After比較

### タスク設計

架空の小規模パイロット実験を想定し、外れ値を1つ混ぜた2群のデータを用意した。

```
Group A (treatment, n=6): 12, 15, 14, 13, 55, 14
Group B (control, n=9): 10, 11, 9, 12, 10, 11, 9, 10, 12
```

「この2群を比較するにはどの統計検定を使うべきか、理由とともに答えよ」という質問を、スキル無し(テキスト推論のみ)とスキル有り(`assumption_checks.py`を実際に実行)の2条件で`claude -p`に投げた。

### Before: スキル無しの回答

ツール使用を禁止した状態でも、Claude Codeは次のように答えた。

> **Use a non-parametric test — Mann-Whitney U (Wilcoxon rank-sum) — not a standard two-sample t-test.**
> 1. Outlier/non-normality problem: Group A has one value (55) that's wildly inconsistent with the rest...
> 2. Unequal variances: ...heteroscedasticity, combined with unequal and very small sample sizes...
> 5. Caveat: it's also worth asking *why* that 55 occurred...

外れ値・不等分散・小標本という妥当な根拠を挙げ、すでに正しい結論(Mann-Whitney U)に到達していた。ただし、具体的な検定統計量やp値は一切示されなかった。

### After: スキル使用時の回答

スキルの指示に従って`assumption_checks.py`とPingouinを実際に実行させた(1回目はWrite権限が無く作成しようとしたスクリプトファイルの許可待ちでブロックされ、権限を追加して再実行した)。実際の出力は次の通り。

```
=== Descriptives ===
Group A: n=6, mean=20.50, sd=16.93, median=14.00
Group B: n=9, mean=10.44, sd=1.13, median=10.00

--- normality_per_group (Shapiro-Wilk) ---
  Group A: W=0.555, p=0.000127 → Normal: No
  Group B: W=0.899, p=0.248496 → Normal: Yes

--- homogeneity (Levene) ---
statistic=1.510, p=0.241, variance_ratio=224.37
"Equal variances not rejected; non-rejection is not evidence of equality."

=== Welch's t-test ===
T=1.453, dof=5.03, p=0.206, cohen_d=0.954

=== Mann-Whitney U ===
U=53.0, p=0.0024, rank-biserial=0.963

=== Sensitivity: 外れ値(55)除外後のt検定 ===
T=4.977, dof=8.32, p<0.001, cohen_d=2.784
```

最終的な結論はBeforeと同じくMann-Whitney Uだったが、「外れ値を除いた場合はWelch検定でも明確に有意になる」という感度分析の数値まで提示された上で、「n=6でのWelch検定の非有意という結果を『効果が無い』と解釈してはいけない(検出力不足と外れ値の歪みが原因)」という、より慎重な注意書きが付いた。

### Before/Afterまとめ

| | Before | After |
|---|---|---|
| 推奨検定 | Mann-Whitney U | Mann-Whitney U(同じ) |
| 検定統計量・p値・効果量 | 無し | Welch t(5.03)=1.453, p=.206, d=.954 / MWU U=53, p=.0024 |
| 感度分析 | 「報告すべき」という提案のみ | 実際に実行(t(8.32)=4.977, p<.001, d=2.784) |

Claude自身の統計的推論力がすでに高いため、スキルの価値は「間違いを正す」ことではなく「口頭の結論を、再現可能で査読者に見せられる数値に裏打ちする」ことにあった。

## 検証2: literature-reviewスキルで分かった意外な構造

同じテーマ(Mann-Whitney検定の外れ値下での挙動)について、`literature-review`スキルの手順に従い、PubMed/arXivの公開APIのみを使った簡易文献調査も行わせた。

ここで分かったのは、スキルに同梱されている`scripts/search_databases.py`は**実際にデータベースへ問い合わせるスクリプトではない**ということだった。`--help`を見ると、既に取得済みの検索結果ファイルをローカルで重複排除・ランキングするだけの後処理ツールだと明記されている。実際の検索自体は、Claude Code本体が`SKILL.md`の指示に従って`WebFetch`でAPIを直接叩く設計になっていた。

実行させたところ、arXivで「Mann-Whitney AND outlier」が0件だったことを受けて検索語を「robust」「rank-sum」「contamination」などに言い換えながら4パターン試行し、最終的に`cat:stat.ME AND abs:"Mann-Whitney" AND abs:robust`で8件ヒットさせた。選んだ5論文のうち2件を別途`WebFetch`で直接開いて実在性を確認したところ、タイトル・著者・内容の要約いずれも一致しており、捏造は無かった。スキル自身も「outlierという語を主題にした論文はほぼ無く、実際にヒットしたのは隣接概念(頑健性・重い裾・打ち切り)だった」と限界を正直にレポートしていた。

## まとめ

今回の検証でいちばん印象的だったのは、「スキルを入れたら賢くなった」という単純な話にならなかったことだ。Claude Code自身の統計的推論力はスキル無しでも十分高く、`statistical-analysis`スキルが本当に変えたのは、口頭の結論を実際のコード実行による数値で裏付けられるかどうかだった。`literature-review`スキルも、同梱スクリプトが検索エンジンではなく後処理ツールだったという、READMEだけでは分からない構造が実際に動かして初めて見えてきた。「賢さの差」ではなく「裏付けと再現性の差」を見るという切り口は、今後似たスキル集を検証するときにも使えそうだ。

- 出典: https://github.com/K-Dense-AI/scientific-agent-skills (MIT)
- 検証したスキル: `statistical-analysis` v2.0 / `literature-review` v1.11
