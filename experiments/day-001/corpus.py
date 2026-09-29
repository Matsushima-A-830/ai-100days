# -*- coding: utf-8 -*-
"""Self-authored chain-of-thought style reasoning traces used as a substitute
for the paper's real training data (open-thoughts/OpenThoughts3-1.2M etc.),
which could not be downloaded in this sandbox because huggingface.co is
blocked by the outbound network policy.

Each trace intentionally reuses the kind of "structural" filler phrases the
paper highlights (Wait,, So,, Let me, Therefore,, Hmm,, Alternatively,,
double-check, step by step, etc.) because those are exactly the low-entropy
n-grams the Shorthand-for-Thought algorithm is designed to fold into
supertokens.
"""

TRAIN_TRACES = [
    """Let me think about this step by step. We need to find two numbers whose
sum is 24 and whose product is 143. Let the numbers be x and 24 - x. So
x(24 - x) = 143, which gives 24x - x^2 = 143, or x^2 - 24x + 143 = 0.
Let me solve this quadratic. The discriminant is 24^2 - 4*143 = 576 - 572 = 4.
So x = (24 +/- 2) / 2, which gives x = 13 or x = 11. Let me double-check:
13 * 11 = 143 and 13 + 11 = 24. That matches. So the answer is 11 and 13.""",
    """Okay, let's work through this. A train travels 60 miles in the first hour
and then slows down by 10 miles per hour every subsequent hour. How far has it
gone after 4 hours? Let me compute hour by hour. Hour 1: 60 miles. Hour 2: 50
miles, total 110. Hour 3: 40 miles, total 150. Hour 4: 30 miles, total 180.
Wait, let me double-check the arithmetic: 60 + 50 = 110, 110 + 40 = 150,
150 + 30 = 180. So after 4 hours the train has traveled 180 miles.""",
    """We need to determine whether 91 is prime. Let me check divisibility step
by step. Is 91 divisible by 2? No, it's odd. Is it divisible by 3? 9 + 1 = 10,
not divisible by 3. Is it divisible by 5? No, it doesn't end in 0 or 5. Is it
divisible by 7? 7 * 13 = 91. Yes! So 91 = 7 * 13, which means 91 is not prime.
Let me double-check: 7 * 13 = 91. That's correct. So 91 is composite.""",
    """Let's think about this carefully. A bag has 4 red balls and 6 blue balls.
If we draw two balls without replacement, what is the probability both are
red? First draw: probability of red is 4/10. Given the first was red, second
draw: probability of red is 3/9. So the combined probability is (4/10) *
(3/9) = 12/90 = 2/15. Let me double-check: 4/10 simplifies to 2/5, and 3/9
simplifies to 1/3, so 2/5 * 1/3 = 2/15. So the probability is 2/15.""",
    """Okay, let me reason through this. We want to know how many ways we can
arrange the letters in the word LEVEL. The word has 5 letters: L, E, V, E, L.
Notice that L appears twice and E appears twice. So the number of distinct
arrangements is 5! / (2! * 2!) = 120 / 4 = 30. Let me double-check that
computation: 5! = 120, 2! * 2! = 4, and 120 / 4 = 30. So there are 30 distinct
arrangements.""",
    """Let's work through this geometry problem step by step. A rectangle has a
perimeter of 36 cm and a length that is twice its width. Let the width be w,
so the length is 2w. The perimeter is 2(w + 2w) = 6w = 36, so w = 6. Then the
length is 12. Let me double-check: perimeter = 2(6 + 12) = 2 * 18 = 36. That
matches. So the width is 6 cm and the length is 12 cm, giving an area of
6 * 12 = 72 square centimeters.""",
    """Hmm, let me think about this differently. We're asked for the sum of the
first 20 positive even numbers. The first 20 even numbers are 2, 4, 6, ...,
40. This is an arithmetic series with first term 2, last term 40, and 20
terms. So the sum is 20 * (2 + 40) / 2 = 20 * 21 = 420. Let me double-check
with a different method: sum of first n even numbers is n(n+1), so
20 * 21 = 420. Both methods agree, so the answer is 420.""",
    """Let's think step by step about this logic puzzle. Three friends, Alice,
Bob, and Carol, each have a different pet: a cat, a dog, and a fish. Alice
does not have the cat. Bob does not have the fish. Carol does not have the
dog. Wait, let me set up a table. If Alice doesn't have the cat, Alice has
the dog or the fish. If Carol doesn't have the dog, and if Alice had the dog,
that's fine, but let's check Bob: Bob doesn't have the fish, so Bob has the
cat or the dog. Suppose Alice has the fish. Then Bob has the cat (since Bob
can't have the fish and Alice took the fish). Then Carol has the dog, but
Carol can't have the dog. Contradiction. So Alice has the dog. Then Carol
has the cat or the fish; Carol can't have the dog anyway which is consistent.
Bob can't have the fish, so Bob has the cat, leaving Carol with the fish. Let
me double-check: Alice=dog, Bob=cat, Carol=fish. Alice doesn't have the cat,
correct. Bob doesn't have the fish, correct. Carol doesn't have the dog,
correct. So the answer is Alice-dog, Bob-cat, Carol-fish.""",
    """Let me think about this carefully. What is 17% of 250? Let's convert
17% to a decimal: 0.17. Then 0.17 * 250 = 42.5. Let me double-check with a
different approach: 10% of 250 is 25, 7% of 250 is 17.5, so 17% is
25 + 17.5 = 42.5. Both approaches agree. So 17% of 250 is 42.5.""",
    """Okay, let's work through this carefully. If f(x) = 2x^2 - 3x + 1, what
is f(4)? Let me substitute x = 4. f(4) = 2*(4^2) - 3*4 + 1 = 2*16 - 12 + 1 =
32 - 12 + 1 = 21. Let me double-check the arithmetic step by step: 4^2 = 16,
2*16 = 32, 3*4 = 12, 32 - 12 = 20, 20 + 1 = 21. So f(4) = 21.""",
    """Let's think about this step by step. A store offers a 20% discount on a
$80 item, and then an additional 10% off the discounted price. What is the
final price? First discount: 80 * 0.8 = 64. Second discount: 64 * 0.9 = 57.6.
Let me double-check: 20% of 80 is 16, so 80 - 16 = 64. Then 10% of 64 is 6.4,
so 64 - 6.4 = 57.6. Both match. So the final price is $57.60.""",
    """Hmm, let's reason about this carefully. Is the number 2^10 - 1 prime?
2^10 = 1024, so 2^10 - 1 = 1023. Let me check divisibility. 1023 / 3 = 341.
Let's verify: 3 * 341 = 1023. Yes. So 1023 is divisible by 3, meaning
1023 = 3 * 341, so 2^10 - 1 is not prime. Let me double-check 341: is 341
itself prime? 341 / 11 = 31, and 11 * 31 = 341. So 341 = 11 * 31. Anyway,
the original question is answered: 1023 is composite.""",
    """Let me think through this combinatorics problem step by step. How many
ways can we choose a committee of 3 people from a group of 8? This is a
combination problem: C(8,3) = 8! / (3! * 5!) = (8*7*6) / (3*2*1) = 336 / 6 =
56. Let me double-check: 8*7*6 = 336, and 3! = 6, so 336/6 = 56. So there are
56 possible committees.""",
    """Okay, let's work through this word problem step by step. Two pipes fill
a tank. Pipe A alone fills it in 6 hours, Pipe B alone fills it in 3 hours.
How long does it take together? Pipe A's rate is 1/6 tank per hour, Pipe B's
rate is 1/3 tank per hour. Combined rate is 1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2
tank per hour. So together they take 2 hours. Let me double-check: in 2
hours, Pipe A fills 2/6 = 1/3 and Pipe B fills 2/3, and 1/3 + 2/3 = 1, a full
tank. So the answer is 2 hours.""",
    """Let's think step by step about this sequence. Find the next term in the
sequence 3, 7, 15, 31, 63, ... Let me look at the differences: 7-3=4,
15-7=8, 31-15=16, 63-31=32. The differences are doubling: 4, 8, 16, 32, so
the next difference should be 64. So the next term is 63 + 64 = 127. Let me
double-check by another pattern: each term looks like 2^(n+1) - 1: 2^2-1=3,
2^3-1=7, 2^4-1=15, 2^5-1=31, 2^6-1=63, so the next is 2^7-1=127. Both
approaches agree. So the answer is 127.""",
    """Hmm, let's reason about this carefully. A right triangle has legs of
length 6 and 8. What is the length of the hypotenuse? By the Pythagorean
theorem, c^2 = 6^2 + 8^2 = 36 + 64 = 100, so c = 10. Let me double-check:
6^2 = 36, 8^2 = 64, 36 + 64 = 100, and the square root of 100 is 10. So the
hypotenuse is 10.""",
]

HELD_OUT_TRACES = [
    """Let me think about this step by step. What is the least common multiple
of 12 and 18? Let's factor them: 12 = 2^2 * 3, and 18 = 2 * 3^2. The LCM
takes the highest power of each prime: 2^2 * 3^2 = 4 * 9 = 36. Let me
double-check: 36 / 12 = 3 and 36 / 18 = 2, both whole numbers, and no smaller
number works. So the LCM of 12 and 18 is 36.""",
    """Okay, let's work through this carefully. A car depreciates by 15% each
year. If it costs $20,000 new, what is its value after 2 years? After year
1: 20000 * 0.85 = 17000. After year 2: 17000 * 0.85 = 14450. Let me
double-check: 20000 * 0.85 * 0.85 = 20000 * 0.7225 = 14450. Both match. So
the value after 2 years is $14,450.""",
    """Let's think step by step about this logic puzzle. Five people are
standing in a line. Dana is somewhere ahead of Eli. Frank is right behind
Dana. Wait, let me reconsider the constraints one at a time and see what
ordering is forced, checking each candidate placement carefully before
settling on a final answer, and then double-check the whole line at the end
to make sure every constraint holds simultaneously without contradiction.""",
    """Hmm, let me reason about this differently. What is the sum of the
interior angles of a hexagon? The formula for a polygon with n sides is
(n-2)*180. For a hexagon, n=6, so (6-2)*180 = 4*180 = 720. Let me
double-check with a triangulation argument: a hexagon can be split into 4
triangles from one vertex, and each triangle contributes 180 degrees, so
4*180 = 720. Both approaches agree. So the sum of interior angles is 720
degrees.""",
]
