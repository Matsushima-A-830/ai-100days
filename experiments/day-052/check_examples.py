import sys
sys.path.insert(0, ".")
from wsp import free_model
from pathlib import Path

EXAMPLES = [
    ("The atoms that make up oxygen gas",
     ["share two covalent bonds.", "have a definite shape.", "share a pair of neutrons.", "have two free electrons."], 0),
    ("In New York State, an observer will usually see the Sun rise in the",
     ["north", "south", "east", "west"], 2),
    ("Which of these living things in a grassland ecosystem depend on the presence of a variety of bacteria and other microorganisms in the soil?",
     ["worms only", "green plants only", "plants and animals only", "all the organisms in the ecosystem"], 3),
    ("Nonrenewable sources of energy have limited supplies. Researchers are developing devices that will make renewable energy more available. Which is a source of renewable energy?",
     ["coal", "gasoline", "oil", "wind"], 3),
    ("When a transverse wave passes from right to left through a medium, what happens to the particles of the medium?",
     ["Particles travel from right to left along the wave.", "Particles travel from left to right along the wave.",
      "Particles move back and forth parallel to the wave.", "Particles move back and forth perpendicular to the wave."], 3),
    ("Over time, the ability to ship foods around the world has improved. Which is the most likely effect these shipping improvements have had on people?",
     ["They have increased the time it takes to shop for food.", "They have decreased the number of grocery stores.",
      "They have decreased the need for refrigerators.", "They have increased the types of food available for sale."], 3),
    ("Students are performing an investigation to determine the types of bacteria that grow inside their school. Which activity should the students avoid while performing this investigation?",
     ["wearing gloves while handling the samples", "cleaning all materials they have finished using",
      "bringing food and drinks into the laboratory", "washing hands before leaving the laboratory"], 2),
    ("Inside cells, special molecules carry messages from the membrane to the nucleus. Which body system uses a similar process?",
     ["endocrine system", "lymphatic system", "excretory system", "integumentary system"], 0),
    ("All of the following are examples of erosion EXCEPT:",
     ["The wind in the desert blows sand against a rock.", "A glacier picks up boulders as it moves.",
      "A flood washes over a riverbank, and the water carries small soil particles downstream.",
      "An icy winter causes the pavement in a road to crack."], 3),
    ("A certain animal has specialized cells that can cause it to change color rapidly. This color change will most likely help the animal",
     ["run quickly.", "digest food rapidly.", "hide from predators.", "retain body heat."], 2),
]

qs = [e[0] for e in EXAMPLES]
opts = [e[1] for e in EXAMPLES]
ans = [e[2] for e in EXAMPLES]
logits, size, problems = free_model.run(Path("my_model"), {"probe": (qs, opts)}, isolate=False, encoder=free_model.encode_of("free-arc"))
print("problems", problems); print("logits type", type(logits), logits if logits is None else list(logits.keys()))
correct = 0
for i, row in enumerate(logits["probe"]):
    pick = int(row.argmax())
    ok = pick == ans[i]
    correct += ok
    print(f"pick={pick} answer={ans[i]} {'OK' if ok else 'WRONG'} :: {qs[i][:60]!r}")
print(f"{correct}/10 correct on the ten given example questions (real torch path)")
