# Day 017 — K-Dense-AI/scientific-agent-skills 検証結果

**結論: `statistical-analysis`スキルは、スキル無しの状態でもClaude Code自身がすでに正しい結論(Mann-Whitney U検定)に到達できた一方、スキル有りでは実際にスキル同梱の`assumption_checks.py`とpingouinを実行し、Shapiro-Wilk・Levene・効果量・信頼区間・感度分析まで含む定量的な裏付けを伴う報告に変わった。「結論が変わるか」ではなく「結論の裏付けの質が変わるか」という形でBefore/After差が出た。**

出典: https://github.com/K-Dense-AI/scientific-agent-skills (MIT)

## 0. 検証スコープとその理由

CLAUDE.mdの「当面は有料APIキーが必須の候補を選ばない」方針に従い、外部APIキー(Exa・Benchling・NCBI・Materials Project等)が不要なスキルに絞って検証した。GPUも不要な範囲に限定した。

- 選んだスキル: **`statistical-analysis`**(MIT、Pingouin/SciPy/statsmodels/PyMCベース、ネットワークはインストール時のみ)、**`literature-review`**(MIT、PubMed/arXiv等の公開APIを使用、`OPENROUTER_API_KEY`は図表生成機能のみで必須ではないため未使用)
- 選定理由: today.mdの候補案(統計解析・文献レビュー手法)のうち、追加APIキーなしで実際にコードを実行できる(＝「疑似研究タスクを解かせる」というBefore/After比較が作りやすい)2つを選んだ。

## 1. リポジトリ全体のライセンスとスキル数

```
$ cat LICENSE.md | head -3
MIT License
Copyright (c) 2025 K-Dense Inc.
```

リポジトリ全体はMIT。個々のスキルの`SKILL.md`フロントマターにも`license: MIT license`または`license: MIT`の記載があることを`statistical-analysis`・`literature-review`で確認した。

スキル数は`skills/`配下のディレクトリ数で実際に数えたところ**177件**だった。today.md作成時点(2026-10-14のbacklog.md記載)では「163種」としていたが、READMEも複数箇所で「177 skills」と記載しており(1箇所のみ「181 skills」という食い違いあり)、実際に数えた177件が現状の正確な数と判断した。1日の間にもリポジトリが成長し続けている(Day 012のvideo-shotcraftで見た現象と同様)。

## 2. `npx skills add`導入時に踏んだ環境依存の失敗(検証に直接関係する失敗として記録)

CLAUDE.mdの「Claude Code自身の`auto mode classifier`」により、`npx skills add`の実行はエージェントが自律的に判断して行うことは一旦ブロックされた(Day 011のdiagram-designと同じ仕組み)。人間に「このコマンドを実行してよいか」を明示的に確認し、許可を得てから実行した。

実行時、もう1つ別の問題にぶつかった。このリポジトリは`\\wsl.localhost\Ubuntu\...`というWSLのUNCパス上にある。この状態で(WindowsネイティブのNode.js経由で)`npx skills@latest add ...`を実行すると、`skills`CLIがClaude Code向けの登録ステップで失敗した。

```
✗ literature-review → Claude Code: EPERM: operation not permitted, mkdir 'C:\Windows\.claude'
✗ statistical-analysis → Claude Code: EPERM: operation not permitted, mkdir 'C:\Windows\.claude'
```

`process.cwd()`自体は正しくUNCパスを返していたが、`skills`CLI内部のどこかで(おそらくWindows版Node.jsからcmd.exeを経由する処理が)UNCパスを扱えず、「UNCパスはサポートされていません。Windowsディレクトリを使用します」という既知のCMD.EXEの挙動でカレントディレクトリが`C:\Windows`にフォールバックし、そこに書き込もうとして権限エラーになっていた。

切り分けのため、`%TEMP%`配下の純粋なWindowsローカルパス(UNCでない場所)で同じコマンドを実行したところ、問題なく成功した。

```
✓ literature-review (copied) → ~\AppData\Local\Temp\day017-skills-test\.claude\skills\literature-review
✓ statistical-analysis (copied) → ~\AppData\Local\Temp\day017-skills-test\.claude\skills\statistical-analysis
```

**→ WSLのUNCパス上にあるプロジェクトで、Windows版Node.js経由の`npx skills add`(Claude Code向けインストール)を実行すると失敗する。** ローカルWindowsパスでは成功することを確認済みなので、WSL環境でこのツールを使う場合は、プロジェクトをWSL側のネイティブパス(`/home/...`)に置くか、Linux版Node.jsを使う(今回の環境にはインストールされていなかった)ことで回避できる可能性が高い。インストールされたスキル本体のファイル(`SKILL.md`等)自体は正常だったため、Windows側の一時ディレクトリからコピーして検証を継続した。

## 3. statistical-analysisスキル: Before/After比較

### 3-1. タスク設計

架空の小規模パイロット実験を想定し、2群を比較する統計検定の選択と理由説明をClaude Codeに求めた。

```
Group A (treatment, n=6): 12, 15, 14, 13, 55, 14
Group B (control, n=9): 10, 11, 9, 12, 10, 11, 9, 10, 12
```

意図的に、Group Aに明らかな外れ値(55)を1つ混ぜ、「素朴にt検定を選ぶと外れ値に振り回される」状況を作った。

- **Before(スキル無し)**: `claude -p`で該当の質問のみ投げ、ツール使用を禁止(`--allowedTools ''`)してテキスト推論のみで答えさせた。
- **After(スキル有り)**: 同じ質問に加え、`statistical-analysis`スキルの`SKILL.md`を読んで指示されたワークフローに従い、同梱の`scripts/assumption_checks.py`と`pingouin`を実際に実行するよう指示した(`--allowedTools 'Read Bash Glob Write'`)。

### 3-2. Before: スキル無しでの回答(全文)

> **Use a non-parametric test — Mann-Whitney U (Wilcoxon rank-sum) — not a standard two-sample t-test.**
>
> 1. Outlier/non-normality problem: Group A has one value (55) that's wildly inconsistent...
> 2. Unequal variances: ...heteroscedasticity, combined with unequal and very small sample sizes...
> 3. Small sample sizes: ...can't rely on the Central Limit Theorem...
> 4. Why Mann-Whitney U fits: ...robust to the outlier...
> 5. Caveat: it's also worth asking *why* that 55 occurred...
>
> **Bottom line**: Mann-Whitney U test.

スキル無しの時点で、すでに正しい結論(Mann-Whitney U)と、外れ値・不等分散・小標本・感度分析の必要性という妥当な理由づけに到達していた。具体的な検定統計量やp値などの数値は一切示されず、定性的な推論のみだった。

### 3-3. After: statistical-analysisスキル使用時の回答

スキル指示通り、Claude自身が`analysis.py`を作成し、`.venv-statistics/bin/python`で実際に実行した(1回目はWrite権限が無く許可待ちでブロックされたため、Write権限を追加して再実行した)。実行した内容と実際の出力は次の通り。

```python
import sys
sys.path.insert(0, "installed-skills/statistical-analysis/scripts")
import numpy as np, pandas as pd, pingouin as pg
from assumption_checks import comprehensive_assumption_check, detect_outliers
# group_a = [12, 15, 14, 13, 55, 14] / group_b = [10, 11, 9, 12, 10, 11, 9, 10, 12]
# ...(descriptives → outlier detection → assumption check → Welch t-test →
#     Mann-Whitney U → 外れ値除外時の感度分析、をこの順に実行)
```

実際の出力(抜粋):

```
=== Descriptives ===
Group A: n=6, mean=20.50, sd=16.93, median=14.00, min=12, max=55
Group B: n=9, mean=10.44, sd=1.13, median=10.00, min=9, max=12

=== Outlier detection (Group A) ===
{'n_outliers': 1, 'pct_outliers': 16.7, 'outlier_values': [55.0], ...}

--- normality_per_group ---
  Group  N   W       p-value  Normal
  A      6   0.555   0.000127  No
  B      9   0.899   0.248496  Yes

--- homogeneity (Levene) ---
statistic=1.510, p_value=0.241, variance_ratio=224.37
interpretation: Equal variances not rejected (F=1.510, p=0.241);
  non-rejection is not evidence of equality.

=== Welch's t-test (prespecified) ===
T=1.453, dof=5.03, p=0.206, cohen_d=0.954, power=0.389, BF10=0.861

=== Mann-Whitney U ===
U=53.0, p=0.0024, rank-biserial=0.963, CLES=0.981

=== Sensitivity: outlier (55) removed from Group A ===
T=4.977, dof=8.32, p<0.001, cohen_d=2.784
```

Claudeの最終的な結論:

> Use the **Mann-Whitney U test** (or Welch's t-test only after resolving the outlier), not a plain Welch t-test on the data as-is. [...] The diagnostics here point in a clear, actionable direction: first investigate whether 55 is a genuine observation or a data-entry/measurement error [...] Report the Welch t-test sensitivity analysis both with and without the outlier so readers see how much that one point drives the parametric result. With n=6, do not treat the non-significant Welch result as "no effect" — it's underpowered and outlier-distorted, not evidence of equivalence.

### 3-4. Before/After比較のまとめ

| | Before(スキル無し) | After(statistical-analysisスキル使用) |
|---|---|---|
| 最終的な推奨検定 | Mann-Whitney U | Mann-Whitney U(同じ) |
| 外れ値の指摘 | あり(定性的) | あり(IQR法で定量的に検出、16.7%) |
| 正規性・等分散の検証 | 定性的な推測のみ | Shapiro-Wilk(W=0.555, p<.001)・Levene(F=1.510, p=.241)を実際に実行 |
| 検定統計量・効果量・信頼区間 | 無し | Welch t(5.03)=1.453, p=.206, d=0.954 / MWU U=53, p=.0024 を実際に算出 |
| 感度分析(外れ値除外時) | 「報告すべき」という提案のみ | 実際に実行し t(8.32)=4.977, p<.001, d=2.784 まで提示 |

**この検証で分かったこと: スキルが無くても、Claude自身がすでに統計的に妥当な「結論」に到達できることがあった(今回の0.6B級ではなくClaude本体のモデルなので、知識ベースの統計的推論力自体が高い)。スキルが追加したのは「結論そのもの」ではなく、再現可能で査読者に提示できる「定量的な裏付け」(実際のp値・効果量・信頼区間・感度分析)だった。** 派手な正解/不正解の差ではなく、レポートの査読耐性が変わる、という地味だが実務的には重要な差だった。

## 4. literature-reviewスキル: 検証

### 4-1. タスク設計

`statistical-analysis`の検証で出てきた「Mann-Whitney U検定は外れ値・小標本下でどう挙動するか」というテーマについて、`literature-review`スキルの手順(検索式を記録する、複数データベースを使う、捏造しない)に従って簡易文献調査(systematic reviewではなく軽量版)を実際に行わせた。PubMed E-utilities・arXiv APIという、APIキー不要の公開APIのみを使うよう指示した(`OPENROUTER_API_KEY`が要る図表生成機能は使っていない)。

重要な発見: このスキルの`scripts/search_databases.py`は、**実際にデータベースへ問い合わせるスクリプトではない。** `--help`を見ると明記されている通り、既に取得済みの正規化された検索結果ファイルをローカルで処理(重複排除・ランキング・フォーマット変換)するだけのツールだった。実際の検索自体は、Claude Code本体がSKILL.mdの指示に従って`WebFetch`で各データベースのAPIを直接叩く、という設計になっている。

### 4-2. 実行結果

```
検索元: arXiv API (export.arxiv.org/api/query) / PubMed E-utilities
検索式(実行順、記録済み):
  1. arXiv: abs:"Mann-Whitney" AND abs:outlier → 0件
  2. arXiv: abs:"rank-sum test" AND abs:robust → 応用論文中心
  3. arXiv: cat:stat.ME AND abs:"Mann-Whitney" AND abs:robust → 8件ヒット(本命)
  4. arXiv: cat:stat.ME AND abs:"rank sum" AND abs:contamination → 0件
  5. PubMed: Mann-Whitney AND outlier → 15件(臨床応用論文のみ、方法論無し)
  6. PubMed: "rank sum test" AND "small sample" AND outlier → 1件(arXivと重複)
```

選定された5論文のうち2件(arXiv:2509.19126, arXiv:2009.02362)を、本検証とは別に`WebFetch`で直接開いて実在確認と内容の裏取りを行った。

- arXiv:2509.19126「Enhanced Lepage-type test statistics for location-scale shifts with right-skewed data」(Hussain & Tsagris)— 実在確認OK。Fligner-Policello検定(Mann-Whitney型)にロバストな分散推定量を組み込み、右に歪んだデータでの検出力を改善、という引用内容も一致。
- arXiv:2009.02362「Bootstrap p-values reduce type 1 error of the robust rank-order test of difference in medians」(Sinha)— 実在確認OK。小標本(n≤20)でのブートストラップ補正、という引用内容も一致。

全文は`experiments/day-017/literature-search-output.md`。

### 4-3. 分かったこと

- 「outlier」という語を直接含む論文はPubMed/arXivともほとんど無く、実際にヒットしたのは「ロバスト性」「重い裾(heavy-tailed)」「打ち切り(censoring)」といった隣接概念を扱う論文だった、とスキル自身がレポート中で正直に限界を明記していた。検索語を額面通り1回打って終わりではなく、ヒットしない場合に概念を言い換えて再検索する(今回は4パターン試行)という振る舞いが見られた。
- 選ばれた論文は実際にWebFetchで検証した範囲では捏造ではなく、内容の要約も正確だった。
- `search_databases.py`が「検索エンジンではなく後処理ツール」だったことは、READMEやSKILL.mdの概要だけを読んで想像していたものと違っており、実際に手を動かして初めて分かった構造だった。

## 5. 全体のまとめ

- ライセンス: リポジトリ全体MIT、検証した2スキルの`SKILL.md`もMIT表記。問題なし。
- スキル数: 実際に数えて177件(today.md記載の163件から増加。README記載とも概ね一致)。
- `statistical-analysis`: スキル無しでも結論(検定の選択)自体は正しかったが、スキル有りでは実際にコードを実行し、定量的な検定統計量・効果量・信頼区間・感度分析という、査読に耐える裏付けが付いた。
- `literature-review`: 検索自体はClaude本体がAPIを直接叩く設計で、同梱スクリプトは後処理用。実際に複数の検索式を試行錯誤し、限界を正直に報告する挙動が確認できた。引用の実在性もサンプルチェックで確認した。
- 環境起因の失敗: WSLのUNCパス上で`npx skills add`(Claude Code向け)が失敗する既知でない挙動を発見・回避した(詳細は2節)。
