# Day 011: diagram-design (cathrynlavery/diagram-design)

指示文だけでエディトリアル調の図解(HTML+インラインSVG)を生成するClaude Code向けagent skill。

- 出典: https://github.com/cathrynlavery/diagram-design
- ライセンス: MIT
- 詳しい経緯・判断根拠・チェックリストは [`results.md`](./results.md) を参照。

## 再現手順

今回の検証環境では、公式のplugin経由インストール(`/plugin marketplace add` /
`/plugin install`)とクローン済みリポジトリ内のスクリプト実行がサンドボックスポリシーで
拒否されたため、「SKILL.mdの指示を人力で忠実に適用する」という形で検証した。
同じ制約がない環境では、本来は以下の公式手順で試せるはず(今回は未検証):

```
/plugin marketplace add cathrynlavery/diagram-design
/plugin install diagram-design@diagram-design
```

今回実際に行った手順:

1. リポジトリを読み取り専用でクローンし、`skills/diagram-design/SKILL.md` と
   `references/type-swimlane.md`、同梱サンプル `assets/example-swimlane.html` を読む。
2. `assets/example-swimlane.html` の検証済みジオメトリ(座標・矢印ルーティング)をそのまま
   流用しつつ、テキスト内容だけを本リポジトリ(ai-100days)自身の1日の運用フロー
   (CLAUDE.mdに書かれている朝Routine→通勤中(人間)→昼Routine→夜(人間))に差し替えて
   `after-diagram-design.html` を作成。
3. 比較用に同じ内容を実際のMermaid.js(v11.4.1)でレンダリングした `before-mermaid.html` を作成。
4. 両方をPlaywright + プリインストール済みChromium(`/opt/pw-browsers/chromium`)で開き、
   フルページスクリーンショット(`after-diagram-design.png` / `before-mermaid.png`)を撮って
   崩れがないか・コンソールエラーが出ていないかを確認。

```bash
# スクリーンショット撮影に使ったNode/Playwrightスクリプト(要旨)
node -e '
import("playwright").then(async ({chromium}) => {
  const browser = await chromium.launch({executablePath: "/opt/pw-browsers/chromium"});
  const page = await browser.newPage({viewport: {width: 1100, height: 700}});
  await page.goto("file://" + process.argv[1]);
  await page.waitForTimeout(1200);
  await page.screenshot({path: process.argv[2], fullPage: true});
  await browser.close();
});
' experiments/day-011/after-diagram-design.html experiments/day-011/after-diagram-design.png
```

(`before-mermaid.html` はCDN参照のままコミットしているため、ネットワーク制限がある環境では
単体では描画されない場合がある。検証時はnpm経由で取得したmermaid.min.jsをローカル参照に
差し替えて描画した。詳細は results.md の実行ログを参照。)

## 人間が確認すべき点

- `after-diagram-design.html` / `before-mermaid.html` を実際にブラウザで開いて、
  見た目の差を自分の目でも確認してほしい(screenshot済みPNGも同梱)。
- 公式のplugin経由インストールはこの実行環境のサンドボックスで拒否されたため未確認。
  手元のClaude Codeで `/plugin marketplace add cathrynlavery/diagram-design` →
  `/plugin install diagram-design@diagram-design` を試せるなら、本検証との差分(特に
  スタイルガイドのオンボーディング対話や`self_check.py`の自動チェック結果)を見てもらえると
  記事の裏取りになる。
