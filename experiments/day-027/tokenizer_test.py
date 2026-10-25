from tokenizers import Tokenizer

iquest = Tokenizer.from_file('tokenizer.json')
gpt2 = Tokenizer.from_pretrained('gpt2')

samples = {
    "japanese_news": "経済産業省は25日、国内の半導体関連企業に対する新たな補助金制度の詳細を発表した。対象となるのは先端ロジック半導体の国内生産を手掛ける企業で、投資額に応じて最大で費用の三分の一を補助する。",
    "english_prose": "The Ministry of Economy announced new subsidy details for domestic semiconductor manufacturers on the 25th, covering up to one third of investment costs for advanced logic chip production.",
    "python_code": "def fibonacci(n: int) -> int:\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n",
}

print(f"{'sample':16s} {'chars':>6s} {'iquest_tok':>11s} {'chars/tok':>10s} {'gpt2_tok':>9s} {'chars/tok':>10s}")
for name, text in samples.items():
    n_chars = len(text)
    n_iq = len(iquest.encode(text).ids)
    n_gpt2 = len(gpt2.encode(text).ids)
    print(f"{name:16s} {n_chars:6d} {n_iq:11d} {n_chars/n_iq:10.2f} {n_gpt2:9d} {n_chars/n_gpt2:10.2f}")
