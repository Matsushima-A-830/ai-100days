# Model: hand-written associative-memory fact table for ARC

I (Claude, acting as the writer for this exercise, per the paper's "weight-space programming"
setup) was given only the ten example ARC questions in the task and no other ARC data. I wrote
down about 150 short grade-school-science fact sentences from my own general knowledge, covering
chemistry, physics, waves, earth/space science, life science, ecology, body systems, and the
scientific method -- the kinds of topics the ten examples span.

How it works (no gradient descent, nothing fitted to labelled ARC data):

1. `vocab.txt` lists every word that appears in my facts, in the ten example questions, and in a
   short hand-written list of common English function/comparison words, so the encoder recognizes
   ordinary words it will meet in unseen test questions.
2. `build.py` turns each fact sentence into a sparse "key" row: a bag-of-words vector over
   `vocab.txt`, weighted by an inverse-document-frequency computed over the fact corpus itself (so
   rare, topic words like "covalent" or "decomposer" count for more than common words like "the"
   or "energy"), then L2-normalized. This is the only place where numbers are computed from what I
   wrote; nothing here is tuned against ARC accuracy.
3. `arch.py` is a fixed tensor program (no branching, nothing data-dependent in Python, as the
   rules require): for each of the four options, it builds a bag-of-words vector of the question
   plus that option, compares it against every fact's key by cosine similarity, takes the 8 most
   similar facts, and sums their similarities (softmax-weighted) into that option's logit. The
   option whose text best overlaps my background-knowledge facts, together with the shared
   question text, gets the highest logit.

This is deliberately the simplest version of what the paper calls an "associative-memory-based"
design: a sparse table of hand-written facts read by a fixed retrieval procedure, rather than a
from-scratch architecture. Every entry traces back to one fact sentence I wrote, so a wrong answer
can be inspected by looking at which fact(s) it retrieved.
