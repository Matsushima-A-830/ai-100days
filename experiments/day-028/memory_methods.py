"""
Day 028: 3種類のメモリ手法を、外部APIキー・GPUなしで実装する。

論文 (arXiv:2610.30755) が比較している構図を、小規模な自作データで模す:

1. MutatingSummaryMemory
   - LLMによる抽出・要約を、ここでは正規表現ベースの簡易抽出で代替した(本物のLLM抽出ではない
     という限界を results.md に明記する)。
   - 新しい発言が既存の項目(住んでいる都市・職業・ペット・好きな食べ物)と矛盾する場合、
     古い値を「上書き」する。これは論文が検証しているMem0のUPDATE/DELETE操作を模している。

2. AppendOnlyMemory
   - 抽出ロジックはMutatingSummaryMemoryと同じだが、矛盾があっても古い値を消さず、
     履歴としてすべて保持し続ける(論文のMem0 UPDATE/DELETE→追記のみ、という実験に相当)。

3. RawRAGMemory
   - 抽出・要約を一切行わず、生の発言をそのまま保持する。
   - 質問が来たら、自作の軽量TF-IDF類似度(外部ライブラリ不使用)で関連する発言を検索する。
   - 論文の「密検索+クロスエンコーダ再ランキング」をTF-IDFのみに簡略化している(クロス
     エンコーダ相当の再ランキングは行っていない)点も限界として正直に記録する。
"""
import math
import re
import time
from collections import Counter, defaultdict


# ---------- 共通の抽出ルール(簡易・正規表現ベース) ----------

def extract_fact(category, text):
    """1ターンのテキストから、指定カテゴリの値を正規表現で抽出する。見つからなければNone。"""
    t = text.strip()

    if category == "home_city":
        m = re.search(r"(?:live(?:s|d)? in|moved to|relocated to)\s+([A-Z][a-zA-Z]+)", t)
        if m:
            return m.group(1)

    elif category == "job":
        m = re.search(
            r"(?:work(?:ing)? as a|now a|i'?m a|i am a)\s+([a-zA-Z][a-zA-Z ]+?)"
            r"(?=\s+at\b|\s+instead\b|\.|,|$)",
            t,
            re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()
        m2 = re.search(r"now specializing in\s+([a-zA-Z]+)", t, re.IGNORECASE)
        if m2:
            return m2.group(1).strip() + " specialist"
        m3 = re.search(r"now doing ([a-zA-Z ]+?) instead of", t, re.IGNORECASE)
        if m3:
            return m3.group(1).strip()

    elif category == "pet":
        m = re.search(r"second (cat|dog|rabbit),?\s*named\s+([A-Za-z]+)", t, re.IGNORECASE)
        if m:
            return ("second", m.group(1).lower(), m.group(2))
        m2 = re.search(r"\ba (cat|dog|rabbit) named ([A-Za-z]+)", t, re.IGNORECASE)
        if m2:
            return ("first", m2.group(1).lower(), m2.group(2))

    elif category == "favorite_food":
        patterns = [
            r"favorite food is (?:actually )?([a-zA-Z][a-zA-Z ]+?)(?:\.|,|$)",
            r"prefer ([a-zA-Z][a-zA-Z ]+?) over",
            r"really love ([a-zA-Z][a-zA-Z ]+?),",
            r"could eat ([a-zA-Z][a-zA-Z ]+?) every day",
            r"still ([a-zA-Z]+) all the way",
        ]
        for p in patterns:
            m = re.search(p, t, re.IGNORECASE)
            if m:
                return m.group(1).strip()

    return None


def format_pet_value(pet_state):
    """pet_state: list of (species, name) in the order they were acquired."""
    if not pet_state:
        return None
    if len(pet_state) == 1:
        species, name = pet_state[0]
        return f"a {species} named {name}"
    number_words = {2: "two", 3: "three", 4: "four"}
    n = len(pet_state)
    species = pet_state[0][0]
    names = ", ".join(name for _, name in pet_state)
    return f"{number_words.get(n, str(n))} {species}s, {names}"


def process_conversation_facts(turns):
    """
    全ターンを順に処理し、各カテゴリについて
    (a) 上書き方式の最終値 mutated,
    (b) 追記方式の履歴リスト appended_history
    を返す。pet は複数ペットの合成が必要なので専用に処理する。
    """
    categories = ["home_city", "job", "favorite_food"]
    mutated = {c: None for c in categories}
    appended_history = {c: [] for c in categories}
    pet_state = []
    pet_history = []

    for turn_id, speaker, text in turns:
        for c in categories:
            val = extract_fact(c, text)
            if val:
                mutated[c] = val
                appended_history[c].append((turn_id, val))

        pet_fact = extract_fact("pet", text)
        if pet_fact:
            order, species, name = pet_fact
            if order == "first" and not pet_state:
                pet_state.append((species, name))
            elif order == "second":
                pet_state.append((species, name))
            formatted = format_pet_value(pet_state)
            pet_history.append((turn_id, formatted))

    mutated["pet"] = pet_history[-1][1] if pet_history else None
    appended_history["pet"] = pet_history
    return mutated, appended_history


# ---------- MutatingSummaryMemory / AppendOnlyMemory ----------

class MutatingSummaryMemory:
    """抽出した事実を上書き(UPDATE/DELETE相当)で保持する、要約・変異型メモリの簡易模倣。"""

    def __init__(self, turns):
        t0 = time.perf_counter()
        self.mutated, _ = process_conversation_facts(turns)
        self.build_time = time.perf_counter() - t0
        self.storage_chars = sum(len(str(v)) for v in self.mutated.values() if v)

    def answer(self, category, question_type):
        return self.mutated.get(category)


class AppendOnlyMemory:
    """抽出した事実を削除せず全履歴として保持する、追記のみ版。"""

    def __init__(self, turns):
        t0 = time.perf_counter()
        _, self.history = process_conversation_facts(turns)
        self.build_time = time.perf_counter() - t0
        self.storage_chars = sum(
            len(str(v)) for hist in self.history.values() for (_, v) in hist if v
        )

    def answer(self, category, question_type):
        hist = self.history.get(category, [])
        if not hist:
            return None
        if question_type == "current":
            return hist[-1][1]
        # historical: 最新以外の値をすべて候補として返す(複数ある場合はリストで返す)
        return [v for (_, v) in hist[:-1]]


# ---------- RawRAGMemory (TF-IDF検索のみ、要約なし) ----------

_WORD_RE = re.compile(r"[a-zA-Z]+")

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "where", "who",
    "do", "does", "did", "i", "you", "your", "s", "to", "of", "for", "in",
    "on", "at", "and", "or", "it", "this", "that", "my", "me", "be",
}


def _stem(word):
    # ごく簡易な語尾処理(ing/ed/s を削るだけ)。NLTK等は使わず自作。
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokenize(text, include_stopwords=True, stem=False):
    words = [w.lower() for w in _WORD_RE.findall(text)]
    if not include_stopwords:
        words = [w for w in words if w not in _STOPWORDS]
    if stem:
        words = [_stem(w) for w in words]
    return words


class RawRAGMemory:
    """生ログをそのまま保持し、質問時に自作の軽量TF-IDF類似度で関連ターンを検索する。"""

    def __init__(self, turns, top_k=5, include_speaker=True, stem=False):
        t0 = time.perf_counter()
        self.turns = turns
        self.top_k = top_k
        self.stem = stem
        self.docs = [
            _tokenize(f"{speaker}: {text}" if include_speaker else text, stem=stem)
            for (_, speaker, text) in turns
        ]
        self.storage_chars = sum(len(text) for (_, _, text) in turns)

        n_docs = len(self.docs)
        df = Counter()
        for doc in self.docs:
            for term in set(doc):
                df[term] += 1
        self.idf = {term: math.log(n_docs / df[term]) + 1.0 for term in df}

        self.doc_vectors = [self._vectorize(doc) for doc in self.docs]
        self.build_time = time.perf_counter() - t0

    def _vectorize(self, tokens):
        tf = Counter(tokens)
        vec = {}
        for term, count in tf.items():
            if term in self.idf:
                vec[term] = count * self.idf[term]
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        return {term: w / norm for term, w in vec.items()}

    @staticmethod
    def _cosine(v1, v2):
        return sum(w * v2.get(term, 0.0) for term, w in v1.items())

    def retrieve(self, query_text):
        t0 = time.perf_counter()
        qvec = self._vectorize(_tokenize(query_text, stem=self.stem))
        scored = [
            (self._cosine(qvec, dv), self.turns[i])
            for i, dv in enumerate(self.doc_vectors)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [t for score, t in scored[: self.top_k] if score > 0]
        query_time = time.perf_counter() - t0
        return top, query_time

    def answer(self, category, question_type, query_text):
        """
        要約を行わないため、「答え」そのものは返さず、検索結果(上位ターン群)を返す。
        採点時は、検索結果の生テキストの中に正解(gold)が部分文字列として含まれているか
        (= 読み手がこの検索結果から正解にたどり着く材料=カバレッジがあるか)を見る。
        """
        top, query_time = self.retrieve(query_text)
        combined_text = " ".join(text for (_, _, text) in top)
        return combined_text, query_time, top
