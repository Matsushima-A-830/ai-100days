# Day 044 — debpalash/VoiceStudio 再現手順

**ローカル検証が必要。** Routine実行環境ではDockerイメージの取得自体(GHCR経路)と、
モデル重みのダウンロード(ライセンス受理不要なエンジンも含め)がネットワーク制約で
完了できなかった。加えて、既定モデルのライセンス受理(非商用条項への同意)は
人間が行うべき操作のため、Routineからは意図的に行っていない。
詳細は[results.md](./results.md)を参照。人間のローカルPC(ネットワーク制約なし)では
以下のコマンドをそのまま実行すれば、今日の検証(ボイスクローンの生成音声を聴いて評価する)
を完了できるはずである。

## 前提

- Docker(Docker Desktop / Docker Engine)が使えること。
- ディスク空き容量: イメージ本体で約6〜18GB(レイヤー展開後)+ モデル重み数百MB〜数GB。
- 対象リポジトリ: https://github.com/debpalash/VoiceStudio (AGPL-3.0)

## 1. コンテナを起動する

READMEの既定経路(GHCR)でもローカルPCなら問題なく取得できるはず。Routine環境で検証した
Docker Hubミラーでもよい(どちらも同じイメージ)。

```bash
export OMNIVOICE_API_KEY="$(openssl rand -hex 32)"
docker run -d --name omnivoice \
  -p 127.0.0.1:3900:3900 \
  -e OMNIVOICE_API_KEY \
  -e OMNIVOICE_DATA_DIR=/app/omnivoice_data \
  -v omnivoice-data:/app/omnivoice_data \
  ghcr.io/debpalash/voicestudio:stable
  # ブロックされる場合は代わりに: palashdeb/omnivoice-studio:stable (Docker Hub)
printf 'API key: %s\n' "$OMNIVOICE_API_KEY"
```

起動確認:

```bash
curl http://localhost:3900/health
# {"status":"ok","device":"cpu","version":"0.5.7"}
```

ブラウザで http://localhost:3900 を開けばWeb UIでも同じことができる。以下はAPI直叩き
(ヘッドレスブラウザ不要)での再現手順。`$KEY`は上で生成した`OMNIVOICE_API_KEY`。

## 2. 既定モデル(OmniVoice)のライセンスを確認し、受理する

**ここは人間が内容を読んで判断すること。** 既定モデルの学習済み重みはCC-BY-NC
(非商用限定)で、商用推論は制限されている(`results.md` §3, §6参照)。個人の検証目的
での利用が自分の状況に合うか確認してから進める。

```bash
KEY=<上で生成したOMNIVOICE_API_KEY>

# ライセンス条文とfingerprintを確認
curl -s "http://localhost:3900/models/licenses/details/k2-fsa%2FOmniVoice" \
  -H "Authorization: Bearer $KEY" | python3 -m json.tool

# 内容を読んで同意できる場合のみ、返ってきたfingerprintを使って受理する
curl -s -X POST http://localhost:3900/models/licenses/accept \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"repo_id":"k2-fsa/OmniVoice","fingerprint":"<上のレスポンスのacceptance.fingerprint>","accepted":true}'
```

## 3. 参照音声を用意する(自分の声を推奨)

著作権上問題のない数秒〜20秒の音声を用意する(`max_ref_seconds`は20秒)。
手早く動作だけ確認したい場合は、アプリに同梱されたデモ音声でもよい。

```bash
# 同梱デモ音声を使う場合
curl -s "http://localhost:3900/profiles/demo0001/audio" \
  -H "Authorization: Bearer $KEY" -o ref.wav
REF_TEXT="Hey. I'm the VoiceStudio demo voice. I was made right here, on your machine: private, local, and ready whenever you are."
```

自分の声を使う場合は`ref.wav`を自分の録音に差し替え、`REF_TEXT`をその録音の発話内容
(なるべく正確な書き起こし)に置き換える。

## 4. クローンした声で別のテキストを生成する(英語)

```bash
curl -s -X POST http://localhost:3900/generate \
  -H "Authorization: Bearer $KEY" \
  -F "text=This sentence was never spoken by the reference voice. If it sounds like the same person, the clone worked." \
  -F "ref_audio=@ref.wav" \
  -F "ref_text=$REF_TEXT" \
  -F "language=English" \
  -o cloned_en.wav
```

## 5. 日本語テキストで読み上げさせ、646言語対応の主張の一部を確認する

```bash
curl -s -X POST http://localhost:3900/generate \
  -H "Authorization: Bearer $KEY" \
  -F "text=このテキストはクローンした声で日本語を読ませたテストです。発音が自然かどうかを確認します。" \
  -F "ref_audio=@ref.wav" \
  -F "ref_text=$REF_TEXT" \
  -F "language=Japanese" \
  -o cloned_ja.wav
```

## 6. 結果を聴いて評価する

- `ref.wav`(参照音声)と`cloned_en.wav`(同じ声で別の英文)を聴き比べ、声質・話者の
  同一性が保たれているかを評価する。
- `cloned_ja.wav`を聴き、日本語の発音の自然さ・不自然なアクセントや読み間違いがないかを
  確認する。
- `GET /engines/tts`(`Authorization: Bearer $KEY`付き)の`supported_language_names`
  (648件、`results.md` §5参照)から、日本語以外にもう1〜2言語試すと主張の裏取りが厚くなる。

```bash
curl -s http://localhost:3900/engines/tts -H "Authorization: Bearer $KEY" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['backends'][0]['supported_language_names'])"
```

## 7. 片付け

```bash
docker stop omnivoice && docker rm omnivoice
docker volume rm omnivoice-data   # モデル重み・生成履歴も含めて消す場合
```

## ローカル検証後にやること

- `results.md`に「## ローカル検証(人間のPC、日付)」の節を追記し、上記の結果
  (聴いた印象・発音品質・言語ごとの違い)をそのまま記録する。
- その結果をもとに`articles/day-044-*.md`・`posts/x/day-044.md`・`posts/note/day-044.md`・
  `posts/cards/day-044.html`を作成する(CLAUDE.md記載のslug命名規則・frontmatter必須)。
  Routine環境で確認済みの内容(§1〜3, 5〜6)はそのまま使ってよい。

## ローカル検証(実施済み・2026-11-11)

人間(matsu)の同意を得た上で2件のモデルライセンスを受理し、実際にクローン音声を生成・試聴した。

- GHCR経由のイメージ取得はローカルでは問題なく成功し、Routine環境固有の制約だったことを裏付けた。
- ライセンス受理後、`/generate`を呼ぶと別の問題に遭遇した: イメージに同梱の`httpx2`パッケージが、
  Hugging Face側のBrotli圧縮レスポンスを解凍する際に`brotli`パッケージとのバージョン不整合で
  `TypeError: process() takes no keyword arguments`を起こし、必ず失敗していた。これはネットワーク
  制約ではなく、イメージ自体の依存関係バグ。
- コンテナ内の該当ファイルを1行パッチ(`docker exec ... sed`)して`docker restart`すると、
  英語・日本語・フランス語それぞれでクローン音声の生成に成功した(CPU推論、各約30〜38秒)。
- 生成した音声を人間が実際に聴いて評価: 英語は「ほとんど同じ話者」、日本語は「話者は同じだが
  日本語ネイティブぽさに欠ける、外国語訛りに近い」発音だった。

詳細は`results.md`の「ローカル検証」節を参照。
