"""Write vocab.txt: every word of the knowledge base, families and stop words, plus inflected forms of knowledge-base
words that the stemmer maps to the same concept (so that a question saying "evaporates" finds "evaporation").
Run: python make_vocab.py (from this folder)."""
import glob

from textproc import Stemmer, load_families, words


def forms(x):
    out = {x + "s", x + "es", x + "ed", x + "d", x + "ing", x + "er", x + "ers", x + "est", x + "ly", x + "'s",
           x + "ation", x + "ations", x + "ment", x + "ments", x + "ness", x + "al", x + "ally", x + "ity", x + "ic"}
    if x.endswith("e"):
        out |= {x[:-1] + "ing", x[:-1] + "ation", x[:-1] + "ations", x[:-1] + "ion", x[:-1] + "ions", x[:-1] + "y"}
    if x.endswith("y"):
        out |= {x[:-1] + "ies", x[:-1] + "ied", x[:-1] + "ier", x[:-1] + "iest", x[:-1] + "ily"}
    if len(x) > 2 and x[-1] not in "aeiouwxy" and x[-2] in "aeiou" and x[-3] not in "aeiou":
        out |= {x + x[-1] + "ed", x + x[-1] + "ing", x + x[-1] + "er", x + x[-1] + "est"}
    for a, b in (("able", "ability"), ("ible", "ibility"), ("ile", "ility"), ("ive", "ivity"), ("al", "ality"),
                 ("ent", "ence"), ("ant", "ance"), ("ous", "osity"), ("ic", "ically"), ("y", "iness")):
        if x.endswith(a):
            out.add(x[:-len(a)] + b)
    if x.endswith("s"):
        out.add(x[:-1])
    if x.endswith("es"):
        out.add(x[:-2])
    if x.endswith("ed"):
        out |= {x[:-2], x[:-1], x[:-2] + "ing", x[:-2] + "s"}
    if x.endswith("ing"):
        out |= {x[:-3], x[:-3] + "e", x[:-3] + "s", x[:-3] + "ed"}
    if x.endswith("ion"):
        out |= {x[:-3], x[:-3] + "e", x[:-3] + "es", x[:-3] + "ed", x[:-3] + "ing"}
    return out


def main():
    stem = Stemmer(load_families("families.txt"))
    base = set()
    for f in sorted(glob.glob("kb/*.txt")) + ["families.txt", "stopwords.txt", "extra_words.txt"]:
        try:
            base |= set(words(open(f, encoding="utf-8").read()))
        except FileNotFoundError:
            pass
    vocab = set(base)
    for x in base:
        s = stem(x)
        for y in forms(x):
            if y not in vocab and stem(y) == s:
                vocab.add(y)
    with open("vocab.txt", "w", encoding="utf-8") as fh:
        for x in sorted(vocab):
            fh.write(x + "\n")
    print(len(base), "base words,", len(vocab), "vocabulary words")


if __name__ == "__main__":
    main()
