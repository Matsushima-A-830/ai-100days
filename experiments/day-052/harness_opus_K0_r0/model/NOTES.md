# A hand-written retrieval model for ARC

## What it is

The model is a small information-retrieval system. All of its knowledge is a hand-written science knowledge base,
and the forward pass is a fixed tensor program that scores each answer option by how well some knowledge-base
sentence supports *question + option* together. Nothing is trained or fitted. Every number comes from counting
words in text I wrote, or is a hand-set constant.

## Files

- `kb/*.txt`: the knowledge base, about 4,900 sentences of grade-school science, one fact per line, grouped by
  topic: Earth and space, rocks and plate tectonics, weather and water, cells, plants, animals, the human body,
  genetics and evolution, ecology, matter, energy and forces, electricity and waves, resources and environment,
  science practice and lab safety, technology and history, a glossary, structure/function statements, contrasts,
  everyday and regional facts, and elementary-level facts.
  A line of the form `= category words | item, item, ...` expands into one short sentence per item
  ("salamander is an amphibian, ..."). This makes it cheap to write lists such as conductors, renewable
  resources, examples of chemical changes, or which tool measures what. Each fact ends up in its own short
  sentence instead of one long list sentence.
- `families.txt`: word families that should count as one concept. These are irregular forms (grew/grow,
  mice/mouse), derivations Porter misses (condense/condensation), protections against wrong merges
  (organism vs organ), comparatives (younger/young), and a few synonyms (produce/generate, spin/rotate,
  sunlight/sun).
- `stopwords.txt`: function words and question filler ("which", "best", "describes", "example", ...).
- `textproc.py`: the tokenizer (the same regex as the harness), a Porter stemmer written from the 1980 paper, and
  the family lookup.
- `make_vocab.py`: writes `vocab.txt`. It contains every knowledge-base, family and stop word, plus generated
  inflections (plurals, -ed, -ing, -ation, ...) that the stemmer maps to the same concept as a knowledge-base word.
  This way a question word like "evaporates" still finds "evaporation". It must be rerun after editing the KB.
- `build.py`: turns the text into tensors (below).
- `arch.py`: the forward pass.

## Weights (build.py)

- `stem_of[word id]`: the concept id of each vocabulary word (0 for padding, unknown words and stop words).
- Phrase concepts: every pair of adjacent content words in a KB sentence (after dropping stop words) becomes an
  extra concept. The pairs are stored as sorted keys `a*C+b`. The forward pass finds them in questions and options
  with `searchsorted`, so "natural gas" or "cell wall" can match as a unit. Their idf is scaled by 0.25.
- `idf[concept] = log((N+1)/(df+0.5))` over the N knowledge-base sentences.
- The sentence × concept incidence matrix, sparse. Each row is scaled by `1/len^0.5`, so short, specific sentences
  count more than long list sentences. It is stored as index and value tensors and assembled in `forward`.
- A flag for each sentence that contains a negation ("not", "no", "cannot", ...).
- A PPMI matrix of concept co-occurrence within sentences. It is only a weak tie-breaker.
- Word flags for negative questions ("except", "least likely", "which ... not").
- `hp`: hand-set constants.

## Forward pass (arch.py)

1. The question becomes a bag of concepts and phrase concepts, weighted by idf. Words near the end of the question
   (where the actual ask usually is) get up to 3× weight, decaying over about 10 words.
2. Each option becomes a bag of idf-weighted concepts. Concepts that already occur in the question are
   discounted, since they match trivially. The option vector is divided by (its total weight)^0.4. Full division
   would let a one-word option beat a three-word option that is two-thirds supported. No division would simply
   reward long options.
3. For every KB sentence s: support(s) = (question coverage of s) × (option coverage of s). A *polarity* factor
   applies: an option that says "not/no/cannot" is supported at full strength by negated sentences and at half
   strength by plain ones, and the reverse for plain options.
4. Retrieval score = the best sentence + 0.3 × the second best + 0.09 × the third, ... (top 5, geometric decay).
5. Add 0.02 × the PPMI association between question and option concepts (a tie-breaker when nothing is
   retrieved).
6. Negative questions (EXCEPT, "Which ... NOT ...", "least likely") flip the sign, so the least-supported option
   wins.
7. A tiny bonus per option word breaks exact ties.

## Why this design

With no training and no pretrained resources, the knowledge has to be written by hand. Retrieval over short
sentences is the simplest mechanism that turns written facts into answers robustly. It does not need the question to
be phrased like the fact; it only needs the important words of the question and of the correct option to occur
together in some fact. The constants were set by reasoning and checked by hand on questions I made up myself (about
450, in /srv/work/dev, not part of the model). No automatic search was done.

## Known limits

- Bag of words: it cannot tell "liquid becomes solid" from "solid becomes liquid", or "increases" from
  "decreases" in a context. Phrase concepts recover only a little word order.
- Questions that need arithmetic, Punnett-square reasoning or several chained steps are mostly guesses.
- Distractors that are frequently mentioned together with the question's topic can win. Using mostly the single
  best sentence, not a sum over many, limits this.
- Coverage is limited to what I wrote: a few thousand facts against a curriculum that is much larger.
