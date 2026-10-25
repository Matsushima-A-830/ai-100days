---
title: "320BのエージェントCLIモデルIQuest-Q1は動かせなかったが、ライセンスとトークナイザは実際に確認できた"
emoji: "🧮"
type: "tech"
topics: ["ai", "llm", "huggingface", "tokenizer", "license"]
published: false
---

Hugging Face Daily Papersに上位掲載されていた「IQuest-Q1」という疎MoE基盤モデルを調べた。総パラメータ320B、コンテキスト524,288トークンで、ソフトウェア開発やサイバーセキュリティ系のエージェント作業に重点を置いたモデルだという。

結論を先に書く。**このモデル本体は今回、実機で動かしていない。** BF16重みは約650GB、公式のデプロイ手順はvLLM/SGLangで8GPU構成(`--tp-size 8`)を前提にしており、個人が6時間以内に手元で用意できる規模ではなかった。無料のHosted Inference ProviderやHugging Face Spacesのデモも存在しない。「動かしていないものを動いたと書かない」という方針のもと、本体の推論結果は書かない。

一方で、手元でダウンロードして実際に動かせる部分——ライセンス全文とトークナイザ——はきちんと検証した。この記事はその内容が中心になる。

## 出典

- 論文(Hugging Face Papers): https://huggingface.co/papers/2610.30949
- モデル: https://huggingface.co/IQuestLab/IQuest-Q1
- コード: https://github.com/IQuestLab/IQuest-Q1

## ライセンス: 「独自ライセンスで条文不明」ではなく、修正MITだった

候補を選ぶ時点でのメモには「Hugging Faceページにはライセンス名『iquest-q1』の表記のみで、商用利用可否等の条文詳細は未確認」と書いていた。これは実際に`LICENSE`ファイルを取得していなかったために生じた不確実性だったので、まず実物を取得して読んだ。

```bash
python3 -c "
from huggingface_hub import hf_hub_download
p = hf_hub_download('IQuestLab/IQuest-Q1', 'LICENSE', local_dir='.')
print(p)
"
```

```
LICENSE downloaded to ./LICENSE in 0.16 s
```

取得した全文(1,318 bytes)を読むと、**MITライセンスに1点だけ追加した「修正MITライセンス」** だった。追加条件は以下の一文のみ。

> if the Software (or any derivative works thereof) is used for any of your commercial products or services, you shall prominently display "IQuest-Q1" on the user interface of such product or service.

つまり商用利用そのものは明確に許可されており、唯一の制約は商用の製品・サービスのUI上に"IQuest-Q1"という名前を表示することだけだった。「ライセンスが不透明で商用利用できるか分からない」という事前の懸念は、実物を読んだことで解消された。このモデルを検証できなかった本当の理由は、ライセンスではなく「650GB・8GPU構成を個人が用意できない」という物理的な制約の方だった。

## トークナイザは実際にダウンロードして動かせた

本体の重みは無理でも、`tokenizer.json`(12.5MB)や`config.json`(1.6KB)はGPUも不要で数秒でダウンロードできる。`huggingface_hub`経由でリポジトリのファイル一覧を取ると190ファイルあり、このうち軽量なものだけを実際に取得した。

```bash
python3 -c "
from huggingface_hub import list_repo_files
print('num files:', len(list_repo_files('IQuestLab/IQuest-Q1')))
"
```

```
num files: 190
```

まず`config.json`の値が、論文・READMEに書かれているアーキテクチャの記述(総パラメータ320B・active 15B・88層・エキスパート256個中8個を活性化・コンテキスト524,288トークン)と一致するかを確認した。

```json
{
  "num_hidden_layers": 88,
  "hidden_size": 3072,
  "num_experts": 256,
  "num_experts_per_tok": 8,
  "vocab_size": 160000,
  "max_position_embeddings": 524288,
  "mlp_only_layers": [0]
}
```

実際に取得した設定ファイルの数値は、論文・READMEの記述と完全に一致していた。ここは「書いてあることと配布物が一致しているか」を実際にファイルを取って確認した部分になる。

## 日本語テキストでGPT-2比約2.8倍のトークン効率

次に、`tokenizers`ライブラリで`tokenizer.json`を実際にロードし、トークナイズを実行した。比較対象には日本語対応を重視していない旧世代の代表としてGPT-2のトークナイザ(`tokenizers.Tokenizer.from_pretrained("gpt2")`)を使った。

```python
from tokenizers import Tokenizer

iquest = Tokenizer.from_file("tokenizer.json")
gpt2 = Tokenizer.from_pretrained("gpt2")

text = "経済産業省は25日、国内の半導体関連企業に対する新たな補助金制度の詳細を発表した。..."
print(len(iquest.encode(text).ids), len(gpt2.encode(text).ids))
```

94文字の日本語ニュース文に対する実行結果:

```
sample            chars  iquest_tok  chars/tok  gpt2_tok  chars/tok
japanese_news        94          56       1.68       158       0.59
english_prose       188          32       5.88        32       5.88
python_code         145          59       2.46        81       1.79
```

同じ日本語テキストに対して、IQuest-Q1は56トークン、GPT-2は158トークンを要した。**GPT-2は同じ内容に約2.8倍のトークンを消費する**ことを実際に確認した。英語の文章(同じ意味内容)ではトークン数に差が無かった一方、Pythonコードでも IQuest-Q1 の方が約27%少ないトークン数で表現できていた。vocab_sizeが160,000(GPT-2の約3.2倍)あることが、日本語やコードのトークナイズ効率に実際に効いていることが分かった。

ついでに`tokenizer_config.json`の特殊トークン一覧も見てみると、`<|vision_start|>`・`<|image_pad|>`・`<|video_pad|>`といった画像・動画向けのプレースホルダトークンが残っていた。READMEには「テキスト入力のみ対応」と明記されているため、これらは使われていないはずだが、ベースにした語彙資産の名残がそのまま残っている状態だった。実害のある話ではないが、「テキスト専用」という説明と語彙の実態には小さなギャップがある。

## ベンチマーク数値(引用のみ、筆者による再現実行なし)

論文(Hugging Face Papers)に掲載されている表の数値を引用する。これは著者ら自身の報告値で、筆者が実行して確認したものではないことを明記しておく。

| モデル | 種別 | SWE-Bench Pro | Terminal-Bench 2.1 | CyberGym | Humanity's Last Exam(ツールなし) |
|---|---|---|---|---|---|
| IQuest-Q1 | 自社モデル | 57.5 | 83.2 | **84.5** | 39.2 |
| GLM-5.3 Flash | OSSベースライン | 59.4* | 84.3 | 81.6* | 39.9 |
| DeepSeek-V4-Flash-0731 | OSSベースライン | 57.3* | 82.7 | 76.7 | 38.6 |
| Claude Opus-5 | 独自モデル | 79.2 | 89.1 | – | 54.9 |
| GPT-5.6 Sol | 独自モデル | 64.6 | 88.8 | 83.6 | 49.5 |

(`*`は論文著者自身による評価、`–`は記載無し)

論文の数値だけを見ると、同規模のオープンモデル群とはおおむね同水準で、サイバーセキュリティ系タスクのCyberGymでは比較対象の中で最高値を報告している。一方、汎用推論のHumanity's Last Examでは、Claude Opus-5やGPT-5.6 Solのような独自モデルに対して明確に差がある。繰り返しになるが、これは論文の報告値であり筆者自身が再現したものではない。

## まとめ

- 本体(320B、650GB、8GPU前提)の実機推論: 用意できる環境がなく未実施。
- ライセンス: 実際にファイルを取得して全文を読んだ。修正MITで商用利用可(UI表示義務のみ)。事前の「条文不明」という懸念は解消された。
- トークナイザ: 実際にダウンロードして動かした。config.jsonの記載と完全一致、日本語でGPT-2比約2.8倍のトークン効率、ただしテキスト専用のはずの語彙にvision系トークンが残る、という3点を確認できた。
- ベンチマーク数値: 論文からの引用のみ。

「本体を動かせなかった日」ではあるが、動かせる範囲の実物(ライセンス・トークナイザ)をちゃんと手元で確認すると、backlog.md時点の推測とは違う発見(ライセンスは明確、トークナイザは実際に効率が良い)があった。
