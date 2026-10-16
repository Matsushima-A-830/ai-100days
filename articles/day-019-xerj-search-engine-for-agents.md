---
title: "AIエージェント専用の検索エンジンxerjを自分のリポジトリに対して動かしてみた"
emoji: "🔎"
type: "tech"
topics: ["ai", "rust", "elasticsearch", "mcp", "llm"]
published: false
---

## これは何か

[xerj(xerj-org/xerj)](https://github.com/xerj-org/xerj)は、コード・ドキュメント・ログ・PDF等のフォルダをまるごとインデックス化し、AIエージェントがファイル全体を読み込まずに該当箇所だけを取り出せるようにする、Rust製のローカル検索エンジンだ(Apache-2.0)。Elasticsearch 8.x互換のREST APIを持ち、全文検索(BM25)・ベクトル検索・ハイブリッド検索に対応し、MCPサーバーとして16個のツールをAIエージェントに提供する。

本日(記事執筆時点)GitHub Trendingで急伸しており、Zenn・Qiita・noteで検索した範囲では日本語の一次検証記事は見つからなかった。

今回は本リポジトリ(`ai-100days`)自身をxerjのインデックス対象にして、実際に手を動かして検証した。

出典: https://github.com/xerj-org/xerj (Apache-2.0)

## 導入

GitHub Releasesの公式プリビルドバイナリを取得するだけで、追加の有料APIキーは不要だった。

```
$ curl -sSL -o xerj.tar.gz \
    https://github.com/xerj-org/xerj/releases/download/v1.0.0-rc.96/xerj-1.0.0-rc.96-x86_64-unknown-linux-gnu.tar.gz
$ tar xzf xerj.tar.gz
$ ./xerj-1.0.0-rc.96-x86_64-unknown-linux-gnu/xerj --version
xerj v1.0.0-rc.96
```

## 最初の失敗: `autoindex`に`--data-dir`は無い

サーバー起動(`xerj [OPTIONS]`)とクライアント操作(`xerj autoindex <folder>`)が同じバイナリの別サブコマンドになっており、一部のフラグ名が重複していないため混同した。

```
$ xerj autoindex /home/user/ai-100days --data-dir ./data
error: unknown argument: --data-dir
```

`autoindex`は「既に起動しているサーバーに`--url`経由でHTTPで指示する」クライアントであり、データディレクトリを持つのはサーバー起動側だけだった。

## 自己言及的な失敗: データディレクトリをインデックス対象の中に置くと落ちる

サーバーのデータディレクトリ・ログを、インデックス対象フォルダの中(`work/`)に置いたまま全体をautoindexすると、サーバー自身が書き込み続けているログファイルのサイズがスキャン中に変化し、失敗した。

```
error: autoindex stopped with bulk/backend failures:
  .../work/server.log changed size during autoindex (expected 15451, now 22472); retry the run
  | .../work/data/audit.jsonl changed size during autoindex (expected 82, now 118784); retry the run
```

データディレクトリとログを`/tmp`配下に退避し、インデックス対象と完全に分離することで解決した。「検索エンジン自身を動かしているディレクトリをそのまま検索対象にしたくなる」のは自然な操作だけに、最初に踏んでおく価値のある落とし穴だった。

## 安全策による拒否: ファイルが消えると更新を拒否する

退避後、同じフォルダに再度autoindexすると、前回の失敗時に書き込んだ(今は存在しない)ログファイルがレジュームジャーナルに「消えた」と記録され、**更新そのものが拒否された。**

```
error: this attempt made no remote mutations ... removing files from an
indexed folder is not reconciled yet. ... rebuild in place by deleting
the indices this plan publishes and the state directory ..., then
rerunning — this re-extracts and re-embeds the whole corpus.
```

`--fresh`オプションも「削除されたファイルのドキュメントは消さない」仕様のため効かず、復旧にはインデックスとジャーナルを丸ごと削除して全件再構築するしかなかった。安全側に倒れた設計として理解はできるが、「ファイルをいくつか移動・削除してから同じフォルダを再autoindexする」という普段の開発で普通にやりそうな操作が、比較的重い復旧を要求される点には驚いた。

データディレクトリを作り直してクリーンな状態からやり直し、以降の検証を進めた。最終的に本リポジトリ全体(280ファイル)が9.0秒、3,694件のドキュメントとしてインデックスされた。

## lexicalモードでの検索: 短い語句はヒットする、言い換え文はヒットしない

既定の`--embed-mode lexical`(ハッシュベースのオフライン手法で、真の意味理解はしない)で検索すると、短い語句は日本語でも問題なくヒットした。

```
$ xerj search "NULバイト"
─── articles/day-018-reverse-engineer-minified-jquery.md
    ... `\0` エスケープがNULバイトに壊れる ...
```

これはday-018で実際に見つけたバグについての記事がそのままヒットしている。一方、本文中に存在しない「不自然な1文の言い換え」クエリはヒットしない。これはBM25として期待通りの挙動で、ツールの不具合ではない。

`xerj def`(go-to-definition)は、Python・C・Rustの関数定義を正しく拾う。day-002で検証した「同じ`rle_decode`関数のC版・Rust版」を一括で見つけられたのが印象的だった。

```
$ xerj def "rle_decode"
─── experiments/day-002/rust/src/lib.rs:17  [function]
    pub fn rle_decode(input: &[u8], out_cap: usize) -> Result<Vec<u8>, CapacityExceeded>
─── experiments/day-002/c/driver.c:13  [function]
    size_t rle_decode(const uint8_t *in, size_t in_len, uint8_t *out, size_t out_cap);
─── experiments/day-002/c/rle_decode.c:21  [function]
    size_t rle_decode(const uint8_t *in, size_t in_len, uint8_t *out, size_t out_cap)
5 definition(s) from 'ax-*'.
```

一方、Markdown内のコードフェンスに書かれたJavaScript関数(day-018の`toType()`)は`def`では一切拾えなかった。`autoindex map`で見える`language`フィールドの実例はpython/c/rustのみで、JavaScriptはsymbol抽出の対象外と見られる。

## neuralモードの罠: `semantic_text`にならない場合がある

`--embed-mode neural`(all-MiniLM-L6-v2、初回起動時に約90MBを自動ダウンロード)でサーバーを起動し、小さいフォルダ(`articles/`の18ファイル、day-002の9ファイル)を対象にautoindexすると、**`body`フィールドが`semantic_text`にならず、素の`text`のままになる**現象を2回再現した。いずれも処理が1〜1.2秒で完了する小規模なケースだった。

```
$ curl -s http://localhost:9200/<small>-docs/_mapping | ...
  "body": {"type": "text"}
```

対して`experiments/`全体(約200ファイル・4.85MB)という大きめのフォルダを同じサーバーに対してautoindexすると、`body`は正しく`semantic_text`になった。根本原因は特定できていないが、小さく速く終わるコーパスでは埋め込みモデルの初期化前に最初の書き込みが完了し、デフォルトの素のtextマッピングで確定してしまうタイミング依存の挙動を疑っている。

重要なのは、この状態で`xerj_semantic_search`を呼んでも黒く誤魔化さず**HTTP 400で明確に失敗する**ことだ。

```
{"error":{"reason":"semantic query on field [body]: it is not a
  `semantic_text` field, so there is no comparable stored vector to
  match. ..."},"status":400}
```

`--embed-mode neural`を指定したからといって無条件に信用せず、`autoindex map`や`_mapping`で実際のフィールド型を確認すべき、という実践的な教訓が得られた。

## MCPサーバー: 自己診断ヒントが一番の収穫

`xerj mcp`は、既に起動しているノードにHTTP経由でプロキシするだけのコマンドで、Claude Code自身のグローバル設定を書き換える必要がない。day-018で検証したREAの`rea setup`(グローバル設定書き換え+再起動が必要)とは対照的な設計で、無人実行の検証でも安全に試せた(`xerj init`というプロジェクトスコープの設定生成コマンドもあるが、こちらも「再起動が必要」と明記されているため`--dry-run`での確認のみに留めた)。

MCPのJSON-RPC(stdio)を直接叩いて`initialize`→`tools/list`を呼ぶと、backlogで見積もった通り16個のツール(`xerj_search`, `xerj_semantic_search`, `xerj_vector_search`, `xerj_hybrid_search`, `xerj_memory_*`, `xerj_brain_*`, `xerj_map`, `xerj_code_search`, `xerj_plan`, `xerj_hub_*`)が確認できた。

最も印象的だったのは、**xerjがクエリ方法の間違いをレスポンス自身で教えてくる**ことだ。`semantic_text`フィールドに対してプレーンな`xerj_search`(BM25のみ)で日本語の言い換えクエリを投げると、結果とは別に`_xerj.hints`というフィールドでこう返ってくる。

```json
{
  "_xerj": {"hints": [{
    "code": "lexical_on_semantic_text",
    "reason": "`body` is `semantic_text`, but this query scored it with
      BM25 over the analysed text — the embedding written at ingest was
      NOT consulted ... For meaning-based recall run the `semantic`
      query on `body`; to keep both signals, combine them with `hybrid`.",
    "try": {"request": "POST /neu-docs/_search", "body": {"query":
      {"semantic": {"field": "body", "query": "...", "k": 10}}}}
  }]},
  "hits": {"total": {"value": 237}, "hits": [...]}
}
```

結果とは別枠で「このクエリでは何が見えていないか」と「次に何を試すべきか」を具体的なJSON例まで添えて返してくる設計で、AIエージェントが自己修正しやすいよう一貫して作られていると感じた。

実際に`semantic_text`が正しく有効なインデックス(`experiments/`の部分インデックス、383件処理時点)に対して、BM25では0件だった日本語パラフレーズクエリ(「CのバグをRustへの書き換えで安全にした検証のまとめ」)を`xerj_semantic_search`に投げると、スコア0.74〜0.80の範囲で5件の近傍が返ってきた。ただし、本来の「正解」であるはずのday-002(C→Rustのメモリ安全性検証)はこの時点ではまだインデックスに取り込まれていなかった。CPUのみでの実測速度が3〜6KB/sと非常に遅く、`experiments/`全体の再埋め込みには15分以上かかる見積りだったため、検証時間の都合で全件完了を待たずに打ち切った。スコアが0.74〜0.80という狭い帯に収まっている点も、all-MiniLM-L6-v2が英語中心のモデルで日本語の意味差を細かく分離できていない可能性を示しており、過大な評価はできない。

## まとめ

- xerjは、ローカル検索エンジンとしてのElasticsearch互換API・BM25全文検索・go-to-definition・MCPサーバーのいずれも、**追加の有料APIキー・GPUなしで動作した。**
- lexicalモードの短い語句検索・多言語(Python/C/Rust)でのsymbol検索は実用的で、day-002の「同じ関数のC版/Rust版」を一括で見つけられた。
- 一方で、「`autoindex`に`--data-dir`は無い」「データディレクトリをインデックス対象の中に置くと自己言及的に失敗する」「`--embed-mode neural`でも小規模コーパスでは`semantic_text`にならない場合がある」という3つの、デフォルト設定のままでは気づきにくい挙動を実際に踏んで発見した。
- 誤用時に黒く誤魔化さず明確なエラーで止まる設計(HTTP 400、削除検知による拒否)と、クエリの誤用をレスポンス自体の`_xerj.hints`で教えてくれる自己診断機能は、AIエージェント向けツールとして一貫した設計思想を感じさせた。
- 日本語の意味ベース検索は動作するが、既定モデルは英語中心であり、過大な期待はできない。
