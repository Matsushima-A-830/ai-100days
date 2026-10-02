# Day 004 向けに筆者が自作した、問い合わせメール分類タスクのデータセット。
# 4カテゴリ: billing(請求・支払い) / technical(技術的な不具合) /
#            cancellation(解約・退会) / shipping(配送・荷物)
#
# "easy" はキーワールベース分類でも素直に当たる例。
# "adversarial" は、文中に別カテゴリのキーワードが混じっている・否定文・皮肉などで、
# 単純なキーワード一致ルールだと誤分類しやすいように筆者が意図して作った例
# (架空の問い合わせ文。実在の顧客データではない)。

EASY = [
    ("My credit card was charged twice for the same order, please refund the extra charge.", "billing"),
    ("The app crashes every time I open the settings menu.", "technical"),
    ("I want to cancel my subscription, I no longer need this service.", "cancellation"),
    ("My package has been stuck in transit for two weeks, where is my delivery?", "shipping"),
    ("Can you explain the charge of $49.99 on my latest invoice?", "billing"),
    ("The login page keeps giving me a 500 error.", "technical"),
    ("Please terminate my membership, I will not be renewing it.", "cancellation"),
    ("My tracking number shows delivered but I never received the package.", "shipping"),
    ("Why was I billed for a plan with a higher price than what I signed up for?", "billing"),
    ("Why does the mobile app freeze whenever I try to upload a photo?", "technical"),
]

ADVERSARIAL = [
    # 「cancel」という単語があるが、意図は請求の取り消し(billing)であって解約(cancellation)ではない
    ("Please cancel the duplicate charge on my card, I never asked for a second item.", "billing"),
    # 「cancel」と「billing」が両方出てくるが、本人は明確に解約を望んでいない
    ("I don't want to cancel my account, I just want you to stop double-billing me every month.", "billing"),
    # 「crashes」(technical)と「charged」(billing)が同居。根本原因は決済画面のクラッシュ=technical
    ("The checkout page crashes right before I can complete my payment, so I still haven't been charged correctly.",
     "technical"),
    # 「broken」(technical寄りの語)があるが、壊れていたのは商品で、問い合わせの主眼は返金(billing)
    ("My refund for the broken item hasn't shown up in my account yet.", "billing"),
    # 「delivery」「shipping」(shipping語)はあるが、実際の不満は二重請求(billing)
    ("The delivery was fine, but I was accidentally charged shipping fees twice for one order.", "billing"),
    # 「cancel」はあるが、本人の関心は出荷停止できるか(shipping)であって、アカウント解約ではない
    ("I tried to cancel my order before it shipped, but it looks like the package already left the warehouse.",
     "shipping"),
    # 皮肉("Great")+ログアウト(technical)+支払い(billing)の語が同居。根本原因はログイン不具合=technical
    ("Great, your app logged me out again right when I was about to pay my bill.", "technical"),
    # 否定文: 「配送遅延の話ではない」と明示しているのに shipping 語(delay)が出てくる。本題は手数料の請求=billing
    ("This isn't a complaint about the delay, it's about being charged a rush fee I never agreed to.", "billing"),
]

DATASET = [{"text": text, "true_label": label, "group": "easy"} for text, label in EASY] + \
          [{"text": text, "true_label": label, "group": "adversarial"} for text, label in ADVERSARIAL]

LABELS = {
    "billing": "Billing: charges, invoices, payments or refunds",
    "technical": "Technical: a bug, error, crash or something not working in the app or website",
    "cancellation": "Cancellation: closing the account or ending a subscription/membership",
    "shipping": "Shipping: a package, delivery or tracking issue",
}
