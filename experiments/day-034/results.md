# Day 034 — pbakaus/impeccable で自前のシェアカードHTMLを検査する

## 対象

- ツール: [pbakaus/impeccable](https://github.com/pbakaus/impeccable)(npm: `impeccable`, v4.8.0, Apache-2.0)
- 出典: https://github.com/pbakaus/impeccable
- 検査対象: 本リポジトリの `posts/cards/day-003.html` 〜 `day-033.html`(全31枚、Day 001・002分は未作成のため欠番)と `tools/card-template.html`
- 実行環境: Node.js v22.23.4 / npm 10.9.9(Routineのクラウド実行環境、ブラウザなし)

## 1. 環境準備・バージョン確認

```
$ npx --yes impeccable@latest --version
4.8.0
```

`npx`経由でのパッケージ取得・実行は問題なく完了した(Routine環境のネットワーク制限には引っかからなかった)。

## 2. 既存シェアカード全体への `detect` 実行(Before)

```
$ npx --yes impeccable@latest detect posts/cards/ tools/card-template.html
...
94 anti-patterns found.
46 advisory notes. Suppress with --no-advisory.
$ echo $?
2
```

`--json` でも同じ140件(primary 94 + advisory 46)を取得し、ファイルごとの内訳を集計した。

| antipattern | 件数 | severity |
|---|---|---|
| low-contrast | 138 | warning 92 / advisory 46 |
| overused-font | 2 | warning |

検出された`low-contrast`の内訳はほぼ全ファイル共通で、実体は2種類の色組だけだった。

1. **warning(92件、31ファイル全てに2件ずつ+template 2件)**: `.eyebrow`(カード先頭の `$ day-NNN / --topic ... / 海外AIネタ100日チャレンジ` 行)で使っている
   `--ink-faint: #626d80` が、ダークモードの背景 `--surface: #161b24` に対して **コントラスト比3.3:1**(WCAG AA基準の4.5:1に届かない)。
2. **advisory(46件)**: ターミナル詳細区画の `--terminal-base: #6b7484` が `--terminal-bg: #090b10` に対して **4.2:1**(4.5:1に僅かに届かないが、検出器側でadvisory=非ブロッキング扱い)。

`overused-font`(2件、`day-014.html`・`day-017.html`)は見出しフォント `Fraunces` の使用を指摘したもの。これは全カード共通の意図的なデザイン(CLAUDE.md記載のテンプレート骨格=フォント変更禁止)であり、ツールのバグではなく「よくあるAIスロップフォント」の機械的な指摘。本検証では対応対象としない(理由は後述)。

## 3. 実際に修正して再検査する(Before/After)

`tools/card-template.html` 自体は編集せず(CLAUDE.md記載の方針)、複製した `experiments/day-034/card-before.html` / `card-after.html` の2ファイルで検証した。

修正内容: `--ink-faint` の値を、背景 `#161b24` に対してWCAG AA(4.5:1)を満たす最小限の色に変える。

- 変更前: `--ink-faint: #626d80;`(contrast 3.3:1)
- 変更後: `--ink-faint: #76839a;`(contrast 4.51:1。元の色のRGBを約1.21倍スケールして色相を保ったまま明度だけ上げた)

計算はWCAG 2.x の相対輝度式をPythonで実装して確認(`sRGB→linear→luminance→(L1+0.05)/(L2+0.05)`)。

```
$ python3 -c "...(WCAG contrast計算)..."
orig contrast: 3.3036955374413908
scale 1.21 new rgb (118, 131, 154) hex 76839a
new contrast: 4.508070363113217
```

修正前後それぞれに `detect` を実行した結果:

```
$ npx --yes impeccable@latest detect --json experiments/day-034/card-before.html
[... low-contrast warning x2 (3.3:1 — text #626d80 on #161b24) ...]
$ echo $?
2

$ npx --yes impeccable@latest detect --json experiments/day-034/card-after.html
[]
$ echo $?
0
```

**1つのCSS変数(`--ink-faint`)の値を1箇所直すだけで、primary findings 2件 → 0件、終了コード 2 → 0 になった。** コントラスト比も実測で3.3:1→4.51:1まで改善し、WCAG AA基準を満たした。

## 4. 触れなかった項目(今回は見送り)

- `overused-font`(Fraunces指摘): 本リポジトリのテンプレートはCLAUDE.mdで「フォント・配色・カードの骨格は100日シリーズを通じて統一するため変更しない」と定めており、指摘自体は妥当だが修正対象から外した。ツールが「よくあるAIっぽいフォント」を機械的に検出できている点自体は確認できた。
- advisory 46件(4.2:1のターミナル文字色): advisoryのため終了コードに影響しないこと、および非ブロッキングという設計自体を確認したのみで、修正は行っていない(閾値にかなり近く、必要なら同じ手法で直せる見込み)。

## 5. エージェント向けコマンド(`help`/`install`等)について

今日の検証スコープの主役である`detect`はローカルの静的HTML解析のみで完結し、ネットワークアクセスは不要だった。
一方で `impeccable help`(利用可能なスキル一覧取得)はimpeccable.style(ホームページ)への通信を試み、本Routineの実行環境では以下のように失敗した。

```
$ npx --yes impeccable@latest help
Could not fetch command list from impeccable.style. Check your network connection.
```

Routine実行環境のエージェントプロキシのステータス確認で、`impeccable.style:443`へのCONNECTがゲートウェイに403で拒否されていることを確認した(`connect_rejected`、`gateway answered 403 to CONNECT`)。これはRoutine環境のネットワーク制限によるものであり、ツール自体の不具合ではない。

- Routine環境の制約により未検証、ローカル検証待ち: `impeccable help` / `impeccable install`(エージェント向けスキル・スラッシュコマンド群の導入、`critique`/`polish`等)の動作確認。
- 再現手順: ローカルPCで `npx --yes impeccable@latest help` および `npx --yes impeccable@latest install` を実行し、インストールされるスキル一覧とその内容を確認する。

本日の検証の主軸(`detect`によるコントラスト検出・Before/After修正)はネットワーク不要で完全に完結しており、上記は「可能であれば」の追加確認項目(優先度低)。

## まとめ

- `impeccable detect`は、APIキー・LLM不要・ネットワーク不要で、本リポジトリの31枚のシェアカードHTML + テンプレートに対して**94件のprimary findings + 46件のadvisory**を実際に検出した。
- 検出された`low-contrast`警告は実体として「テンプレート共通の1色」に起因しており、その1色(`--ink-faint`)を1箇所修正するだけで該当ファイルの findings を0件にできることを、複製ファイルでのBefore/After実行で確認した。
- 検出器自体の挙動はドキュメント通りで、誤検出・クラッシュ等の不具合は確認されなかった。
