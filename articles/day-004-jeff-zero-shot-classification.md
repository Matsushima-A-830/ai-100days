---
title: "0.8Bのゼロショット分類モデル「Jeff」でキーワードルールベース分類を殴ってみた"
emoji: "🧮"
type: "tech"
topics: ["ai", "llm", "huggingface", "python", "classification"]
published: true
---

## これは何

海外AIネタ100日チャレンジ Day 004。今回取り上げるのは [Jeff](https://github.com/firelex/jeff)。
Qwen3.5-0.8B(0.8Bパラメータ)をファインチューンして作られた、**生成ではなく確率を返すゼロショット分類モデル**です。
重みは Hugging Face の [`mstrasser/Jeff-Qwen3.5-0.8B`](https://huggingface.co/mstrasser/Jeff-Qwen3.5-0.8B) で公開されています。

状況と選択肢を文章で渡すと、各選択肢の確率を1回の forward pass で返してくれる、というのがJeffのコンセプトです。
READMEの謳い文句は「27Bモデルの前にJeffを置いて、Jeffが自信を持てる決定は自分で片付け、迷ったときだけ27Bに回す」。
今回はその入り口として、**「文中の単語を見るだけの単純なキーワードルールベース分類器」と「Jeffのゼロショット分類」を、
筆者が自作した問い合わせメール分類タスクで実際に殴り合わせてみました。**

:::message
前日(2026-10-01)の検証では、このクラウド実行環境のネットワークポリシーで `huggingface.co` への
アクセスがブロックされており、モデル重みを一度もダウンロードできず検証未完了でした
([experiments/day-004/README.md](https://github.com/matsushima-a-830/ai-100days/blob/main/experiments/day-004/README.md)
に経緯を記録済み)。2026-10-02に環境のネットワーク設定が修正されたとの連絡を受けて再試行し、
今回は最後まで動かせています。
:::

## Jeffのここが面白い

ふつうのLLMに「これはbillingですか、technicalですか」と聞くと、生成されたテキストをパースして
意図を取り出す必要があります。Jeffは違っていて、choiceの選択肢ごとに確率を返す専用の「読み出しヘッド」
(`readout.safetensors`)を持っていて、**パース不要・1回の forward pass で確率分布が返ってくる**のが特徴です。

```python
from jeff import Client
from jeff.client import choice_question

jeff = Client("http://localhost:8765", model="jeff-latest")
answers = jeff.ask("The parcel arrived crushed and I want my money back.", {
    "team": choice_question({"refunds": "Refunds and payments", "parcels": "Damaged or lost parcels",
                             "login": "Account and login problems"}, "Which team should handle this ticket?"),
})
answers.choice("team").key    # "parcels"
```

0.8Bという小ささもあり、READMEのベンチマークではRTX PRO 6000で22ms/決定、CPUでも463ms/決定と謳われています
(筆者の実測は後述する通りもっと遅かったです)。

## 検証したこと

架空の問い合わせメール18件を、`billing`(請求・支払い)/`technical`(技術的な不具合)/
`cancellation`(解約・退会)/`shipping`(配送・荷物)の4カテゴリに分類するタスクを自作しました。
実在のデータではなく、すべて筆者が作った例文です。

- **easy(10件)**: 単純なキーワード一致でも素直に当たりそうな例。
- **adversarial(8件)**: わざと別カテゴリのキーワードを混ぜたり、否定文・皮肉を使ったりして、
  「文中に出てくる単語を見るだけ」のルールベース分類器が誤爆しやすいように作った意地悪な例。

adversarial群の例:

> Please cancel the duplicate charge on my card, I never asked for a second item.
> (正解: billing。"cancel" という単語が先に出てきますが、言いたいのは「請求を取り消してほしい」であって
> アカウント解約の話ではありません)

比較対象のルールベース分類器は、単語を文章の先頭から順に見ていき、最初にヒットしたキーワードの
カテゴリを採用するという、ありがちな実装です(`billing`なら charge/bill/invoice/refund/payment、
`technical`ならcrash/error/bug/broken、といった具合)。

## 実行環境・再現方法

```bash
pip install -U huggingface_hub transformers torch
hf download mstrasser/Jeff-Qwen3.5-0.8B --local-dir ./Jeff-Qwen3.5-0.8B   # 約1.79GB

git clone --depth 1 https://github.com/firelex/jeff.git && cd jeff
pip install --upgrade uv   # pyproject.tomlがuv>=0.12.19を要求するため
uv sync --no-default-groups --extra lora

JEFF_CHECKPOINT=/path/to/Jeff-Qwen3.5-0.8B PORT=8765 .venv/bin/jeff-serve
```

GPUなし・CPU4コアのクラウド実行環境です。詳細な再現手順と検証コード一式
(`dataset.py` / `rule_based.py` / `run_compare.py` / `jeff_client.py`)は
[experiments/day-004/](https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-004)
にすべて置いてあります。

## 結果

| | 全体精度(18件) | easy(10件) | adversarial(8件) | 平均レイテンシ |
|---|---:|---:|---:|---:|
| キーワードルールベース | 72.2%(13/18) | 100.0%(10/10) | **37.5%**(3/8) | 0.00 ms/件 |
| Jeff-Qwen3.5-0.8B(ゼロショット) | **94.4%**(17/18) | 100.0%(10/10) | **87.5%**(7/8) | 約1,500 ms/件 |

easyな例ではどちらも全問正解で差が出ませんでしたが、意地悪なadversarial群では
**ルールベースが37.5%まで精度が落ちたのに対し、Jeffは87.5%を維持**しました。
ルールベース分類器が間違えた5件はこんな感じです。

```
'Please cancel the duplicate charge on my card, I never asked for a second item.'
  true=billing pred=cancellation   ← "cancel"という単語だけを見て誤爆

"I don't want to cancel my account, I just want you to stop double-billing me every month."
  true=billing pred=cancellation   ← 「解約したくない」と明言しているのに"cancel"で誤爆

'The delivery was fine, but I was accidentally charged shipping fees twice for one order.'
  true=billing pred=shipping       ← "delivery"が先に出てくるが、本題は二重請求

'I tried to cancel my order before it shipped, but it looks like the package already left the warehouse.'
  true=shipping pred=cancellation  ← 本当の関心は「発送を止められるか」

"This isn't a complaint about the delay, it's about being charged a rush fee I never agreed to."
  true=billing pred=shipping       ← 「配送遅延の話ではない」と否定しているのに"delay"で誤爆
```

これらはすべて、文脈・否定・皮肉を扱えないキーワード一致の典型的な弱点です。

Jeffの唯一の誤分類は次の1件でした。

```
"Great, your app logged me out again right when I was about to pay my bill."
  true=technical pred=billing
  確率: billing=55.7%, technical=42.4%, cancellation=1.7%, shipping=0.1%
  confidence=0.409
```

正解できた例(例えば先頭の例)では billing=99.3% と一方的な確率になっていたのに対し、
唯一間違えたこの例ではbilling/technicalが僅差で、confidenceも0.409と低く出ていました。
**「自信なく間違えている」ことが確率分布から読み取れる**のは、0/1でしか答えないルールベースには
ない情報で、「確信度が低いときだけ人間や大きいモデルに回す」というJeffの想定用途の説得力を補強する結果でした。

### 速度については正直に

READMEはCPUで463ms/決定(32スレッド)と謳っていますが、今回のクラウド実行環境(GPUなし、CPU4コア)での
実測は約1,500ms/決定でした。1件ずつHTTPリクエストしてバッチ化していないこと、コア数が少ないことが
主な理由と考えられます。ルールベースの0msに比べればJeffは明確に遅く、**「速い」という売り文句は
このCPU環境ではそのまま成立しませんでした**。精度を取るか速度を取るかはユースケース次第、というのが
正直な感想です。

## ライセンス・出典

- コード: [github.com/firelex/jeff](https://github.com/firelex/jeff)(MITライセンス)
- モデル重み: [huggingface.co/mstrasser/Jeff-Qwen3.5-0.8B](https://huggingface.co/mstrasser/Jeff-Qwen3.5-0.8B)(Apache 2.0)
- 検証で使った問い合わせメール18件はすべて筆者の自作例文で、実在の顧客データではありません。

## まとめ

0.8Bという小さなモデルでも、「文脈・否定・皮肉を扱えるゼロショット分類」という点では
単純なキーワードルールベースを明確に上回ることを、自作の意地悪なテストケースで確認できました。
一方で速度面はこのCPU環境では謳い文句ほどには出ず、GPUやApple Silicon環境でこそ真価が出そうです。
次に試すなら、READMEにある9種類のLoRAアダプタ(`guard`/`triage`/`spam`など)を実際に読み込んで、
ベース単体との精度差を見てみたいと思います。
