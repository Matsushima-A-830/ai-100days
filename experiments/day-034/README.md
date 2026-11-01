# Day 034 — pbakaus/impeccable 再現手順

対象: https://github.com/pbakaus/impeccable (npm: `impeccable`, v4.8.0, Apache-2.0)

## 前提

- Node.js(v18以上、動作確認はv22.23.4)
- npm
- 追加のAPIキー・GPU不要

## 手順

1. 本リポジトリのルートで、既存のシェアカードHTML群に対して検出器を実行する。

   ```bash
   npx --yes impeccable@latest detect posts/cards/ tools/card-template.html
   # JSON出力したい場合:
   npx --yes impeccable@latest detect --json posts/cards/ tools/card-template.html > detect-result.json
   ```

   終了コード: 0=指摘なし(advisoryのみは可) / 1=対象をスキャンできなかった / 2=primary findingsあり。

2. Before/After比較用のファイルを作る(本リポジトリの `tools/card-template.html` 自体は編集しない)。

   ```bash
   cp tools/card-template.html experiments/day-034/card-before.html
   cp tools/card-template.html experiments/day-034/card-after.html
   # card-after.html の --ink-faint: #626d80; を --ink-faint: #76839a; に2箇所置換
   sed -i 's/--ink-faint: #626d80;/--ink-faint: #76839a;/g' experiments/day-034/card-after.html
   ```

3. 修正前後それぞれに再度 `detect` を実行し、findingsが解消されたことを確認する。

   ```bash
   npx --yes impeccable@latest detect --json experiments/day-034/card-before.html
   echo $?   # => 2 (findings 2件)
   npx --yes impeccable@latest detect --json experiments/day-034/card-after.html
   echo $?   # => 0 (findings 0件)
   ```

4. (ローカル検証待ち・ネットワーク必要) エージェント向けスキル一覧・導入コマンドを試す場合:

   ```bash
   npx --yes impeccable@latest help
   npx --yes impeccable@latest install
   ```

   Routineのクラウド実行環境ではimpeccable.styleへの通信がネットワークポリシーでブロックされ、
   `Could not fetch command list from impeccable.style. Check your network connection.` というエラーになった。
   ローカルPC(ネットワーク制限なし)で再実行して結果を確認してほしい。

## 使った色のコントラスト比計算スクリプト

`results.md` に記載したWCAGコントラスト比の計算は、Pythonで次の式をそのまま実装して確認した
(外部ライブラリ不要、`python3 -I`で実行)。

```python
def srgb_to_linear(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def luminance(r, g, b):
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def contrast(rgb1, rgb2):
    l1, l2 = luminance(*rgb1), luminance(*rgb2)
    l1, l2 = max(l1, l2), min(l1, l2)
    return (l1 + 0.05) / (l2 + 0.05)
```
