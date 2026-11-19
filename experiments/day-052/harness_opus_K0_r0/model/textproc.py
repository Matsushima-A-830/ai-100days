"""Text processing shared by build.py and make_vocab.py: tokenizer, Porter stemmer, hand-written word families."""
import re

TOKEN = re.compile(r"[a-z0-9']+")


def words(text):
    return TOKEN.findall(text.lower())


# ---------------------------------------------------------------- Porter stemmer (Porter 1980), written from the paper
VOWELS = set("aeiou")


def _cons(w, i):
    c = w[i]
    if c in VOWELS:
        return False
    if c == "y":
        return i == 0 or not _cons(w, i - 1)
    return True


def _m(stem):
    """number of VC sequences"""
    m, prev_v = 0, False
    for i in range(len(stem)):
        v = not _cons(stem, i)
        if prev_v and not v:
            m += 1
        prev_v = v
    return m


def _has_v(stem):
    return any(not _cons(stem, i) for i in range(len(stem)))


def _dbl(w):
    return len(w) >= 2 and w[-1] == w[-2] and _cons(w, len(w) - 1)


def _cvc(w):
    if len(w) < 3:
        return False
    return _cons(w, len(w) - 3) and not _cons(w, len(w) - 2) and _cons(w, len(w) - 1) and w[-1] not in "wxy"


STEP2 = [("ational", "ate"), ("tional", "tion"), ("enci", "ence"), ("anci", "ance"), ("izer", "ize"), ("bli", "ble"),
         ("alli", "al"), ("entli", "ent"), ("eli", "e"), ("ousli", "ous"), ("ization", "ize"), ("ation", "ate"),
         ("ator", "ate"), ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"), ("ousness", "ous"), ("aliti", "al"),
         ("iviti", "ive"), ("biliti", "ble"), ("logi", "log")]
STEP3 = [("icate", "ic"), ("ative", ""), ("alize", "al"), ("iciti", "ic"), ("ical", "ic"), ("ful", ""), ("ness", "")]
STEP4 = ["al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement", "ment", "ent", "ion", "ou", "ism", "ate",
         "iti", "ous", "ive", "ize"]


def porter(w):
    if len(w) <= 2:
        return w
    # step 1a
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies"):
        w = w[:-2]
    elif w.endswith("ss"):
        pass
    elif w.endswith("s"):
        w = w[:-1]
    # step 1b
    flag = False
    if w.endswith("eed"):
        if _m(w[:-3]) > 0:
            w = w[:-1]
    elif w.endswith("ed") and _has_v(w[:-2]):
        w, flag = w[:-2], True
    elif w.endswith("ing") and _has_v(w[:-3]):
        w, flag = w[:-3], True
    if flag:
        if w.endswith(("at", "bl", "iz")):
            w += "e"
        elif _dbl(w) and w[-1] not in "lsz":
            w = w[:-1]
        elif _m(w) == 1 and _cvc(w):
            w += "e"
    # step 1c
    if w.endswith("y") and _has_v(w[:-1]):
        w = w[:-1] + "i"
    # step 2
    for suf, rep in STEP2:
        if w.endswith(suf):
            if _m(w[:-len(suf)]) > 0:
                w = w[:-len(suf)] + rep
            break
    # step 3
    for suf, rep in STEP3:
        if w.endswith(suf):
            if _m(w[:-len(suf)]) > 0:
                w = w[:-len(suf)] + rep
            break
    # step 4
    for suf in STEP4:
        if w.endswith(suf):
            st = w[:-len(suf)]
            if _m(st) > 1 and (suf != "ion" or (st and st[-1] in "st")):
                w = st
            break
    # step 5a
    if w.endswith("e"):
        st = w[:-1]
        if _m(st) > 1 or (_m(st) == 1 and not _cvc(st)):
            w = st
    # step 5b
    if _m(w) > 1 and _dbl(w) and w.endswith("l"):
        w = w[:-1]
    return w


def _inflect(x):
    out = [x + "s", x + "es", x + "ed", x + "ing", x + "'s"]
    if x.endswith("e"):
        out += [x + "d", x[:-1] + "ing"]
    if x.endswith("y"):
        out += [x[:-1] + "ies", x[:-1] + "ied"]
    return out


def load_families(path="families.txt"):
    """Each line: a group of words that should share one stem (the first word's). Simple inflections of every listed
    word join the group too, unless listed elsewhere. Text after # is a comment."""
    fam, extra = {}, {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        ws = words(line)
        for x in ws:
            fam[x] = ws[0]
            for y in _inflect(x):
                extra.setdefault(y, ws[0])
    for y, h in extra.items():
        fam.setdefault(y, h)
    return fam


class Stemmer:
    def __init__(self, families):
        self.fam = families
        self.cache = {}

    def __call__(self, w):
        r = self.cache.get(w)
        if r is not None:
            return r
        x = w
        if x.endswith("'s"):
            x = x[:-2]
        x = x.strip("'")
        if x.endswith("uses") and not x.endswith("ouses") and len(x) > 5:
            x = x[:-2]                    # viruses -> virus, octopuses -> octopus
        if x in self.fam:
            r = "#" + self.fam[x]
        elif len(x) > 3 and x.endswith(("us", "is")) and not x.endswith("ous"):
            r = x                         # virus, axis: Porter would cut them to viru, axi
        else:
            r = porter(x)
        self.cache[w] = r
        return r
