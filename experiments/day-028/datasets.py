"""
Day 028 検証用の自作・架空の会話ログ。

元論文 (arXiv:2610.30755) の LoCoMo / LongMemEval 等は使わず、
3人の架空の人物についての長期会話ログを自分で書き起こした。
各人物は「住んでいる都市」「職業」「ペット」「好きな食べ物」の4項目について、
会話が進むにつれて設定が変化していく(引っ越し・転職・ペットが増える・好みが変わる、等)。
途中に関係ない世間話のターンも混ぜて、検索(RAG)が自明すぎないようにしている。

各会話は turns (発言のリスト) と、何ターン目でどの項目がどの値に「更新」されたかを示す
updates のメタ情報を持つ。updates はこのスクリプト側の採点用の正解データであり、
メモリ手法自身には渡さない。
"""

CONVERSATIONS = [
    {
        "id": "conv_001_aki",
        "person": "Aki",
        "turns": [
            (1, "Aki", "Hi! I just wanted to say I'm really happy with the new coffee machine at the office."),
            (2, "Bot", "Glad to hear that! How has work been otherwise?"),
            (3, "Aki", "Work is good. I live in Osaka now and I commute by train every day."),
            (4, "Bot", "Osaka is a great city. What do you do for work?"),
            (5, "Aki", "I work as a graphic designer at a small studio downtown."),
            (6, "Bot", "That sounds creative. Do you have any pets?"),
            (7, "Aki", "Yes, I have a cat named Mochi. She's very lazy."),
            (8, "Bot", "Cats are the best. What's your favorite food?"),
            (9, "Aki", "My favorite food is ramen, especially tonkotsu ramen."),
            (10, "Bot", "Nice choice. Any weekend plans?"),
            (11, "Aki", "Just relaxing at home with Mochi, probably."),
            (12, "Bot", "Sounds peaceful."),
            (13, "Aki", "By the way, big update: I moved to Fukuoka last month for a new job."),
            (14, "Bot", "Oh wow, how's Fukuoka treating you?"),
            (15, "Aki", "It's nice, much more relaxed than Osaka. I'm now working as a UX researcher at a startup."),
            (16, "Bot", "That's a big career shift from graphic design. Congrats!"),
            (17, "Aki", "Thanks! Also Mochi got a new friend, we adopted a second cat named Tofu."),
            (18, "Bot", "Two cats now, that's wonderful."),
            (19, "Aki", "And honestly my tastes changed too, these days I actually prefer udon over ramen."),
            (20, "Bot", "Good to know. Anything else new?"),
            (21, "Aki", "Not really, just settling into the new place."),
            (22, "Bot", "Take your time."),
            (23, "Aki", "One more thing, I switched jobs again, I'm now a product manager at a bigger company in Fukuoka."),
            (24, "Bot", "That's quick! Congrats on the promotion-ish move."),
            (25, "Aki", "Thanks, it's a step up for sure."),
        ],
        "facts": {
            "home_city": [
                {"value": "Osaka", "turn": 3},
                {"value": "Fukuoka", "turn": 13},
            ],
            "job": [
                {"value": "graphic designer", "turn": 5},
                {"value": "UX researcher", "turn": 15},
                {"value": "product manager", "turn": 23},
            ],
            "pet": [
                {"value": "a cat named Mochi", "turn": 7},
                {"value": "two cats, Mochi and Tofu", "turn": 17},
            ],
            "favorite_food": [
                {"value": "tonkotsu ramen", "turn": 9},
                {"value": "udon", "turn": 19},
            ],
        },
    },
    {
        "id": "conv_002_ben",
        "person": "Ben",
        "turns": [
            (1, "Ben", "Hey, quick life update, I live in Seattle these days."),
            (2, "Bot", "Seattle! Nice. What keeps you busy there?"),
            (3, "Ben", "I'm a backend engineer at a logistics company."),
            (4, "Bot", "Cool. Any pets?"),
            (5, "Ben", "I have a dog named Biscuit, a golden retriever."),
            (6, "Bot", "Golden retrievers are so friendly. Favorite food?"),
            (7, "Ben", "Honestly I could eat pizza every day."),
            (8, "Bot", "Classic choice. How's the weather been?"),
            (9, "Ben", "Rainy as always, typical Seattle."),
            (10, "Bot", "Haha, makes sense."),
            (11, "Ben", "I actually got a new job offer and moved to Austin last week."),
            (12, "Bot", "Big move! How is Austin so far?"),
            (13, "Ben", "It's hot but I like it. I'm now a backend engineer at a fintech startup."),
            (14, "Bot", "Same role, new domain, nice."),
            (15, "Ben", "Biscuit came with me of course, he loves the backyard here."),
            (16, "Bot", "Glad he's adjusting well."),
            (17, "Ben", "Also I've been trying to eat healthier, so lately my favorite food is actually grilled salmon."),
            (18, "Bot", "That's a big shift from pizza every day!"),
            (19, "Ben", "Yeah, trying to be better about it."),
            (20, "Bot", "Good for you."),
            (21, "Ben", "Oh and one more change, I switched teams, now I'm doing data engineering instead of backend."),
            (22, "Bot", "Interesting pivot."),
            (23, "Ben", "Yeah I wanted to try something new."),
        ],
        "facts": {
            "home_city": [
                {"value": "Seattle", "turn": 1},
                {"value": "Austin", "turn": 11},
            ],
            "job": [
                {"value": "backend engineer at a logistics company", "turn": 3},
                {"value": "backend engineer at a fintech startup", "turn": 13},
                {"value": "data engineer", "turn": 21},
            ],
            "pet": [
                {"value": "a dog named Biscuit", "turn": 5},
            ],
            "favorite_food": [
                {"value": "pizza", "turn": 7},
                {"value": "grilled salmon", "turn": 17},
            ],
        },
    },
    {
        "id": "conv_003_chi",
        "person": "Chi",
        "turns": [
            (1, "Chi", "So I live in Toronto, been here for a few years."),
            (2, "Bot", "Nice, how do you like it?"),
            (3, "Chi", "It's good. I'm a nurse at a downtown hospital."),
            (4, "Bot", "That must be demanding work. Any pets at home?"),
            (5, "Chi", "I have a rabbit named Pudding."),
            (6, "Bot", "A rabbit, that's unusual and cute. Favorite food?"),
            (7, "Chi", "I really love sushi, I eat it at least once a week."),
            (8, "Bot", "Great choice. Anything fun planned?"),
            (9, "Chi", "Just work mostly, it's been a busy season."),
            (10, "Bot", "Take care of yourself."),
            (11, "Chi", "Thanks. Update: I relocated to Vancouver for a new hospital position."),
            (12, "Bot", "Oh nice, new city! Same field?"),
            (13, "Chi", "Yes, still a nurse, but now specializing in pediatrics."),
            (14, "Bot", "That's a meaningful specialty."),
            (15, "Chi", "Pudding is doing fine, adjusted to the new apartment quickly."),
            (16, "Bot", "Glad to hear it."),
            (17, "Chi", "Also we got a second rabbit, named Waffle, so Pudding has a friend now."),
            (18, "Bot", "Two rabbits! Lovely."),
            (19, "Chi", "My food tastes are the same honestly, still sushi all the way."),
            (20, "Bot", "Consistency is nice."),
        ],
        "facts": {
            "home_city": [
                {"value": "Toronto", "turn": 1},
                {"value": "Vancouver", "turn": 11},
            ],
            "job": [
                {"value": "nurse at a downtown hospital", "turn": 3},
                {"value": "pediatric nurse", "turn": 13},
            ],
            "pet": [
                {"value": "a rabbit named Pudding", "turn": 5},
                {"value": "two rabbits, Pudding and Waffle", "turn": 17},
            ],
            "favorite_food": [
                {"value": "sushi", "turn": 7},
            ],
        },
    },
]

# 採点用の質問セット。
# type="current": 最新の値を聞く質問(どのメモリ手法でも答えられるはず)。
# type="historical": 既に上書き・変更された過去の値を聞く質問
#   (素朴なRaw-RAG・追記のみメモリは生ログ/履歴から答えられる可能性があるが、
#    上書き型の変異メモリは失う可能性がある、というのが論文の指摘の核心部分)。
QUESTIONS = []
for conv in CONVERSATIONS:
    cid = conv["id"]
    for category, history in conv["facts"].items():
        latest = history[-1]
        QUESTIONS.append({
            "conv_id": cid,
            "category": category,
            "type": "current",
            "question": f"Where/what is {conv['person']}'s current {category.replace('_', ' ')}?"
            if category != "home_city"
            else f"What city does {conv['person']} currently live in?",
            "gold": latest["value"],
        })
        if len(history) >= 2:
            # 最新より前の値を1つ、過去の値として問う(最新ではないものすべてを候補にする)
            for old in history[:-1]:
                QUESTIONS.append({
                    "conv_id": cid,
                    "category": category,
                    "type": "historical",
                    "question": f"What was {conv['person']}'s {category.replace('_', ' ')} *before* the most recent change?",
                    "gold": old["value"],
                })
