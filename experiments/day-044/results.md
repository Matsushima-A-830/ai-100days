# Day 044 検証結果 — debpalash/VoiceStudio

対象: https://github.com/debpalash/VoiceStudio (AGPL-3.0)
検証したcommit(`main`、参照用にclone): `c85a866f19dfddd6a31c50f88ee2e08e644c77ea`
実際に動かしたのは`docker run`で取得したタグ付きイメージ `palashdeb/omnivoice-studio:stable`
(`docker.io`上のダイジェスト `sha256:65f1305c749c759d3656fed5f12623a98aff11e5f326d28bf7095cb57f3a9e0b`)
で、アプリ内部の`/health`が返すバージョンは`0.5.7`。`main`の`package.json`は`0.5.8-beta.4`であり、
`stable`タグはそれよりわずかに古い。

## 0. 冒頭の結論

**ボイスクローンの生成音声を実際に聴いて評価する、という今日の検証の核心部分はRoutine環境の
ネットワーク制約により未達成。ローカル検証待ち。** 再現手順は [README.md](./README.md) に
そのまま実行できる形で用意した。以下はRoutine環境内で実際に確認できたこと・できなかったことの記録。

## 1. Docker起動は一度の回避策で成功した

本Routine実行環境ではDockerデーモンが既定で起動していなかったが、`dockerd &`で手動起動すると
正常に動作した(`docker --version` → `Docker version 29.9.2, build a82e528`)。

READMEが案内する既定の取得先はGHCR(`ghcr.io/debpalash/voicestudio:stable`)だが、これは
このRoutine実行環境のネットワークポリシーでブロックされていた。

```
$ docker pull ghcr.io/debpalash/voicestudio:stable
failed to copy: httpReadSeeker: failed open: failed to do request:
Get "https://pkg-containers.githubusercontent.com/...": dial tcp:
lookup pkg-containers.githubusercontent.com on 8.8.8.8:53: no such host
```
(プロキシ経由で再試行すると `403 Forbidden`。プロキシの状態確認エンドポイントでも
`gateway answered 403 to CONNECT (policy denial or other refusal)` と記録されていた。)

これはRoutine実行環境のネットワークポリシーに起因するものと判断し、回避策として
READMEに明記されている**Docker Hubミラー**(`palashdeb/omnivoice-studio:stable`)を使った。

```
$ docker pull palashdeb/omnivoice-studio:stable
stable: Pulling from palashdeb/omnivoice-studio
Digest: sha256:65f1305c749c759d3656fed5f12623a98aff11e5f326d28bf7095cb57f3a9e0b
Status: Downloaded newer image for palashdeb/omnivoice-studio:stable
```
(イメージサイズ: `docker images`表示でDISK USAGE 17.3GB / CONTENT SIZE 5.81GB。初回取得は
約5.9GB分の転送に数分かかった。)

Docker Hubミラー経由では取得できたため、「GHCR既定経路がこの環境でブロックされていた」という
事実自体はDocker Hub側で問題なく回避できており、これ以上のエスカレーションは不要と判断した。

## 2. コンテナ起動・ヘッドレスWeb UI/APIは正常に動作した

```
$ docker run -d --name omnivoice-test -p 127.0.0.1:3900:3900 \
    -e OMNIVOICE_API_KEY=testkey123 palashdeb/omnivoice-studio:stable
$ curl http://localhost:3900/health
{"status":"ok","device":"cpu","version":"0.5.7"}
```

起動ログも正常(DBマイグレーション完走、デモ音声プロファイル`Demo Voice`を自動シード、
`/mcp`にMCPサーバーもマウント)。OpenAI互換API(`GET /v1/audio/voices`)や音声プロファイル一覧
(`GET /profiles`)も認証ヘッダー(`Authorization: Bearer <OMNIVOICE_API_KEY>`)付きで正常応答した。
`GET /profiles`はシード済みデモ音声`demo0001`(参照音声`demo0001.wav`、"Hey. I'm the VoiceStudio
demo voice. ..." というテキスト付き)を返し、`GET /profiles/demo0001/audio`で実際にWAVファイル
(RIFF/WAVE, PCM 16bit mono 24000Hz, 349,484バイト)としてダウンロードできた。

重要な気づき: VoiceStudioはElectronのGUI前提のアプリだが、Docker版はOpenAI互換の
`/v1/audio/speech`や独自の`POST /generate`(`ref_audio`をmultipartでアップロードするだけで
ゼロショットクローンができる)というREST APIを公開しているため、**ヘッドレスブラウザ(Playwright等)
を使わずcurlだけでボイスクローンの検証ができる**設計だった。today.md作成時点ではPlaywrightでの
UIスクリーンショットを想定していたが、実際にはAPI直叩きの方が確実で高速だった。

## 3. 既定の音声合成モデル(OmniVoice)はライセンス受理が必須で、Routineでは受理できなかった

起動直後のログに以下があった。

```
2026-11-11 01:15:23,933 INFO [omnivoice.model] Preload skipped: the OmniVoice model licence is not accepted yet.
```

`GET /models/licenses/details/k2-fsa%2FOmniVoice` を呼ぶと、ライセンス詳細が返ってきた。

```json
{"repo_id":"k2-fsa/OmniVoice","info":{"license":"CC-BY-NC (version unspecified); Higgs Audio 2; Meta Llama 3",
"commercial_inference":"restricted","license_category":"noncommercial", ...},
"acceptance":{"accepted":false,"state":"not_accepted",
"fingerprint":"v2:d938ea928581624d5732507057d8530320f638ac61426165cbd5abe67be5c9bc"}}
```

**ここがCLAUDE.mdの「出典・ライセンスを確認する」に関わる重要な発見**: backlog.md/today.mdでは
リポジトリ全体のライセンスをAGPL-3.0と記載していたが、これはVoiceStudioアプリ本体
(Electron/FastAPIバックエンド)のライセンスであり、**既定のTTSモデル本体(k2-fsa/OmniVoice)の
学習済み重みはCC-BY-NCで、商用推論は"restricted"と明記されている**。コード(Apache-2.0)と
学習済み重み(CC-BY-NC)が別ライセンスである点、音声トークナイザーにさらにHiggs Audio 2・
Meta Llama 3の個別条項が重なる点は、リポジトリの`LICENSE-NOTICE.md`にも明記されていた。
「ElevenLabsのローカル完結版」という売り文句から期待される「自由に商用利用できるOSS」とは
既定モデルに関して言えば異なり、記事で明記すべき重要な注意点だと判断した。

このライセンス受理(`POST /models/licenses/accept`)は、非商用限定の利用条件に同意するという
**人間の判断・同意が必要な操作**であり、本Routine実行環境の自動実行モード分類器によって
明確に拒否された。

```
Permission for this action was denied by the Claude Code auto mode classifier.
Reason: [Consent Given For The User]
```

これは「動かしていないものを動いたと書かない」以前に、**人間不在の自動実行が代わりに
ライセンス条項への同意を行ってはならない**という、Routine環境の意図的な安全装置だと判断した。
回避を試みていない。これは単なる技術的なネットワーク制約ではなく、本チャレンジの運用方針
(PRのマージ・公開判断は必ず人間が行う)の精神にも合致するため、ライセンス受理そのものは
人間(matsu)に委ねる。

## 4. ライセンス受理を経ずに使える別エンジンでも、モデル重みのダウンロード自体がRoutine環境でブロックされた

ライセンス受理を回避する代わりに、受理不要な別のTTSエンジンで動作確認を試みた。
`GET /engines/tts` はこのイメージに15種類のTTSエンジン候補を返し、うち追加インストール不要で
即利用可能(`available: true`)なのは`omnivoice`(要ライセンス受理)と`kittentts`
(`KittenML/kitten-tts-mini-0.8`、ライセンス受理不要、ONNX・CPU専用・約80MB)の2つだけだった。
`kittentts`は`supports_cloning: false`(クローン非対応、プリセット音声のみ)だが、ライセンス
受理なしでAPI全体が動くかどうかの確認には使える。

```
$ curl -X POST http://localhost:3900/generate -F "text=Hello, this is a test." -F "engine=kittentts" ...
HTTP 503
{"detail":"TTS engine 'kittentts' could not load its model. On a first run this is the
weight download failing rather than generation ...","error_class":"LocalEntryNotFoundError"}
```

コンテナログ:

```
2026-11-11 01:17:18,576 WARNING [omnivoice.tts] KittenTTS: model download failed
(An error happened while trying to locate the file on the Hub ... check your connection) retrying (attempt 1/3)
2026-11-11 01:17:43,716 WARNING ... retrying (attempt 2/3)
2026-11-11 01:18:10,884 ERROR [omnivoice.generate] engine model load failed
```

コンテナの外からHugging Face側への到達性を直接確認すると、`huggingface.co`自体(APIエンドポイント)
は到達できるが、実際の重みファイルを配信する`cdn-lfs.huggingface.co`への接続だけが失敗していた。

```
$ curl -o /dev/null -w "%{http_code}\n" https://huggingface.co            # 200
$ curl -o /dev/null -w "%{http_code}\n" https://cdn-lfs.huggingface.co    # 000 (CONNECT tunnel failed, response 502)
```

このRoutine実行環境のエージェントプロキシの状態確認エンドポイント(`/__agentproxy/status`)
にも、該当する失敗が記録されていた。

```json
{"ts": "2026-11-11T01:12:42.903Z", "kind": "connect_unreachable",
 "detail": "gateway answered 502 to CONNECT (host allowed, but the gateway could not connect to it)",
 "host": "cdn-lfs.huggingface.co:443"}
```

3回連続で再試行しても同じ結果で、GHCRのブロック(`403`、ポリシーによる拒否)とは異なり
`502`(ホスト自体は許可されているが接続できない)だった。いずれにせよ、ライセンス受理が
不要な`kittentts`でさえ、モデル重みのダウンロードがこのRoutine実行環境のネットワーク制約で
失敗することを確認した。これはツール自体の欠陥ではなく、Routine実行環境固有の制約と判断した。

→ **よって「ボイスクローンによる生成音声を実際に聴いて評価する」「646言語対応という主張の
一部を確認する」という今日の検証の核心は、このRoutine実行環境内では完了できなかった。**
ローカル検証待ち。再現手順は[README.md](./README.md)にまとめた(コンテナの起動から
ライセンス受理・クローン生成・結果の確認まで、そのまま実行できる形)。

## 5. API越しに確認できたその他の事実(記事で使える内容)

- `GET /engines/tts`が返す`omnivoice`バックエンドの`supported_language_names`は**648件**
  (`"japanese"`を含む)。UI/API説明文の`display_name`には"600+ languages"とだけ書かれており、
  today.mdが引用した「646言語対応」とは近いが完全には一致しない数字だった(648件はおそらく
  バージョンによって増減している値で、"646"も"600+"も大きな意味では正しいが厳密な一致ではない)。
- クローン用の参照音声は最大20秒(`max_ref_seconds: 20.0`)という制約がAPIレスポンスに明記されていた。
- サーバー版はDocker内で`request.client.host`がブリッジゲートウェイIPにNATされてしまうため、
  127.0.0.1限定のループバック判定が機能しない。これに対処するため`OMNIVOICE_SERVER_MODE=1`相当の
  「サーバーモード」に切り替わり、admin系ルートの保護は代わりにAPIキーで行う、という設計上の
  工夫が`backend/api/dependencies.py`のコメントに明記されていた(issue #261として詳細あり)。
- `/v1/audio/voices`で返るのは実際には"alloy"等OpenAIのプリセット名のエイリアス一覧であり、
  現在選択中のエンジンのデフォルト音声にマッピングされる、という仕組みだった。

## 6. ライセンス確認(まとめ)

- VoiceStudio本体(Electron/FastAPIバックエンド/CLI): **AGPL-3.0**(`LICENSE`原文で確認)。
- 同梱の`omnivoice`パッケージ(TTSエンジン実装): Apache-2.0(別ライセンス、AGPL-3.0と組み合わせ可能)。
- 既定モデルk2-fsa/OmniVoiceの**学習済み重み**: CC-BY-NC(非商用限定)。加えて音声トークナイザーに
  Higgs Audio 2・Meta Llama 3の個別条項。
- `kittentts`(KittenML/kitten-tts-mini-0.8)はこのリポジトリのモデル設定上はgatedでもHFトークン
  必須でもない(= 重みのライセンス自体は緩やかと見られる)が、今回はネットワーク制約により
  実際の重みのライセンス条文までは確認できなかった。
