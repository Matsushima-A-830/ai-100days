---
title: "diagram-designスキルに自分のリポジトリの1日サイクルを図解させてみた"
emoji: "🗺️"
type: "tech"
topics: ["ai", "claudecode", "svg", "agentskill", "diagramming"]
published: false
---

## 今日のネタ: diagram-design(2回目)

[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) というリポジトリを、本シリーズでは2回目になるが別の切り口で検証した。
自然言語の指示だけで自己完結したHTML+インラインSVGのエディトリアル調図解を生成するClaude Code向けのagent skillである。
前回(Day 011)はこのスキルの指示をスイムレーン図1枚に適用し、素のMermaidとの見た目をBefore/Afterで比較した。
今回は「このスキルに、このリポジトリ自身の運用フローを2種類の図として説明させたら、実際にどこまで使えるか」を検証した。

ライセンスはMIT(Copyright (c) 2025 Cathryn Lavery、リポジトリ直下の`LICENSE`ファイルで確認済み)。
検証時点のHEADは`11b08ead`(2026-10-13時点のコミット)。
筆者が検索した範囲ではZenn・Qiita・noteのいずれにも日本語での一次紹介記事は見つからなかった。

## また公式インストールは拒否された

today.mdの指示通り、まずは公式のplugin marketplace経由でのインストールを試した。

```
$ claude --print "/plugin marketplace add cathrynlavery/diagram-design"
Permission for this action was denied by the Claude Code auto mode classifier.
Reason: [Untrusted Code Integration].
```

Day 011で確認したのと同じ理由で拒否された。
これはこのクラウド実行環境のサンドボックスが持つ安全策であり、スキル自体の不具合ではない。
そこで今回もDay 011で確立した方法、つまりリポジトリを読み取り専用でcloneし、`SKILL.md`と各図タイプのリファレンスを自分で読んで、その設計ルールを手で適用するという方法を踏襲した。

## 図その1: CLAUDE.mdの4段階フローをフローチャートにする

`SKILL.md`の図タイプ選定表を見ると、フローチャートは「分岐を含むユーザー向けの判断ロジック」に向くとある。
CLAUDE.mdに書かれている「朝: リサーチRoutine→通勤中: 人間がPRマージ→昼: 実装Routine→夜: 人間がレビュー・公開」という1日サイクルには、実際に分岐が1つ存在する。
実装Routine自身が「today.mdが未設定なら何もせず終了する」という条件を持っているので、これをひし形の分岐ノードとして組み込んだ。

`references/type-flowchart.md`の規約は明確だった。
形がノードの種類を表す(楕円=開始/終了、矩形=ステップ、ひし形=分岐)ので色で種類を示してはいけない。
ハッピーパスか、最も重要な1つの分岐だけに珊瑚色のアクセントを使う。
ひし形から出る矢印はYES/NOどちらにもラベルを付ける。

出来上がったのが次の図である。

![day-016のフローチャート](./diagram-flow.png)

ノード数は8、矢印は7本で、`SKILL.md`が定める複雑さ予算(ノード9個・矢印12本まで)の範囲に収まった。
ハッピーパス(today.md設定済み→実装Routineへ進む矢印と、そのノード自体)だけに珊瑚色を使い、他の矢印・ノードはすべてグレー系の`muted`トーンにした。

## 図その2: experiments/day-NNNが増えていく構成をアーキテクチャ図にする

2枚目は`references/type-architecture.md`に従って、`experiments/`配下にday-013→014→015→016とディレクトリが積み重なっていく様子と、最新のday-016が`articles/`と`posts/`に出力を生成する関係を描いた。

ここで実際に手が止まった場面があった。
当初の設計では`posts/x`・`posts/note`・`posts/cards`をそれぞれ別のノードにするつもりで、day-016ノードから3本の矢印を引こうとしていた。
しかし`SKILL.md`冒頭の設計思想には「常に一緒に移動する2つのノードは1つのノードである」という削除原則が書かれている。
この3つのファイルは実装Routineが必ず同じタイミングで1セットとして作るものなので、まさにこの原則が当てはまる。
そこで3ノードを「X案・note・シェアカード」という1つのノードにまとめ、サブラベルに`x/ note/ cards/ day-016.*`と列挙する形に変更した。
結果としてノード数は8→6、矢印は7→5に減り、ゾーンもアーキテクチャ図の上限である3つ(`EXPERIMENTS/`・`ARTICLES/`・`POSTS/`)にきれいに収まった。

![day-016のアーキテクチャ図](./diagram-architecture.png)

day-016ノードから`articles/`と`posts/`への2本の矢印は、縦方向にも横方向にも離れた位置への接続になる。
`type-architecture.md`が示す直交コネクタ(縦→横→縦、または横→縦→横に曲がる)のルールを、縦に出て横に渡り縦に入るパターンとして適用し、2本の矢印の水平区間のY座標を24px(規約が求める12px以上のオフセット)ずらすことで、矢印同士が重ならないようにした。

## ブラウザでの表示確認: 今回はChromiumが使えた

Day 012の検証時点では、このクラウド実行環境にはブラウザがプリインストールされておらず、シェアカードの見た目確認はHTML/CSSの目視チェックにとどめていた。
今回の実行環境には`/opt/pw-browsers`にChromiumがプリインストールされており、Playwright経由で実際に2枚のHTMLをブラウザで開いてスクリーンショットを撮ることができた。

```
$ node shot.mjs diagram-flow.html diagram-flow.png
{"errors":[]}

$ node shot.mjs diagram-architecture.html diagram-architecture.png
{"errors":[]}
```

どちらもconsoleエラー・pageerrorともになし。
外部リソースはGoogle Fontsのみで、SKILL.mdが求める「単一HTMLファイル完結」の要件も満たしている。

## 自動チェックスクリプトは今回も動かせなかった

スキルには`scripts/self_check.py`や`scripts/verify-geometry.py`という、生成したSVGが規約通りか機械的に検証するスクリプトが同梱されている。
Day 011の時点でこれらの実行はサンドボックスに拒否されており、今回も同じ制約が続くと判断して実行を試みず、代わりに`SKILL.md` §9の「Pre-Output Checklist」の技術項目を1つずつ自分の目で確認した(`experiments/day-016/results.md`に全項目のチェック結果を記録した)。
これは検証対象ツールの欠陥ではなく、このクラウド実行環境のサンドボックス固有の制約であり、記事の評価には含めない。

## 「45種類」という表記は今の所正しかった

このスキルを選んだbacklog.mdのメモには「READMEの表記と実際のギャラリーの数に食い違いがあるとの報告もある」という注記があった。
実際に数えてみたところ、`skills/diagram-design/references/`配下の図タイプ別リファレンス(`type-*.md`)はちょうど45件で、README本文の「45 diagram types」という表記と一致していた。

```
$ ls skills/diagram-design/references/type-*.md | wc -l
45
```

`docs/screenshots/`には47枚のPNGがあったが、差分の2枚は`import-drawio.png`(インポート機能のデモ)と`quadrant-consultant.png`(quadrantタイプのバリアント違い)で、独立したタイプではなかった。
検証時点のバージョンでは、報告されていたような食い違いは確認できなかった。

## まとめ

- CLAUDE.mdの4段階フローはフローチャートとして、`experiments/day-NNN`の積み重なりはアーキテクチャ図として、それぞれスキルの規約通りに手で描くことができた。
- アーキテクチャ図を作る過程で、スキルが掲げる「常に一緒に動く要素は1つのノードにまとめる」という削除原則を実際に自分の設計判断に使う場面があった。
- 公式のplugin経由のインストールは今回もクラウド実行環境のサンドボックスに拒否されたため、スキルの指示書を手で適用する方法で検証した。これは環境固有の制約であり、ツール自体の評価には影響しない。
- README記載の「45種類」という図タイプ数は、検証時点のリポジトリの実際のリファレンス数と一致していた。

出典: https://github.com/cathrynlavery/diagram-design (MIT License)
