---
title: "ElevenLabs代替を自称するOSS音声クローンを動かしたら、ライセンス以前に依存関係のバグで動かなかった"
emoji: "🎙️"
type: "tech"
topics: ["ai", "tts", "docker", "opensource", "voicecloning"]
published: false
---

## これは何を試した記事か

[debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio)(AGPL-3.0)は、「ElevenLabsのローカル完結版」を自称する音声スタジオである。
ボイスクローン・テキストからの声質デザイン・動画の吹き替え・文字起こしなどをひとつのローカル動作アプリでまとめて行え、646言語(API上は648言語)対応を謳っている。

筆者はこれをローカルPCでDocker起動し、実際にボイスクローンを生成して聴き比べる、というのが今日の検証の核心だった。
結論を先に書くと、**たどり着くまでに、ネットワークの問題でもライセンスの問題でもない、純粋にツール自体の依存関係のバグに遭遇した。** それを1行のパッチで回避してようやく音声が生成でき、実際に聴いた印象は「英語は同じ話者に聞こえるが、日本語は発音は自然でも、ネイティブぽさには欠ける」というものだった。

- 出典: https://github.com/debpalash/VoiceStudio (AGPL-3.0)
- 日本語記事件数(2026-11-10時点、Zenn/Qiita/note検索): 0件

## まずDockerで立ち上げる

公式が案内する既定の取得先はGHCR(GitHub Container Registry)だった。

```bash
docker pull ghcr.io/debpalash/voicestudio:stable
```

```bash
docker run -d --name omnivoice -p 127.0.0.1:3900:3900 \
  -e OMNIVOICE_API_KEY -e OMNIVOICE_DATA_DIR=/app/omnivoice_data \
  -v omnivoice-data:/app/omnivoice_data \
  ghcr.io/debpalash/voicestudio:stable
```

取得・起動は問題なかった。`curl http://localhost:3900/health`は`{"status":"ok","device":"cpu","version":"0.5.7"}`を返し、Electronのデスクトップアプリ前提のツールだが、実際にはOpenAI互換のREST APIも公開されているので、ブラウザもGUIも使わずcurlだけでボイスクローンまで完結できる設計だった。

## ライセンスは二重構造になっていた

既定の音声合成エンジン(`k2-fsa/OmniVoice`)を使うには、モデルのライセンス受理が必要だった。
VoiceStudio本体はAGPL-3.0だが、**既定モデルの学習済み重みは別ライセンス(CC-BY-NC、非商用限定)** で、商用推論は明示的に"restricted"とされている。

```json
{"license": "CC-BY-NC (version unspecified); Higgs Audio 2; Meta Llama 3",
 "commercial_inference": "restricted", "license_category": "noncommercial"}
```

「ElevenLabsのローカル完結版」という売り文句から素朴に期待する「自由に使えるOSS」とは、少なくとも既定モデルに関しては異なる。
さらに生成を進めると、音声トークナイザー(`eustlb/higgs-audio-v2-tokenizer`)についても別途ライセンス受理を求められた。
こちらは拍子抜けするような内容で、ライセンス自体が`NOASSERTION`——**アップストリームのHugging Face上でライセンスが明記されていない**、という状態だった。

この2つのライセンス受理は、個人の検証目的であることを確認した上で、人間が実際に内容を読んで同意する形で進めた。
AIエージェントが人間の代わりに利用規約へ同意する操作ではない。

## ライセンスを受理しても、別のバグで動かなかった

ライセンスを2件とも受理して、いよいよ`/generate`を呼んでみた。
返ってきたのは、ライセンスともネットワークとも関係ない、意外な結果だった。

```json
{"detail":"VoiceStudio hit an internal error; check the backend log for details.",
 "error_class":"NETWORK_ERROR","error_type":"OmniVoiceModelAssetError"}
```

コンテナのログを遡ると、本当の原因はこれだった。

```
TypeError: process() takes no keyword arguments
```

音声トークナイザーの設定ファイル(`config.json`)をHugging Faceからダウンロードする際、サーバーがBrotli圧縮(`Content-Encoding: br`)で応答し、それをイメージに同梱されたHTTPクライアント(`httpx2`というパッケージ)が解凍しようとした箇所で起きていた。

```python
# httpx2/_decoders.py
decompressed = self._decompress(data, output_buffer_limit=output_buffer_limit)
```

イメージに同梱されている`brotli`パッケージの実体を調べると、`Decompressor().process()`は単一の位置引数(`string`)しか受け付けないバージョンだった。

```
$ docker exec omnivoice python3 -c "import brotli; help(brotli.Decompressor().process)"
Signature: decompress(string)
```

**`httpx2`が前提とするBrotliパッケージのAPIと、イメージに実際に同梱されているBrotliパッケージのバージョンが食い違っていた。** 同じURLを手元で直接`curl -L`で叩くと問題なく取得できることからも、ネットワーク到達性の問題ではないことは確認済みだった。この不整合により、**Brotli圧縮で応答するHugging Face上のアセットを一つでも必要とすると、ダウンロードの時点で必ず失敗する**状態になっていた。`:stable`タグのこのイメージを素のまま使う限り、誰が試しても再現するはずの不具合である。

回避策は単純だった。該当ファイルの1行だけ、問題のキーワード引数を外して書き換え、コンテナを再起動する。

```bash
docker exec omnivoice sed -i \
  's/self._decompress(data, output_buffer_limit=output_buffer_limit)/self._decompress(data)/; \
   s/self._decompress(b"", output_buffer_limit=output_buffer_limit)/self._decompress(b"")/' \
  /opt/conda/lib/python3.11/site-packages/httpx2/_decoders.py
docker restart omnivoice
```

これで`POST /generate`が`200 OK`を返すようになった。

```
render trace {'total_seconds': 37.82,
  'stages': {'synthesis': {'seconds': 31.90}, 'watermark': {'seconds': 5.80}},
  'outcome': 'complete'}
```

## 実際にクローンした声を聴いてみる

同梱のデモ音声を参照音声として、英語・日本語・フランス語でクローン音声を生成した(いずれもCPU推論で約30〜38秒)。
生成した音声を、筆者(人間)が実際に聴いて評価した。

**英語**: 参照音声とは異なる文章を読ませても、「ほとんど同じ話者に聞こえた」。
話者の同一性は保たれていた。

**日本語**: 「話者は同じように思えるが、日本語に慣れている外国人の話す発音に近い雰囲気を感じ、日本語ネイティブぽさはあまり感じられなかった。ただ、問題なく聞き取れるくらい発音は自然だった。」
話者の同一性は維持されつつ、アクセントには英語話者由来と思われる訛りが残っている、という評価だった。

補足として、簡易な音響特徴(基本周波数・スペクトル重心)も機械的に比較した。

| | 平均基本周波数 | スペクトル重心(平均) |
|---|---|---|
| 参照音声 | 215.3 Hz | 1762 Hz |
| クローン(英語) | 204.6 Hz | 3243 Hz |
| クローン(日本語) | 222.8 Hz | 3038 Hz |

ピッチ(声の高さ)は3者とも近い値に収まっており、「同じ話者に聞こえる」という聴感評価と方向性は一致する。
一方でスペクトル重心(音色の明るさの目安)はクローン後の方がかなり高く出ており、ウォーターマーク処理や生成過程での音色変化が影響している可能性がある。
この数値だけで声質の同一性を判定できるわけではなく、あくまで人間の聴感評価を補足する参考情報である。

## 648言語対応という主張について

READMEやtoday.mdの調査メモでは「646言語対応」という数字が引用されていたが、実際にAPIから取得した対応言語リストは**648件**だった。
完全な一致ではないが近い値ではあり、バージョンによって増減する性質の数字と考えられる。
また、既定の`omnivoice`以外にも`cosyvoice`/`kittentts`/`mlx-audio`/`voxcpm2`等、合計18種類のTTSエンジンバックエンドがこのイメージに同梱されていることも分かった。

## ライセンス

- VoiceStudio本体(Electron/FastAPIバックエンド/CLI): AGPL-3.0。
- 同梱の`omnivoice`パッケージ(TTSエンジン実装): Apache-2.0。
- 既定モデル`k2-fsa/OmniVoice`の学習済み重み: CC-BY-NC(非商用限定)。
- 音声トークナイザー`eustlb/higgs-audio-v2-tokenizer`: `NOASSERTION`(ライセンス不明記)。

## まとめ

- Dockerイメージの取得・起動自体は問題なかった。
- 既定モデルのライセンスは、VoiceStudio本体(AGPL-3.0)とは別にCC-BY-NC(非商用限定)で、さらに音声トークナイザーにはライセンスが明記されていない("NOASSERTION")コンポーネントも含まれていた。
- ライセンス受理後も、イメージに同梱された`httpx2`と`brotli`パッケージのバージョン不整合により、Brotli圧縮で応答するHugging Face上のアセットのダウンロードが必ず失敗するという、ツール自体のバグに遭遇した。1行のパッチで回避し、実際の生成に到達した。
- 生成した英語のクローン音声は「ほとんど同じ話者」、日本語は「発音は自然だが、ネイティブぽさに欠ける」という評価だった。
- 648言語対応という主張は、today.md記載の646という数字とは完全一致しないが近い値として確認できた。

「ローカル完結のElevenLabs代替」という触れ込みを試す前に、ライセンスの構造を正しく理解し、依存関係のバグを1つ踏み越える必要があった。
動くところまでたどり着けば、ボイスクローンの基本的な実力(少なくとも話者の同一性)は確かに持っているツールだった。
