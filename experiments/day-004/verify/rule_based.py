import re

# 単純なキーワールベース分類器(筆者自作)。
# 典型的な「よくあるルールベース実装」を模して、文中に出てくる単語を左から順に見ていき、
# 最初にヒットしたキーワードのカテゴリを採用する(カテゴリの優先順位ではなく、単語の出現順)。
KEYWORD_TO_LABEL = {
    "cancel": "cancellation", "canceled": "cancellation", "cancelled": "cancellation",
    "unsubscribe": "cancellation", "terminate": "cancellation", "membership": "cancellation",

    "package": "shipping", "delivery": "shipping", "delivered": "shipping",
    "shipping": "shipping", "shipped": "shipping", "tracking": "shipping",
    "transit": "shipping", "warehouse": "shipping", "delay": "shipping",

    "charge": "billing", "charged": "billing", "charges": "billing",
    "bill": "billing", "billing": "billing", "billed": "billing",
    "invoice": "billing", "refund": "billing", "payment": "billing", "pay": "billing",

    "crash": "technical", "crashes": "technical", "crashed": "technical",
    "error": "technical", "freeze": "technical", "freezes": "technical",
    "bug": "technical", "broken": "technical", "logged": "technical",
}

WORD_RE = re.compile(r"[a-zA-Z']+")


def classify(text: str) -> str | None:
    """文中の単語を出現順に見て、最初にキーワード辞書にヒットしたカテゴリを返す。
    1つもヒットしなければ None(分類不能)を返す。"""
    for word in WORD_RE.findall(text.lower()):
        label = KEYWORD_TO_LABEL.get(word)
        if label is not None:
            return label
    return None
