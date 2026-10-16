# Day 019 検証結果: xerj-org/xerj を自分のリポジトリに対して動かす

対象: [xerj-org/xerj](https://github.com/xerj-org/xerj) v1.0.0-rc.96 (Apache-2.0)
Elasticsearch互換APIを持つ、AIエージェント向けのローカル検索エンジン(Rust製)。

今日は research routineが見つけた候補の一つを、人間の指示で即日検証する形になった
(通常の「朝にbacklog.md→today.md→昼に実装」という分業ではなく、同日中に
候補選定から検証まで一括で行っている)。

## 導入

GitHub Releasesから公式のプリビルドバイナリ(x86_64-unknown-linux-gnu)を取得した。

```
$ curl -sSL -o xerj.tar.gz \
    https://github.com/xerj-org/xerj/releases/download/v1.0.0-rc.96/xerj-1.0.0-rc.96-x86_64-unknown-linux-gnu.tar.gz
$ tar xzf xerj.tar.gz
$ ./xerj-1.0.0-rc.96-x86_64-unknown-linux-gnu/xerj --version
xerj v1.0.0-rc.96
```

追加の有料APIキーは不要。既定の埋め込みはオフラインの軽量lexical方式でGPUも不要。
(後述の`--embed-mode neural`時はCPUのみで動作したが非常に低速だった。)

## 1. 最初の失敗: `autoindex`に`--data-dir`は存在しない

`xerj [OPTIONS]`(サーバー起動)と`xerj autoindex <folder>`(クライアント、
既に起動しているサーバーにHTTP経由で投げる)は同じバイナリの別サブコマンドで、
一部のフラグ名が重複していないため混同しやすい。`--data-dir`はサーバー起動時
のみのオプションで、`autoindex`には無い。エラーメッセージ自体は明確だった。
詳細: [`samples/01-autoindex-data-dir-flag-error.txt`](./samples/01-autoindex-data-dir-flag-error.txt)

## 2. 自己言及的な失敗: データディレクトリをインデックス対象の中に置くと落ちる

`xerj --insecure --data-dir ./work/data --port 9200`を`work/`ディレクトリの
中で起動したまま、`work/`を含むリポジトリ全体に対して`autoindex`を実行した。
サーバー自身のログ・audit.jsonlが、まさにインデックス中のフォルダの中で
書き込まれ続けていたため、「スキャン中にファイルサイズが変わった」という
理由で`exit=1 reason=aborted`になった。

これは**検証対象ツール自体の挙動に関係する失敗**であり、データディレクトリと
ログの配置場所を自分で誤ったことが直接の原因だが、「サーバーを起動した
ディレクトリの中身をそのままautoindexしたくなる」という自然な操作が
落とし穴になる、という意味で記事に書く価値があると判断した。
詳細: [`samples/02-autoindex-self-pollution-abort.txt`](./samples/02-autoindex-self-pollution-abort.txt)

対策として、xerjのバイナリ・データディレクトリ・ログを`/tmp`配下に退避し、
インデックス対象のリポジトリとは完全に分離してから再実行した。

## 3. 安全策による拒否: インデックス済みフォルダからファイルが消えると止まる

退避後、同じフォルダに対して再度`autoindex`すると、前回の失敗時に書き込んだ
`work/`配下のログファイル(今は存在しない)がレジュームジャーナルに
「消えた」と記録され、**インデックス更新そのものを拒否**された。
`--fresh`も「削除されたファイルのドキュメントは消さない」仕様のため効かず、
復旧には「インデックスとジャーナルを丸ごと削除して全件再構築」が必要だった。
詳細: [`samples/03-autoindex-delete-detection-refusal.txt`](./samples/03-autoindex-delete-detection-refusal.txt)

データディレクトリを作り直してクリーンに再実行し、以降の検証はこの状態を
起点にした。最終的な全体インデックス結果:

```
done in 9.0s — 12 datasets, 3694 records live, 1 duplicate aliases,
  52 junk records, 13 junk/skipped files (411.2 docs/sec)
indexed: 3694 documents live; this run submitted 3414 source records
  from 280 files
```

## 4. lexical(既定)モードでの全文検索・symbol検索

既定の`--embed-mode lexical`(ハッシュベースのオフライン手法、真の意味理解は
しない)で、本リポジトリ自身(`ai-100days`)をまるごとautoindexした。

**日本語の短い語句はヒットする。不自然な1文の言い換えクエリはヒットしない:**

```
$ xerj search "NULバイト"        → day-018関連の3パッセージがヒット
$ xerj search "トークン削減"      → day-001関連がヒット
$ xerj search "Wakaruが復元したコードにNULバイトが混入する不具合"
  → no match (こちらは本文中に存在しない「文」なので当然ヒットしない。
     lexicalはBM25であり意味理解はしない、という前提通りの挙動)
```

**`xerj def`(go-to-definition)はPython/C/Rustの関数を正しく拾う。
day-002で検証した「同じ関数のC版・Rust版」を一括で見つけられた:**

```
$ xerj def "rle_decode"
─── experiments/day-002/rust/src/lib.rs:17  [function]
─── experiments/day-002/c/driver.c:13  [function]
─── experiments/day-002/c/rle_decode.c:21  [function]
5 definition(s) from 'ax-*'.
```

一方、Markdown内のコードフェンスに書かれたJavaScript関数(day-018の
`toType()`)は`def`では一切拾えない(`search`では全文検索としてヒットする)。
`autoindex map`で見える`language`フィールドの実例はpython/c/rustのみで、
javascriptはsymbol抽出の対象外と見られる。
詳細: [`samples/05-xerj-def-multilang.txt`](./samples/05-xerj-def-multilang.txt)

## 5. neuralモードとMCPサーバー、semantic_textマッピングの罠

`--embed-mode neural`(all-MiniLM-L6-v2、初回起動時に約90MBを自動ダウンロード)
でサーバーを起動し、小さいフォルダ(articles/の18ファイル、day-002の9ファイル)
を対象に`autoindex`すると、**`body`フィールドが`semantic_text`にならず、
素の`text`のままになる**現象を2回再現した。いずれも処理が1〜1.2秒で完了する
小規模なケースで発生した。

対して、`experiments/`全体(約200ファイル・4.85MB)という大きめのフォルダを
同じ`--embed-mode neural`サーバーに対してautoindexすると、`body`は正しく
`semantic_text`になった(383件処理時点で確認)。根本原因は特定できていないが、
「小さく速く終わるコーパスでは、埋め込みモデルの初期化前に最初の書き込みが
完了し、デフォルトの素のtextマッピングで確定してしまう」というタイミング
依存の挙動を疑っている。
詳細: [`samples/07-semantic-text-mapping-scale-dependent.txt`](./samples/07-semantic-text-mapping-scale-dependent.txt)

重要なのは、この状態で`xerj_semantic_search`を呼んでも**黒く誤魔化さず
HTTP 400で明確に失敗する**こと(エラーメッセージが「`body`はsemantic_textでは
ない」と原因を明示する)。neuralモードを指定したからといって無条件に
信用せず、`autoindex map`や`_mapping`で実際のフィールド型を確認すべき、
という実践的な教訓が得られた。

**MCPサーバー(stdio, JSON-RPC 2.0)を直接叩いて確認したこと:**

`xerj mcp`は既に起動しているノードにHTTP経由でプロキシするだけで、Claude
Code自身のグローバル設定(`~/.claude.json`)を書き換える必要がない。これは
day-018で検証したREAの`rea setup`(グローバル設定を書き換え、再起動が必要)
とは対照的な設計で、無人実行のRoutineでも安全に検証できた。
(`xerj init`というプロジェクトスコープの設定ファイル生成コマンドも
あるが、これも「エージェントの再起動が必要」と明記されているため、
`--dry-run`で生成内容の確認のみ行い、実際の書き込みは行っていない。)

`initialize`→`tools/list`で、backlogで見積もった通り**16個のツール**
(xerj_search, xerj_semantic_search, xerj_vector_search, xerj_hybrid_search,
xerj_memory_store, xerj_memory_recall, xerj_brain_*, xerj_map,
xerj_code_search, xerj_plan, xerj_hub_*)が確認できた。
詳細: [`samples/08-mcp-tools-list-and-working-semantic.txt`](./samples/08-mcp-tools-list-and-working-semantic.txt)

**最も印象的だった発見: xerjは「クエリ方法の間違い」をレスポンス自身で
教えてくる。** `semantic_text`フィールドに対してプレーンな`xerj_search`
(BM25のみ)で日本語の言い換えクエリを投げると、結果とは別に
`_xerj.hints`というフィールドで「このクエリはBM25のみで評価されており、
embeddingは使われていない。意味ベースの検索には`semantic`または
`hybrid`クエリを使え」という具体的な診断とJSON例まで返ってくる。
詳細: [`samples/06-mcp-self-diagnosing-hint.txt`](./samples/06-mcp-self-diagnosing-hint.txt)

実際に`semantic_text`が正しく有効なインデックス(`experiments/`の部分
インデックス、383件時点)に対して、BM25では0件だった日本語パラフレーズ
クエリを`xerj_semantic_search`に投げると、スコア0.74〜0.80の範囲で
5件の近傍が返ってきた。ただし、肝心の「正解」であるはずのday-002は
まだこの部分インデックスに取り込まれていなかった(CPUのみでの実測速度が
3〜6KB/sと非常に遅く、`experiments/`全体の再埋め込みには15分以上かかる
見積りだったため、検証時間の都合で全件完了を待たずに打ち切った)。
スコアが0.74〜0.80の狭い帯に収まっている点も、all-MiniLM-L6-v2が英語中心の
モデルで日本語の意味差をあまり細かく分離できていない可能性を示しており、
「動いてはいるが過大評価はできない」という評価にとどめる。

## 6. 結論・まとめ

- xerjは、ローカルの検索エンジンとしてElasticsearch互換API・BM25全文検索・
  go-to-definition・MCPサーバーのいずれも、**追加の有料APIキー・GPUなしで
  動作した。**
- lexicalモードの短い語句検索・多言語(Python/C/Rust)でのsymbol検索は
  実用的で、day-002で検証した「同じ関数のC版/Rust版」を一括で見つけられた。
- 一方で、以下の3つの「デフォルト設定のままでは気づきにくい」挙動を実際に
  踏んで発見した:
  1. `autoindex`に`--data-dir`は無い(サーバー起動オプションと混同しやすい)
  2. データディレクトリ・ログをインデックス対象フォルダの中に置くと
     自己言及的に失敗する
  3. `--embed-mode neural`を指定しても、小さく速く終わるコーパスでは
     `semantic_text`マッピングが有効にならない場合がある(スケール依存)
- 3のケースで`xerj_semantic_search`を誤用しても、黙って壊れた結果を返さず
  明確なHTTP 400で止まる点は良い設計だった。
- 最大の収穫は、クエリの誤用をレスポンス自体の`_xerj.hints`で教えてくれる
  自己診断機能で、AIエージェント向けツールとして一貫した設計思想を感じた。
- 日本語の意味ベース検索(`xerj_semantic_search`)は動作するが、既定の
  all-MiniLM-L6-v2は英語中心のモデルであり、スコアの分離が粗く、
  過大な期待はできない。
