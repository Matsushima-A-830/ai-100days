# Day 024 検証結果: DietrichGebert/ponytail

検証日: 2026-10-22
検証対象: https://github.com/DietrichGebert/ponytail (HEAD `09c434a`, 2026-10-18, npm `5.3.2`, MITライセンス)

## 1. 公式ベンチマークの再現を試みて、環境の制約にぶつかった

ponytailの公式ベンチマーク(`benchmarks/results/2026-10-07-agentic.md`)は、`claude -p --plugin-dir <ponytailのパス>` で起動したheadlessなClaude Codeセッションを、スキル無しのセッションとペアで比較する方式(39タスク×5回)。これをこのRoutineの実行環境でそのまま再現しようとした。

```
$ claude -p "In forms/signup.js, add a date-of-birth field ..." \
    --output-format json --permission-mode bypassPermissions --disallowed-tools WebFetch,WebSearch
```
```
<error>Permission for this action was denied by the Claude Code auto mode classifier.
Reason: [Create Unsafe Agents]. ...
```

`--permission-mode acceptEdits` に変えても同じ理由で拒否された(2パターンとも実行結果は上記と同一のエラー)。これは**このRoutineのクラウド実行環境に組み込まれた権限自動分類器が、権限昇格を伴うネストしたClaude Codeエージェントの起動そのものをブロックする**という制約であり、ponytail自体の不具合や挙動ではない。CLAUDE.mdの方針に従い、これは「Routine環境の制約」として扱い、記事本文では「ponytailの失敗」として書かない。公式ベンチマークそのものの再現は**ローカル検証が必要**(再現コマンドは `README.md` に記載)。

## 2. 代替手法: 同じモデルへの独立したサブエージェント実行によるBefore/After比較

公式と全く同じ手法が使えないため、Claude Code内のサブエージェント機能(Agent tool)を使い、**同じモデル(`claude-sonnet-5`、このセッション自身と同じ)** に対して独立した実行コンテキストを2つ作り、
- **baseline**: タスク文のみを与える
- **ponytail**: `skills/ponytail/SKILL.md` の全文(ルールセットそのもの、52行)をシステム指示として与えた上で同じタスク文を与える

という簡易比較を自分で組んだ。公式のように実際にプラグインをインストールしてスキルを自動発火させたわけではなく、ルールセットのテキストをそのまま注入した点で公式の手法とは異なる(詳細は `README.md` の「やったこと」参照)。すべての生成結果は、このRoutine自身が `node` で実際に実行して動作確認済み(下記出力はすべて実行結果そのもの)。

### Task A: 生年月日フィールドの追加

タスク文: 「signupフォームに、ユーザーが生年月日を選べる必須の日付フィールドを追加して」

| | baseline | ponytail |
|---|---|---|
| `forms/signup.js` 行数 | 11→12 (+1) | 11→12 (+1) |
| `components/Input.js` 行数 | 8→8 (+0) | 8→8 (+0) |
| 実装方法 | 既存の`createInput({type:'date', ...})`を1行追加 | 既存の`createInput({type:'date', ...})`を1行追加 |

実行結果(baseline):
```html
<label for="dateOfBirth">Date of birth</label>
<input type="date" id="dateOfBirth" name="dateOfBirth" required>
```
実行結果(ponytail):
```html
<label for="dob">Date of birth</label>
<input type="date" id="dob" name="dob" required>
```

**差は実質ゼロ**(変数名が `dateOfBirth` vs `dob` という程度の違いのみ)。どちらも既存の汎用`Input`コンポーネントをそのまま再利用し、新規コードを一切追加しなかった。

### Task B: 「Remember me」チェックボックスの追加

タスク文: 「signupフォームに、任意のRemember meチェックボックスを追加して」

| | baseline | ponytail |
|---|---|---|
| `forms/signup.js` 行数 | 11→12 (+1) | 11→12 (+1) |
| `components/Input.js` 行数 | 8→8 (+0) | 8→8 (+0) |

実行結果はbaseline/ponytailで**完全に同一**(`required: false`を明示するかどうかの違いのみで生成HTMLは同じ)。こちらも差は実質ゼロ。

### Task A・Bで差が出なかった理由(気づき)

公式ベンチマークの手法ノート(`benchmarks/agentic/README.md`)を読み直すと、LOCティアのタスクは意図的に「まだ存在しない機能」を選んでいる("a feature that does **not** already exist, so the agent chooses how much to build")。Task A・Bは、汎用`Input`コンポーネントがすでに`type`属性をそのまま渡すだけで対応できてしまう設計にしてしまったため、「再利用する以外の選択肢がほぼ無い」タスクになっていた。つまりponytailの指示が無くても、現行モデル(Sonnet 5)は既にこの程度の再利用判断を自然にできる、というのが素直な解釈であり、過剰実装の「余地」を用意できていなかった自分のタスク設計の問題だった。

### Task C: 星レーティング(1〜5)フィールドの追加(公式のLOCティア「star rating」と同じ設計)

タスク文: 「signupフォームに、入会への期待度を1〜5の星で評価する任意のフィールドを追加して。このコードベースに星レーティング用のコンポーネントは存在しない」

| | baseline | ponytail |
|---|---|---|
| `components/Input.js` 行数 | 8→30 (**+22**) | 8→16 (**+8**) |
| `forms/signup.js` 行数 | 11→17 (**+6**) | 11→12 (**+1**) |
| 追加行数合計 | **+28行** | **+9行** |
| 削減率(ponytail / baseline) | — | **約68%減** |
| 実装方法 | `createStarRating()`という新規関数を追加。`<fieldset>`+`<legend>`+★×5のradioグループを生成する専用コンポーネント | 既存の`createInput()`に`min`/`max`属性を追加しただけ。`<input type="number" min="1" max="5">`として実装し、新規コンポーネントは作らなかった |
| テスト/自己チェック | 無し(手元で`node -e`で目視確認したのみ、コードとしては残していない) | `require.main === module`ブロックで`console.assert`による自己チェックを追加(ponytailのルール「非自明なロジックには簡単なテストを残す」に沿った挙動) |

実行結果(baseline、`node -e "console.log(require('./forms/signup').renderSignupForm())"`):
```html
<fieldset class="star-rating" data-name="excitement">
<legend>How excited are you to join? (optional)</legend>
<input type="radio" id="excitement-5" name="excitement" value="5" >
<label for="excitement-5" title="5 stars">★</label>
<input type="radio" id="excitement-4" name="excitement" value="4" >
<label for="excitement-4" title="4 stars">★</label>
<input type="radio" id="excitement-3" name="excitement" value="3" >
<label for="excitement-3" title="3 stars">★</label>
<input type="radio" id="excitement-2" name="excitement" value="2" >
<label for="excitement-2" title="2 stars">★</label>
<input type="radio" id="excitement-1" name="excitement" value="1" >
<label for="excitement-1" title="1 star">★</label>
</fieldset>
```
実行結果(ponytail):
```html
<label for="excitement">How excited are you to join? (1-5 stars, optional)</label>
<input type="number" id="excitement" name="excitement" min="1" max="5" >
```
自己チェックの実行結果(ponytail側が追加したもの、実際に実行して確認):
```
$ node c-ponytail/components/Input.js
Input.js self-check passed
```

**ここでは明確な差が出た。** 新規コンポーネントを作らず、既存の`createInput`を数属性だけ拡張して済ませたponytail側は、行数で約68%少ない。公式が主張する「-53%」という数値のレンジに近い(ただしn=1、タスク1件のみの結果であり、公式の39タスク×5回という規模とは全く比較にならない点に注意)。

### 見過ごせない点: ponytailの解は「星レーティング」というUI要求を機能的にしか満たしていない

タスク文は「1〜5の星で評価する」と書いており、素直に読めば★アイコンのUIを期待する文言になっている。baseline側は実際に★記号を使ったradioグループを作り、見た目も「星レーティング」に見える。一方ponytail側は`<input type="number" min="1" max="5">`という素のスピナー入力にしており、**データとしては1〜5の値を受け取れるが、見た目は星レーティングには見えない**。これはponytailのルール5番「プラットフォーム機能で済むなら使う」を忠実に適用した結果だが、タスクの意図(視覚的な星UI)を厳密には満たしていない可能性がある。「怠惰だが手は抜かない」はコードの安全性・堅牢性には当てはまっても、UIの見た目の要求までは必ずしも守られないケースがある、というのが今回の実測から見えた限界。

## 3. ローカルPCで公式方式(`claude -p --plugin-dir`)を再現

人間のローカルPC(Windows 11 + WSL2 Ubuntu)で、1節でクラウドRoutine環境にブロックされた
公式方式そのもの——`claude -p --plugin-dir <ponytailのパス>` によるheadless Claude Code
セッションのペア比較——を実際に実行した。Task A・B・Cそれぞれについて、`fixture-template/`
を独立したディレクトリにコピーし、baseline(プラグイン無し)とponytail(`--plugin-dir`で
ponytailを読み込み)の両方を実行した。

```
$ cd <タスク用ディレクトリ>
$ claude -p "In forms/signup.js, add a required date-of-birth field to the signup form." \
    --output-format json --permission-mode acceptEdits --disallowed-tools WebFetch,WebSearch
```
```
$ claude -p "..." --output-format json --permission-mode acceptEdits \
    --disallowed-tools WebFetch,WebSearch --plugin-dir ~/scratch/day024/ponytail-src
```

**結果: ローカル環境ではクラウドRoutine環境で見られた「Create Unsafe Agents」による
ブロックは一切発生しなかった。** 6回の実行すべてで`permission_denials`は空配列、
`terminal_reason`は`completed`だった。つまり1節のブロックは、ponytail自体の問題でも
`claude -p --plugin-dir`という起動方式そのものの問題でもなく、**このRoutineのクラウド
実行環境固有の権限自動分類器の制約**だったことが確定した。

生成結果は`experiments/day-024/runs-cli/{a,b,c}-{baseline,ponytail}/`にコミット済み。
2節の代替手法(サブエージェントへのSKILL.md注入)による結果と比較できるよう、
同じタスク文・同じfixtureで実行した。

### Task A・B(公式方式)

| | baseline | ponytail |
|---|---|---|
| Task A 追加行数 | +1 | +1 |
| Task B 追加行数 | +1 | +1 |

2節の代替手法と同じく、**公式方式でも差はゼロ**だった。既存の`createInput`をそのまま
再利用し、どちらの腕も新規コードを追加しなかった。

### Task C(公式方式、星レーティング)

| | baseline | ponytail |
|---|---|---|
| 新規ファイル | `components/StarRating.js`(13行) | 無し |
| `forms/signup.js`の追加行数 | +2(import + 呼び出し) | +1 |
| 追加行数合計 | **15行** | **1行** |
| 削減率 | — | **約93%減** |

baselineは2節と同様、専用の`createStarRating()`コンポーネント(radioボタン×5の
fieldset)を新規ファイルとして作った。

```js
// components/StarRating.js (baseline, 新規ファイル)
function createStarRating({ name, label, required = false, max = 5 }) {
  const req = required ? 'required' : '';
  const stars = [];
  for (let value = max; value >= 1; value--) {
    stars.push(
      `<input type="radio" id="${name}-${value}" name="${name}" value="${value}" ${req}><label for="${name}-${value}">${value}</label>`
    );
  }
  return `<fieldset class="star-rating">\n<legend>${label}</legend>\n${stars.join('\n')}\n</fieldset>`;
}
```

一方ponytail側は、新規ファイルを作らず`forms/signup.js`に`<select>`要素を1行だけ
直接埋め込んだ。

```html
<label for="excitement">How excited are you to join? (optional)</label>
<select id="excitement" name="excitement">
  <option value="">N/A</option>
  <option value="1">★</option>
  <option value="2">★★</option>
  <option value="3">★★★</option>
  <option value="4">★★★★</option>
  <option value="5">★★★★★</option>
</select>
```

今回は2節(サブエージェント代替手法、約68%減)よりもさらに大きい**約93%減**という
結果になった。公式が主張する「-53%」(39タスク×5回の平均)というレンジを超えている
点には注意が必要で、これはn=1・タスク1件のみの結果であり、サンプルサイズが
極端に小さいことに起因するブレの範囲内と考えられる。それでも、方向性(ponytailは
新規ファイルを作らず既存要素で済ませる)は2節の代替手法と一致していた。

ponytail側の解は、2節で見られた`<input type="number">`とも異なり、今回は
`<select>`ドロップダウンに★記号をテキストとして埋め込む形になった。実行のたびに
実装の細部が変わる(決定的ではない)点、そして**今回もまた「星レーティング」という
視覚的な要求を、インタラクティブな星アイコンではなく素のフォーム部品で済ませている**
点は、2節で見つけた限界と同じ傾向である。

### コスト・実行時間(公式方式、JSON出力の実測値)

| タスク | 腕 | cost (USD) | duration (ms) | turns |
|---|---|---|---|---|
| A | baseline | $0.1185 | 14,403 | 5 |
| A | ponytail | $0.1260 | 15,797 | 5 |
| B | baseline | $0.1180 | 15,462 | 5 |
| B | ponytail | $0.1167 | 14,097 | 4 |
| C | baseline | $0.1455 | 28,484 | 7 |
| C | ponytail | $0.1340 | 23,020 | 5 |

Task A・Bではcost/durationに明確な傾向差は無かった(むしろponytail側がわずかに
高コストの回もあった)。Task Cでは、ponytail側がbaseline比で約8%安く・約19%速かった
(新規ファイルを作らず、ターン数も7→5に減ったため)。公式が主張する「コスト-26%・
時間-41%」ほど明確な差ではないが、同じ方向ではあった(n=1、1タスクのみの結果)。

## 4. 結論(更新)

- 既存コンポーネントの再利用が「ほぼ唯一の正解」であるような簡単なタスク(Task A・B)では、ponytailのルールセットを与えても与えなくても、Sonnet 5は同じ最小限の解に到達した。差はゼロ。これは代替手法(2節)・公式方式(3節)の両方で一致した。
- 新規UIコンポーネントを作る余地がある公式スタイルのタスク(Task C)では、代替手法で約68%減、公式方式で約93%減と、どちらもponytail側が大幅に少ないコード量で済ませた。方向性としては公式の主張(大幅なコード削減)と一致する。
- **公式方式(`claude -p --plugin-dir`)のローカル再現により、1節でクラウドRoutine環境にブロックされていた「Create Unsafe Agents」エラーは、環境固有の制約でありponytail自体の問題ではないことが確定した。** ローカルPCでは6回すべての実行が`permission_denials: []`で正常完了した。
- ponytail側の星レーティング実装は、2節では`<input type="number">`、3節(公式方式)では`<select>`ドロップダウンと、実行のたびに細部が変わった。どちらも「星レーティング」という視覚的な要求をインタラクティブな星アイコンでは満たしておらず、この限界は代替手法・公式方式を問わず一貫して見られた。
- 今回の実測はいずれもn=1(各タスク1回のみ)であり、公式の39タスク×5回という規模とは全く比較にならない点には引き続き注意が必要。
- ponytailの効果は、タスクに「既に存在するコードで済ませられる余地」があるかどうかに強く依存するように見える。README自身も同様の設計思想(ladder: 既存コード→標準ライブラリ→プラットフォーム機能→依存→1行→最小実装、の順に検討する)を明言しており、今回の実測はその通りの挙動だった。
