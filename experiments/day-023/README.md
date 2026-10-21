# Day 023: Graphify でコードベースを知識グラフ化し、grep/Read との「読み込み量」を比較する

対象: https://github.com/Graphify-Labs/graphify (PyPI配布名 `graphifyy`、Apache-2.0。
過去にMITで提供していた部分はMIT条件のまま併存。詳細は[`results.md`](./results.md)参照)

詳しい実行ログ・結果・考察は [`results.md`](./results.md) を参照。ここでは再現手順のみまとめる。

## 事前準備

- Python 3.10以上(本検証はPython 3.11.17で実施)。
- 追加の有料APIキー・GPUともに不要(`--code-only`は完全ローカルのtree-sitter解析のみ)。
- `uv`(`pipx`でも可)がインストールされていること。

## 再現手順

```bash
# 1. CLIを導入
uv tool install graphifyy
graphify --version   # graphify 0.9.93 で確認

# 2. リポジトリ全体(ai-100days)を --code-only でグラフ化
cd /path/to/ai-100days
graphify extract . --code-only --out experiments/day-023/graphify-out
# ツールの仕様で実際には experiments/day-023/graphify-out/graphify-out/ 以下に
# 書き出される(本リポジトリにコミットした分はその内容を1段上に移動済み)。

# 3. クラスタリング・レポート・graph.htmlの生成(APIキー不要の --no-label)
graphify cluster-only experiments/day-023/graphify-out --no-label

# 4. 公式のトークン削減率ベンチマーク
graphify benchmark experiments/day-023/graphify-out/graph.json

# 5. 具体的な質問への回答(ノード名を直接指定する explain が安定して使えた)
graphify explain "KronosPredictor" \
  --graph experiments/day-023/graphify-out/graph.json

# 6. (挙動確認用)自然言語クエリ。日本語では機能しなかった(results.md 5節)
graphify query "KronosPredictorを呼び出している箇所はどこか" \
  --graph experiments/day-023/graphify-out/graph.json --budget 2000
```

## 比較実験の前提

grep側の比較対象として、`grep -rln "KronosPredictor" experiments/day-022/ --include="*.py"`
で見つかる5ファイルを使用。「素朴に全文読む」「grepしてから該当箇所だけ読む」の
2パターンの文字数を`wc -c`で実測し、`graphify explain`の出力文字数と比較した。
4文字≒1トークンという粗い近似で概算トークン数を出している(厳密なトークナイザは
使用していない。詳細はresults.md参照)。

## Routine環境の制約(ローカルPCで検証済み)

`experiments/day-023/graphify-out/graph.html`はCDN(unpkg.com)から
vis-network.jsを読み込む構成になっており、このRoutine実行環境のネットワーク
プロキシがunpkg.comをブロックしていたため、ブラウザでの描画を確認できなかった
(Routine環境固有の制約。CLAUDE.md参照)。

人間のローカルPC(通常のインターネット接続)で検証した結果、vis-network.jsが
HTTP 200で正常に読み込まれ、JSエラー無くノードリンク図(914 nodes / 1657 edges /
56 communities)が描画され、ノードクリック等のインタラクションも問題なく
動作することを確認した。詳細はresults.md 7節を参照。
