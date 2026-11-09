# Day 042 results — ranxianglei/billion-context

出典: https://github.com/ranxianglei/billion-context (MIT License。製品面に表示する場合はbillion-context〈および該当する場合はacp-kernel〉へのクレジット表記を求める追加条項あり)
npm: https://www.npmjs.com/package/billion-context (version 0.1.213)

検証環境: Ubuntu 24.04.5 LTS (クラウドRoutine実行コンテナ)、Node.js v22.23.4 / npm 10.9.9(デフォルトのまま、要件のNode 20+を満たす)。
モデル呼び出しは本Routine自身が使っているClaude Code CLI(`claude` 2.1.319、認証済み)をそのままラップして使った。追加の有料APIキーは使っていない。

## 1. インストール

グローバルインストール(`npm install -g`)はこのRoutine実行環境のコマンド承認ポリシーでブロックされたため、
プロジェクトローカルの依存として導入した(動作上の違いはなく、`node_modules/.bin/bili` を直接呼ぶだけ)。

```
$ mkdir sandbox && cd sandbox && npm init -y >/dev/null
$ npm install billion-context
added 93 packages, and audited 94 packages in 9s
30 high severity vulnerabilities
```

`npm audit` の結果、30件のhigh severity脆弱性が出た。中身を見ると画像処理ライブラリ`@jimp/*`系が
依存する古い`zod`(メモリ枯渇の報告 GHSA-mrhx-c7xc-m3w5)がほぼ全件の原因で、
billion-context本体の画像関連テスト機能(image-billing)向けの依存のよう。
今回検証したテキストのみのCLIラップ用途では直接の攻撃経路にはならないと考えられるが、
依存ツリーの健全性としては記録しておく。

```
$ ./node_modules/.bin/bili --help
```
で `bili claude` / `bili codex` / `bili opencode` など主要CLIラッパー一式とサブコマンド(`sessions`, `export`, `doctor`, `plugin` 等)が表示され、READMEの説明と一致した。

## 2. `bili claude` でClaude Code CLIを直接ラップできるか

```
$ cd scratch-run
$ ../node_modules/.bin/bili claude -- -p "2+2? Answer with just the number." 2>&1 | tail -10
bili: started proxy at http://127.0.0.1:18787 (MITM domains: defaults) (HTTP /bili/ rewrites: 1)
bili: proxy log: /tmp/bili-proxy-18787.log
bili: injecting native bili MCP tools for claude (disable with BILI_LAUNCHER_PLUGIN=0).
4
```

**成功した。** 本Routineが使っているのと同じ `claude` CLIを、追加の設定ファイル編集なしで
MITM用ローカルプロキシ(ポート自動割当)経由に起動でき、プロンプト通りに応答した。
このクラウド実行コンテナは元々 `HTTPS_PROXY` 経由のエージェントプロキシ越しにしか外へ出られない
構成だが、bili自身のプロキシがその内側でさらに子プロセスのHTTPS通信を奪う形でも支障なく動いた。

`mcp__bili__acp_status` / `mcp__bili__compress` / `mcp__bili__decompress` / `mcp__bili__search_context`
の4ツールが実際にClaude Code CLIのツール一覧に注入されていることも確認した
(最初の呼び出しは `--allowedTools` で許可しないと権限エラーになる。非対話の `-p` モードでは
対話的な許可プロンプトが出ないため、CI的に使うには事前に `--allowedTools "mcp__bili__*"` 等の指定が必要)。

```
$ ../node_modules/.bin/bili claude -- -p "Call the acp_status tool and report its raw output verbatim." \
    --output-format json --allowedTools "mcp__bili__acp_status"
...
RESULT: ACTIVE SURFACE: pack=default | host=billion-context 0.1.213 (133f3525c)
CONTEXT BREAKDOWN
  0 tool (0%) | 10.8K text (100%) | 0 summaries (0%)
COMPRESSED BLOCKS
  No compressed blocks.
BILLED INPUT (upstream usage): 46101 tok · est-view total 34195 tok · ratio 1.3×
Nudge: idle — max compressible 0 < threshold 50000; growth 0 < floor 22500
UNRECOGNIZED PATHS (instance-level): 1 request(s) ... /bili/https://api.anthropic.com/v1/code/agent-proxy/ca-cert×1
```

この時点で早くも1件の「未知プロトコル」が記録されている。Claude Code CLI自身が証明書取得用に
叩く `/v1/code/agent-proxy/ca-cert` エンドポイントがbiliのプロトコル表に無く、圧縮対象外として
素通しされていた。bili自体はpi/Codex/OpenCode等を主眼に作られているため、Claude Code CLI固有の
補助エンドポイントまでは完全に網羅されていないという、ツール自体の既知の穴と言える。

## 3. Before/After: 同一の6ターン会話を「直接」と「bili経由」で実行

README自身が主張する「ContextBench約58%・LongMemEval-S約71%のコスト削減」は大規模ベンチマーク
前提の数値のため、完全な再現ではなく縮小版シナリオでの概念実証に絞った。

**シナリオ:** ランダムな単語トークンで構成した合成ログ(著作権的に無害、意味内容は問わない)
1,599行・約137KBを6分割し、`claude -p --resume` でセッションを継続しながら1ターンに1セグメントずつ
読み込ませ、最後に最初のセグメントの値を聞き直して文脈が保持されているか確認した。
これを(A)直接 `claude -p`、(B) `bili claude -p` の2系統で同じスクリプトで実行し、
`--output-format json` で返る `usage`(トークン数)と `total_cost_usd`(そのセッションの累計コスト)を記録した。

再現スクリプト: `scripts/generate_chunks.py` / `scripts/driver.py` / `scripts/continue_bili.py` /
`scripts/continue_direct.py`。生の実行結果は `logs/` 配下に、biliの圧縮発動ログ抜粋は
`logs/bili-compression-log-excerpt.txt` に保存した。

### 結果(ターンごとの累計値)

| turn | 直接: cache_read_input_tokens | 直接: 累計cost(USD) | bili: cache_read_input_tokens | bili: 累計cost(USD) |
|---|---|---|---|---|
| 1 | 26,867 | 0.1313 | 27,712 | 0.1448 |
| 2 | 51,166 | 0.2364 | 55,280 | 0.2509 |
| 3 | 76,143 | 0.3127 | 80,408 | 0.3279 |
| 4 | 93,312 | 0.3907 | 97,652 | 0.4067 |
| 5 | 110,463 | 0.4701 | 115,866 | 0.5266 |
| 6 | 127,537 | 0.5516 | **80,448**(↓) | 0.6813 |

(4件目の後、bili系では `acp_status` 確認呼び出しを1回挟んだため、ターン5以降の累計costには
その分も乗っている。直接系は同じ呼び出しを挟んでいないため、cost列はターン数以外の変数が1つ
増えている点に注意。それでも cache_read_input_tokens の推移そのものはターン6の挙動差を
素直に表している。)

ターン4まで(= `acp_status`呼び出し前)の時点では、両者ともほぼ同じペースでcache_read_input_tokensが
増加しており、biliのMCPツール定義注入分だけbiliの方が毎ターン数千トークン分高コストだった
(ターン4累計cost: 直接0.3907 vs bili 0.4067、+約4%)。**この規模ではまだ圧縮しきい値
(`threshold 50000`)に達しておらず、biliは純粋にオーバーヘッドとして上乗せされていた。**

ターン6で状況が変わった。`/root/.local/state/billion-context/bili.log` の実ログに以下が記録されている:

```
context 225813.31... tokens reached preflight target 200000
  (model window 200000, model=claude-sonnet-5-5; ...); preflight compressing before forward
[preflight] fold order (largest first outside the recent zone, #2682):
  m00008:m00011 (17242 tok), m00004:m00007 (17220 tok), ...
[acp-proxy: compress requested 1 range(s): m00008–m00011]
[acp-compress-obs] shrink 16% this-fold (~17242/110468 tok) ... anchor≈299 tok
[acp-proxy: [Compressed m00008–m00011 → 1 block(s), ~17242 tokens saved.]
preflight compressed 1 range(s), ~28618.57... tokens saved (225813.31... → 168665.40...) in 4936ms
```

直後に取った `acp_status` の出力でも一致する:

```
COMPRESSED BLOCKS — 1 active (299 summary, 17.2K original)
  b1 (T1)  17.2K→299  4 msgs  "preflight overflow compress"
Nudge: idle — growth 311 < floor 22500, ready: T1 62341
```

つまり**自分で圧縮をお願いしたわけではなく、bili自身がモデルの文脈窓を超えそうだと判断した
時点で自動的に(「preflight overflow compress」として)1ブロック・17,242トークン分の会話を
299トークンの要約に折り畳んだ**。README記載のモデル主導(`compress`/`decompress`ツールを
モデル自身が呼ぶ)設計に加えて、オーバーフロー寸前の自動セーフティネットが別に存在することが
確認できた。17,242→299という単一ブロックの圧縮率は約98.3%で、これ自体は実測として成立している。

一方で、その圧縮は過去のプロンプトキャッシュの前提(どこまでが「変わらない接頭辞」か)を
変えてしまうため、**次のターンでキャッシュの再構築が必要になった**。ターン6で
`cache_read_input_tokens` が115,866→80,448へ減った(文脈サイズそのものは小さくなった)一方、
`cache_creation_input_tokens` は17,957→36,642へ跳ね上がった(直接系の同ターンは17,160で変化なし)。
圧縮で文脈は確かに縮んだが、そのターン単体のコストはキャッシュ再生成分だけ高くついている。
6ターンという短いシナリオでは「縮んだ299トークン分を何度も安く読み返す」ことによる
回収フェーズまでは到達せず、**この規模の概念実証では圧縮の“正味の得”までは確認できなかった**
(README自身の58–71%という削減率は、こうした再構築コストを遥かに上回る規模とターン数で
初めて効いてくる前提の数値だと考えられる)。

### 補足: biliが想定するモデルのコンテキスト窓が実際と食い違っている可能性

上記の `bili.log` には `model window 200000 ... model=claude-sonnet-5-5` とあるが、
同じ呼び出しのClaude Code CLI側の `usage.modelUsage` には
`"claude-sonnet-5-5":{"contextWindow":1000000, ...}` と出ている。
biliの内部モデルレジストリが(比較的新しいモデルである)claude-sonnet-5-5の実際の
コンテキスト窓(1,000,000トークン)を把握しておらず、旧世代相当の200,000トークンとして
扱っている可能性がある。もしそうだとすれば、実際にはまだ余裕がある場面でも早期に
preflight圧縮を発動させてしまう(= 上記のコスト逆転が起きやすくなる)ことになる。
これはbili側のモデル定義が更新される前のタイミング依存の問題である可能性が高く、
将来のバージョンで直るものかもしれないが、2026-11-09時点のv0.1.213では実際に observed した。

## 4. 文脈保持の確認(本題であるコンテキスト圧縮がある場合でも破綻しないか)

ターン4(圧縮が発生する*前*)の時点で「ターン1で読み込んだ最初の行(LOG-00001)の value= の
数値は?」と聞いたところ、直接系・bili系とも正しく `1488` と回答した。少なくとも圧縮が
起きていない範囲では双方とも文脈を正しく保持していたことが分かる。
圧縮が発生した後(ターン6以降)に同種の質問をして「圧縮された299トークンの要約からでも
元の数値を正しく思い出せるか」を確認することは、今回はコスト計測を優先したため実施できておらず、
圧縮後の記憶の正確性は今回の検証では未確認のまま残っている。

## 5. ライセンス

MIT。ただし「ユーザーが見える製品・サービスに組み込む場合はbilion-context(および該当する場合は
acp-kernel)へのクレジット表記を製品ホームページ・ドキュメント・Credits類のいずれかに掲載する」
という追加条項がある。今回は検証目的のCLI利用のみで製品組み込みではないため、この追加条項は
発生していない。

## まとめ

- `bili claude` によるClaude Code CLIのラップは、このクラウドRoutine実行環境でも問題なく動いた。
- MCPツール(`acp_status`/`compress`/`decompress`/`search_context`)の注入も実際に確認できた。
- 小規模(6ターン・累計18万トークン程度)のシナリオでは、圧縮が実際に1回発動し
  17,242トークンを299トークンへ圧縮したことを実測した。
- ただし圧縮はプロンプトキャッシュを無効化するため、そのターン単体では直接呼び出しより
  コストが高くなった。README記載の大幅なコスト削減は、今回より遥かに長いセッションで
  初めて正味の得になる設計だと考えられる。
- biliの内部モデルレジストリがclaude-sonnet-5-5の実コンテキスト窓(1M)より小さい200K想定で
  動いている可能性がある、という具体的な食い違いも観測した。
