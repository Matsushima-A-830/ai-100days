# Day 027 検証結果: IQuestLab/IQuest-Q1

検証日: 2026-10-25
検証対象: https://huggingface.co/IQuestLab/IQuest-Q1 (論文: https://huggingface.co/papers/2610.30949 、コード: https://github.com/IQuestLab/IQuest-Q1)
検証時点のHugging Faceリポジトリの内容(`config.json`・`tokenizer.json`・`LICENSE`等)はすべて2026-10-25時点のもの。

## 0. 本体(320B/650GB)の実機推論は行っていない

today.md・backlog.mdに記載の通り、本体のsafetensors重みはBF16で約650GB、公式のデプロイ手順
(vLLM/SGLang)は`--tp-size 8`/`--tensor-parallel-size 8`を前提としており、8GPU構成が必要。
Hosted Inference ProviderやHugging Face Spaces上の無料デモも存在しない(モデルカードに
"This model isn't deployed by any Inference Provider."と表示される)。GGUF等の量子化版や
軽量デモも探したが見つからなかった(下記2参照)。

これは個人が6時間以内に手元で用意できる構成ではないため、**本体の実機推論("動かしてみた")は
行っていない。** 「動かしていないものを動いたと書かない」というCLAUDE.mdの原則に従い、本体推論の
結果は記事に書かない。一方で、ダウンロード可能な範囲(トークナイザ・config・LICENSEファイルなど、
数十KB〜十数MB程度の軽量ファイル)は実際に取得して動かし、以下の2〜4に記録する。

## 1. ライセンス条文の実機確認(backlog.mdの「未確認」を実際に確認した)

backlog.mdの時点では「Hugging Faceページには独自ライセンス『iquest-q1』の表記のみで条文の詳細・
商用利用可否は未確認」としていた。実際にリポジトリの`LICENSE`ファイル(1,318 bytes)を取得して
全文を読んだ。

```
$ python3.13 -c "
from huggingface_hub import hf_hub_download
p = hf_hub_download('IQuestLab/IQuest-Q1', 'LICENSE', local_dir='.')
print(p)
"
LICENSE downloaded to ./LICENSE in 0.16 s
```

全文(そのまま引用、`experiments/day-027/LICENSE`にも保存):

```
Modified MIT License

Software Copyright© 2026 IQuest Research

Our only modification is that, if the Software (or any derivative works
thereof) is used for any of your commercial products or services, you shall
prominently display "IQuest-Q1" on the user interface of such product or
service.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

**結論: MITライセンスに「商用利用時はUI上に"IQuest-Q1"の名前を目立つように表示する」という
1点だけを追加した、修正MITライセンス。商用利用は明確に許可されている。** 懸念されていたのは
ライセンスの不透明さではなく、実際に手元で動かす手段(軽量デモ・量子化版)が無いことだった。

## 2. 量子化版・軽量デモの有無の再確認

Hugging Face上のモデルカード、GitHubリポジトリ、Web検索で以下を確認した。

- Hosted Inference Provider: 無し(モデルカードに明記)。
- Hugging Face Spaces上のデモ: 見当たらなかった。
- GGUF等の量子化版: `IQuestLab`組織・関連リポジトリ・Web検索で確認したが、2026-10-25時点では
  公開されたGGUF量子化版は見つからなかった(README内の「llama.cpp向け」という記述は確認できたが、
  実際の量子化済みファイルの配布ページには到達できなかった)。

→ 軽量な代替手段は無いため、本体推論は今回もスコープ外とする。

## 3. ダウンロード可能な軽量ファイルの実機検証

`config.json`(1.6KB)・`tokenizer.json`(12.5MB)・`tokenizer_config.json`(92.7KB)・
`chat_template.jinja`(10.9KB)・`generation_config.json`(195 bytes)はGPU不要・数秒で
ダウンロードできるため、実際に取得して動かした。

```
$ python3.13 -c "
from huggingface_hub import list_repo_files
files = list_repo_files('IQuestLab/IQuest-Q1')
print('num files:', len(files))
"
num files: 190
```

### 3-1. アーキテクチャ設定(config.json)とモデルカードの記載の一致を確認

```json
{
  "num_hidden_layers": 88,
  "hidden_size": 3072,
  "num_attention_heads": 48,
  "num_key_value_heads": 8,
  "num_experts": 256,
  "num_experts_per_tok": 8,
  "vocab_size": 160000,
  "max_position_embeddings": 524288,
  "sliding_window": 4096,
  "hybrid_layers_types_block": ["full_attention", "sliding_attention", "sliding_attention", "sliding_attention"],
  "mlp_only_layers": [0]
}
```

論文(Table 1)・READMEに記載の「総パラメータ320B、active 15B、88層、hidden 3072、
コンテキスト524,288トークン、エキスパート256個中8個を活性化、最初のレイヤーのみdense FFN」
という記述と、実際にHugging Faceから取得した`config.json`の値は完全に一致した。

### 3-2. トークナイザを実際に動かし、vocab_sizeとJapanese対応を確認

```
$ python3.13 -c "
from tokenizers import Tokenizer
tok = Tokenizer.from_file('tokenizer.json')
print('vocab_size (tokenizer.json):', tok.get_vocab_size())
"
vocab_size (tokenizer.json): 160000
```

`config.json`の`vocab_size: 160000`と実際のトークナイザのvocabが一致することを確認した。

日本語・英語・Pythonコードの3種類のテキストで、実際にトークナイズしてトークン数を比較した
(比較対象はGPT-2の公開トークナイザ。日本語対応を重視していない旧世代の代表例として使用)。
スクリプト全文は`experiments/day-027/tokenizer_test.py`。

```
$ python3.13 tokenizer_test.py
sample            chars  iquest_tok  chars/tok  gpt2_tok  chars/tok
japanese_news        94          56       1.68       158       0.59
english_prose       188          32       5.88        32       5.88
python_code         145          59       2.46        81       1.79
```

日本語ニュース文(94文字)は、IQuest-Q1のトークナイザでは56トークン(1文字あたり1.68文字/トークン)
だったのに対し、GPT-2のトークナイザでは158トークン(0.59文字/トークン)かかった。
**同じ日本語テキストに対してGPT-2は約2.8倍のトークンを消費する**ことを実際に確認した。
英語の文章(188文字、意味内容はほぼ同じ)はどちらも32トークンで差が無かった一方、Pythonコード
(145文字)ではIQuest-Q1が59トークン、GPT-2が81トークンで、IQuest-Q1の方が約27%少ないトークン数
で表現できていた。IQuest-Q1の語彙設計(vocab_size 160,000、GPT-2の約3.2倍)が、日本語やコードの
トークナイズ効率に実際に効いていることを確認できた。

### 3-3. 特殊トークンにvision関連のプレースホルダが残っている

`tokenizer_config.json`の`additional_special_tokens`を実際に確認したところ、
`<|vision_start|>`・`<|vision_end|>`・`<|vision_pad|>`・`<|image_pad|>`・`<|video_pad|>`
といった画像・動画向けの特殊トークンが含まれていた。

```
$ python3.13 -c "
import json
cfg = json.load(open('tokenizer_config.json'))
print(cfg['additional_special_tokens'])
"
['<|im_start|>', '<|iquest_end|>', '<|object_ref_start|>', '<|object_ref_end|>',
 '<|box_start|>', '<|box_end|>', '<|quad_start|>', '<|quad_end|>', '<|vision_start|>',
 '<|vision_end|>', '<|vision_pad|>', '<|image_pad|>', '<|video_pad|>', '<|iquest_system|>',
 '<|iquest_user|>', '<|iquest_assistant|>', '<|iquest_tool|>', '<|iquest_developer|>']
```

README・モデルカードには「テキスト入力のみ対応」と明記されているため、これらのvision系トークンは
使われていない(ベースとなったトークナイザ資産を再利用した結果の残骸と見られる)。実害はないが、
「テキスト専用」という説明と語彙の実態には小さなギャップがあることを実際に確認した。

### 3-4. eos/pad トークンの整合性確認

```
$ python3.13 -c "
from tokenizers import Tokenizer
tok = Tokenizer.from_file('tokenizer.json')
print('id 0 ->', tok.id_to_token(0))
"
id 0 -> <|iquest_end|>
```

`config.json`の`eos_token_id: 0`、`tokenizer_config.json`の`eos_token`/`pad_token`が
いずれも`<|iquest_end|>`を指しており、実際のトークナイザのid 0もこのトークンだった。表記上の
矛盾は見つからなかった。

## 4. ベンチマーク数値(論文より、未検証・引用のみ)

以下はHugging Face Papers掲載の論文本文の表から引用した数値で、**筆者が実行して確認したものではない。**
著者ら自身の報告値であることに注意。

| モデル | 種別 | SWE-Bench Pro | Terminal-Bench 2.1 | CyberGym | SWE-bench Multilingual | Humanity's Last Exam(ツールなし) |
|---|---|---|---|---|---|---|
| IQuest-Q1 | 自社モデル | 57.5 | 83.2 | 84.5 | 80.3 | 39.2 |
| GLM-5.3 Flash | OSSベースライン | 59.4* | 84.3 | 81.6* | 79.7* | 39.9 |
| DeepSeek-V4-Flash-0731 | OSSベースライン | 57.3* | 82.7 | 76.7 | 78.7* | 38.6 |
| Tencent Hy3 | OSSベースライン | 57.9 | 71.7 | 51.8 | 75.8 | 33.5 |
| MiniMax M3 | OSSベースライン | 59.0 | 66.0 | 40.3* | 75.0* | 39.0 |
| Claude Opus-5 | 独自モデル | 79.2 | 89.1 | – | 89.5 | 54.9 |
| GPT-5.6 Sol | 独自モデル | 64.6 | 88.8 | 83.6 | 74.1 | 49.5 |

(`*`は論文の著者らによる独自評価、`–`は論文中に数値の記載が無いことを示す。)

論文の数値を見る限り、IQuest-Q1は同規模オープンモデル(GLM-5.3 Flash・DeepSeek-V4-Flash等)と
概ね同水準で、CyberGym(サイバーセキュリティ系タスク)ではGPT-5.6 Solを含む比較対象の中で最高値
(84.5)を報告している。一方Humanity's Last Exam(ツールなし、汎用推論)はClaude Opus-5・
GPT-5.6 Solに対して明確に下回っている(39.2 対 54.9/49.5)。これらは論文の報告値であり、
筆者自身は再現していない。

## まとめ

- 本体(320B、650GB、8GPU前提)の実機推論: **未実施**(個人が6時間以内に用意できる構成ではないため)。
- ライセンス: **実際にLICENSEファイルを取得して全文を確認した。** 修正MITライセンス(商用利用可、
  UI表示義務のみ)で、backlog.md時点の「条文未確認」という懸念は解消された。
- トークナイザ: **実際にダウンロードして動かした。** vocab_size 160,000がconfig.jsonの記載と一致し、
  日本語テキストでGPT-2比約2.8倍のトークン効率、Pythonコードで約27%少ないトークン数を確認した。
  一方、テキスト専用と説明されているにもかかわらずvision系の特殊トークンが語彙に残っている点も確認した。
  config.jsonのアーキテクチャ設定(88層・256エキスパート等)は論文・READMEの記載と完全に一致した。
  eos/padトークンの整合性にも矛盾は無かった。
  これらは実際にファイルを取得しコードを実行して得た結果であり、推測ではない。
- ベンチマーク数値: 論文からの引用のみで、筆者による再現実行は行っていない。
