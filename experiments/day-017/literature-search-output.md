# 文献検索メモ: Mann-Whitney U検定(Wilcoxon順位和検定)の外れ値・小標本下での挙動

## 検索方法(再現性のため記録)

- 実施日: 2026-10-15
- 検索元: arXiv API (`http://export.arxiv.org/api/query`) / PubMed E-utilities (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`)
- 検索式と実行順:
  1. arXiv: `search_query=abs:"Mann-Whitney" AND abs:outlier` (sortBy=submittedDate) → 0件
  2. arXiv: `search_query=abs:"rank-sum test" AND abs:robust` (sortBy=submittedDate) → 応用論文中心、方法論論文少数
  3. arXiv: `search_query=cat:stat.ME AND abs:"Mann-Whitney" AND abs:robust` (sortBy=submittedDate) → **本命、8件ヒット**
  4. arXiv: `search_query=cat:stat.ME AND abs:"rank sum" AND abs:contamination` → 0件
  5. PubMed: `term=Mann-Whitney AND outlier` (sort=date) → 15件、いずれも臨床応用論文で検定の挙動自体を扱う論文なし
  6. PubMed: `term="rank sum test" AND "small sample" AND outlier` → 1件(下記ULVと重複、arXiv由来)
- 注: PubMedは統計手法論文(とくにarXiv専業の統計学分野)のインデックスが薄く、本トピックでは arXiv (stat.ME) の方が有効だった。

## 選定した論文(関連度の高い順)

### 1. Enhanced Lepage-Type Test Statistics for Location-Scale Shifts
- 著者: Abid Hussain, Michail Tsagris
- 年: 2025 (2025-09-23)
- 出典: arXiv:2509.19126
- URL: https://arxiv.org/abs/2509.19126
- 関連メモ: Fligner-Policello検定(Mann-Whitney型の順位和検定の頑健版)にロバストな分散推定量を組み込み、右に歪んだ分布・外れ値を含むデータでの検出力とType I誤差制御を評価している。外れ値耐性のある順位和統計量の設計という点で直接関連。

### 2. Adaptive Rank-Based Tests for High Dimensional Mean Problems
- 著者: Yu Zhang, Long Feng
- 年: 2023 (2023-12-30)
- 出典: arXiv:2401.00255
- URL: https://arxiv.org/abs/2401.00255
- 関連メモ: Wilcoxon-Mann-Whitney検定を高次元平均比較に拡張し、重い裾を持つ分布(ヘビーテール=外れ値が生じやすい分布)に対する頑健性・検出力の優位性を示している。

### 3. Bootstrap p-Values for Robust Rank-Order Test
- 著者: Nirvik Sinha
- 年: 2020 (2020-09-04)
- 出典: arXiv:2009.02362
- URL: https://arxiv.org/abs/2009.02362
- 関連メモ: Fligner-Policelloロバスト順位検定について、標本サイズが小さい(≤20)場合に正規近似が不正確になる問題をモンテカルロ・ブートストラップで補正する提案。まさに「小標本での正確な挙動」を扱っている。

### 4. A New Composite Mann-Whitney Test for Survival Comparisons
- 著者: Abid Hussain, Touqeer Ahmad
- 年: 2025 (2025-10-06, v2)
- 出典: arXiv:2510.05353
- URL: https://arxiv.org/abs/2510.05353
- 関連メモ: 2つの独立したMann-Whitney統計量を打ち切りの有無で分解・合成する手法で、高い打ち切り率(≒極端値・異質なデータ)下でも頑健性を保つことを報告。外れ値そのものではなく打ち切りだが、MWU統計量の非正則データへの頑健性という共通テーマで参考になる。

### 5. A Doubly Robust Estimator for the Mann Whitney Wilcoxon Rank Sum Test When Applied for Causal Inference in Observational Studies
- 著者: Ruohui Chen, Tuo Lin, Lin Liu, Jinyuan Liu, Ruifeng Chen, Jingjing Zou, Chenyu Liu, Loki Natarajan, Tang Wang, Xinlian Zhang, Xin Tu
- 年: 2024 (2024-03-11)
- 出典: arXiv:2403.06783
- URL: https://arxiv.org/abs/2403.06783
- 関連メモ: 観察研究におけるMWU検定の交絡バイアスに対する「二重に頑健な」推定量を提案。外れ値そのものの頑健性ではなく交絡への頑健性が主眼だが、「robust」を冠したMWU拡張として参考候補に含めた。

## 評価・限界

- これは系統的レビューではなく簡易文献調査(lightweight search)。網羅性は保証しない。
- 「outlier」という語を明示的に主題にした論文はPubMed/arXivともほぼ見つからず、実際にヒットしたのは「頑健(robust)」「重い裾(heavy-tailed)」「打ち切り(censoring)」といった隣接概念を扱う論文だった。外れ値の影響という観点では#1,#2,#3が特に直接的。
- bioRxiv・Semantic Scholarは今回未照会(arXiv/PubMedのみで打ち切り)。より網羅的な調査が必要な場合は追加照会を推奨。
