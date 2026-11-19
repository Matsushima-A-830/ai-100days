"""Builds the weights of a hand-written associative-memory model for ARC science questions.

Every fact below was written by hand from general science knowledge, not fitted to any data.
build() turns each fact sentence into a sparse bag-of-words "key" row over vocab.txt, weighted by
an inverse-document-frequency computed over the fact corpus itself (so common words like "the" or
"energy" matter less than rare, topic-specific words like "covalent" or "decomposer"). arch.py
then only has to compare an encoded question+option against these keys and read off a value; no
weight is tuned by gradient descent or by looking at labelled ARC questions.
"""
import math
import re
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).parent
TOKEN = re.compile(r"[a-z0-9']+")

FACTS = [
    "An oxygen molecule is made of two oxygen atoms that share two electron pairs, a double covalent bond.",
    "A covalent bond forms when two atoms share a pair of electrons instead of transferring them.",
    "An ionic bond forms when one atom transfers an electron to another atom, creating charged ions that attract each other.",
    "Water is a compound made of two hydrogen atoms covalently bonded to one oxygen atom.",
    "An atom is the smallest unit of an element that keeps the chemical properties of that element.",
    "A molecule is two or more atoms joined together by chemical bonds.",
    "An element is a pure substance made of only one kind of atom and cannot be broken into simpler substances by chemical means.",
    "A compound is a substance made of two or more different elements chemically combined in a fixed ratio.",
    "A mixture combines two or more substances that keep their own properties and can be separated by physical means.",
    "Solids have particles that are tightly packed and vibrate in place, so a solid keeps a fixed shape and volume.",
    "Liquids have particles that are close together but can move past each other, so a liquid takes the shape of its container.",
    "Gases have particles that are far apart and move freely, so a gas expands to fill its container.",
    "Melting is the change of a solid into a liquid when heat is added.",
    "Freezing is the change of a liquid into a solid when heat is removed.",
    "Evaporation is the change of a liquid into a gas, usually at its surface.",
    "Condensation is the change of a gas into a liquid when the gas loses heat energy.",
    "Sublimation is the change of a solid directly into a gas without passing through the liquid state.",
    "A physical change, such as cutting paper or melting ice, changes the form of a substance but not what it is made of.",
    "A chemical change, such as burning wood or rusting iron, produces a new substance with different properties.",
    "Rusting happens when iron reacts slowly with oxygen and water to form iron oxide.",
    "Burning, or combustion, is a chemical reaction between a fuel and oxygen that releases heat and light.",
    "The law of conservation of mass says that matter is neither created nor destroyed in a chemical reaction, only rearranged.",
    "An acid is a substance that tastes sour and turns blue litmus paper red, like lemon juice or vinegar.",
    "A base is a substance that feels slippery and turns red litmus paper blue, like baking soda or soap.",
    "The pH scale measures how acidic or basic a solution is, from 0 very acidic to 14 very basic, with 7 neutral.",
    "Density is the amount of mass packed into a given volume of a substance.",
    "An object sinks in water if its density is greater than the density of water, and floats if it is less.",
    "Metals are usually shiny, conduct heat and electricity well, and can be bent into wires or hammered into sheets.",
    "A force is a push or a pull that can change the speed or direction of an object's motion.",
    "Gravity is a force that pulls objects toward each other and pulls objects on Earth toward the center of Earth.",
    "Friction is a force that opposes motion between two surfaces that are touching each other.",
    "Newton's first law says an object at rest stays at rest and an object in motion stays in motion unless a force acts on it.",
    "Newton's second law says the acceleration of an object depends on the net force applied and the object's mass.",
    "Newton's third law says that for every action force there is an equal and opposite reaction force.",
    "Speed is the distance an object travels divided by the time it takes to travel that distance.",
    "Kinetic energy is the energy of motion; a faster or heavier moving object has more kinetic energy.",
    "Potential energy is stored energy, such as the energy an object has because of its height above the ground.",
    "Energy cannot be created or destroyed, only changed from one form to another; this is the law of conservation of energy.",
    "A simple machine, such as a lever, pulley, wheel and axle, inclined plane, screw, or wedge, changes the size or direction of a force needed to do work.",
    "A lever is a rigid bar that pivots on a fixed point called a fulcrum to lift a load with less force.",
    "A pulley uses a wheel and a rope to change the direction of a pulling force, making it easier to lift objects.",
    "An inclined plane is a flat, slanted surface that reduces the force needed to raise an object by increasing the distance.",
    "Work is done when a force moves an object over a distance in the direction of the force.",
    "Heat moves by conduction when it travels directly through a material by contact between particles.",
    "Heat moves by convection when warmer, less dense fluid rises and cooler, denser fluid sinks, creating a circulating current.",
    "Heat moves by radiation when energy travels as electromagnetic waves and needs no matter to travel through, as from the Sun to Earth.",
    "An electric circuit is a closed loop path along which electric current can flow from a power source through a load and back.",
    "In a series circuit the components are connected one after another along a single path, so one break stops current everywhere.",
    "In a parallel circuit the components are connected along separate branches, so current can keep flowing through the other branches if one breaks.",
    "A conductor, such as copper or other metals, allows electric current to pass through it easily.",
    "An insulator, such as rubber, plastic, or glass, resists the flow of electric current.",
    "A magnet has a north pole and a south pole; like poles repel each other and opposite poles attract each other.",
    "An electromagnet is a magnet created by an electric current flowing through a coil of wire, often wrapped around an iron core.",
    "Static electricity builds up when electrons are transferred between objects by rubbing, leaving one object positively and the other negatively charged.",
    "A wave carries energy from one place to another without the medium itself traveling along with it.",
    "In a transverse wave, the particles of the medium move up and down, perpendicular to the direction the wave travels.",
    "In a longitudinal wave, such as sound, the particles of the medium move back and forth, parallel to the direction the wave travels.",
    "Wavelength is the distance between one point on a wave and the identical point on the next cycle of the wave.",
    "Frequency is the number of complete wave cycles that pass a point in one second, measured in hertz.",
    "Sound is a longitudinal wave made by a vibrating object that travels through a medium such as air, water, or solid material.",
    "Sound cannot travel through a vacuum because it needs a medium of particles to carry its vibrations.",
    "Pitch depends on frequency: a higher frequency sound wave has a higher pitch, and a lower frequency has a lower pitch.",
    "Light is an electromagnetic wave that can travel through empty space, unlike sound.",
    "Reflection occurs when a wave bounces off a surface instead of passing through it, as light bounces off a mirror.",
    "Refraction occurs when a wave bends as it passes from one medium into another medium of different density, like light bending through water.",
    "A rainbow forms when sunlight is refracted and separated into its different colors as it passes through water droplets.",
    "Opaque materials block light completely, translucent materials let some light pass through and scatter it, and transparent materials let light pass through clearly.",
    "Earth rotates on its axis once approximately every 24 hours, which causes day and night.",
    "Because Earth spins from west to east, the Sun appears to rise in the east and set in the west.",
    "Earth revolves around the Sun once approximately every 365 days, which, combined with the tilt of Earth's axis, causes the seasons.",
    "The Moon orbits Earth about once every 27 to 29 days, and its changing appearance from new moon to full moon is called the lunar phases.",
    "A solar eclipse happens when the Moon passes between the Sun and Earth, blocking some or all of the Sun's light.",
    "A lunar eclipse happens when Earth passes between the Sun and the Moon, casting Earth's shadow on the Moon.",
    "The solar system includes the Sun and the planets, moons, asteroids, and comets that orbit it because of the Sun's gravity.",
    "The inner, rocky planets of the solar system are Mercury, Venus, Earth, and Mars.",
    "The outer planets, Jupiter, Saturn, Uranus, and Neptune, are much larger and made mostly of gas and ice.",
    "Weathering is the breaking down of rock into smaller pieces by wind, water, ice, temperature changes, or living things, without moving the pieces away.",
    "Erosion is the process by which wind, water, ice, or gravity picks up and carries weathered rock and soil to a new location.",
    "Deposition is the process by which eroded sediment is dropped and settles in a new location, such as sand at the bottom of a river.",
    "A glacier is a huge, slow-moving mass of ice that can pick up and carry boulders and soil as it moves downhill.",
    "Flowing water in a river or flood can carry away small soil particles from a riverbank and deposit them elsewhere.",
    "Wind can pick up and blow loose sand and dust against rocks, slowly wearing them down in desert areas.",
    "Freezing and thawing of water in cracks of pavement or rock, called ice wedging, can split the rock or pavement apart.",
    "The rock cycle describes how igneous, sedimentary, and metamorphic rocks can change from one type into another over long periods of time.",
    "Igneous rock forms when melted rock, called magma or lava, cools and solidifies.",
    "Sedimentary rock forms when layers of sediment are compacted and cemented together over time.",
    "Metamorphic rock forms when existing rock is changed by intense heat and pressure without melting completely.",
    "The water cycle describes water moving between the atmosphere, land, and oceans through evaporation, condensation, precipitation, and collection.",
    "Precipitation is water falling from clouds to Earth's surface as rain, snow, sleet, or hail.",
    "Weather is the short-term condition of the atmosphere in a place, such as today's temperature and rain, while climate is the average weather pattern of a region over many years.",
    "Soil is formed over long periods of time from weathered rock mixed with decayed organic matter, water, and air.",
    "Fossil fuels, such as coal, oil, and natural gas, formed from the remains of ancient living things and take millions of years to form, making them nonrenewable resources.",
    "Renewable energy sources, such as wind, solar, hydroelectric, and geothermal power, naturally replenish within a short period of time and do not run out with use.",
    "Solar panels convert energy from sunlight directly into electrical energy.",
    "Wind turbines convert the kinetic energy of moving air into electrical energy.",
    "A cell is the smallest basic unit of structure and function in all living things.",
    "Plant cells have a rigid cell wall and chloroplasts for photosynthesis, while animal cells have neither.",
    "The nucleus of a cell stores the cell's genetic material, DNA, and directs the cell's activities.",
    "Mitochondria are the organelles in a cell that break down food to release usable energy for the cell, a process called cellular respiration.",
    "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce glucose and release oxygen.",
    "Chlorophyll is the green pigment in chloroplasts that absorbs sunlight for photosynthesis.",
    "Cellular respiration is the process by which cells break down glucose using oxygen to release energy, producing carbon dioxide and water as waste.",
    "Roots absorb water and minerals from the soil and anchor a plant in place.",
    "Stems support a plant and transport water and nutrients between the roots and the leaves.",
    "Leaves are the main site of photosynthesis in most plants, capturing sunlight and exchanging gases through small pores called stomata.",
    "Flowers contain the reproductive structures of many plants and often attract pollinators such as bees and butterflies.",
    "DNA, deoxyribonucleic acid, carries the genetic instructions that determine an organism's traits and is passed from parent to offspring.",
    "A gene is a section of DNA that codes for a specific trait, such as eye color or flower color.",
    "Heredity is the passing of traits from parents to offspring through genes.",
    "A dominant trait can show up in an offspring even when only one copy of the gene for it is inherited, while a recessive trait needs two copies to show up.",
    "Natural selection is the process by which organisms with traits better suited to their environment survive and reproduce more successfully than others.",
    "An adaptation is an inherited trait that helps an organism survive and reproduce in its particular environment.",
    "Camouflage is an adaptation in which an organism's coloring or pattern helps it blend into its surroundings and avoid predators.",
    "Some animals, such as certain octopuses, cuttlefish, and chameleons, have specialized skin cells that let them change color rapidly to hide from predators or communicate.",
    "Mimicry is an adaptation in which one species evolves to resemble another species, often to avoid predators.",
    "A food chain shows the transfer of energy from one organism to the next, usually starting with a producer and moving through consumers.",
    "A producer, such as a green plant or algae, makes its own food using photosynthesis.",
    "A consumer is an organism that must eat other organisms to obtain energy, including herbivores, carnivores, and omnivores.",
    "A decomposer, such as certain bacteria and fungi, breaks down dead organisms and waste, returning nutrients to the soil.",
    "Nearly all organisms in a grassland or other ecosystem depend, directly or indirectly, on decomposer bacteria and fungi in the soil to recycle nutrients that plants need to grow.",
    "A food web shows the many interconnected food chains within an ecosystem.",
    "An ecosystem includes all the living organisms and nonliving factors, such as water, soil, and sunlight, interacting in a particular area.",
    "A population is a group of the same species living in the same area at the same time.",
    "A community is made up of all the different populations of species living and interacting in the same area.",
    "A biome is a large region characterized by a particular climate and the plant and animal communities adapted to it, such as a desert, rainforest, or tundra.",
    "The circulatory system, including the heart and blood vessels, transports blood, oxygen, and nutrients throughout the body.",
    "The respiratory system, including the lungs, brings oxygen into the body and removes carbon dioxide.",
    "The digestive system breaks down food into nutrients that the body can absorb and use for energy and growth.",
    "The nervous system, including the brain, spinal cord, and nerves, carries electrical signals that let the body sense and respond to its surroundings.",
    "The skeletal system provides the body's framework of bones, supporting the body and protecting internal organs.",
    "The muscular system is made of muscles that contract to produce movement of the body.",
    "The excretory system removes waste products from the body, including through the kidneys, which filter waste from the blood to form urine.",
    "The endocrine system is made of glands that release chemical messengers, called hormones, into the bloodstream to carry signals from one part of the body to another, similar to how other body systems carry messages between parts of the body.",
    "The integumentary system includes the skin, hair, and nails, and protects the body from injury, infection, and water loss.",
    "The immune system defends the body against disease-causing organisms such as bacteria and viruses.",
    "A virus is a tiny infectious particle that must invade a living cell in order to reproduce.",
    "Bacteria are single-celled microorganisms; some cause disease, while many others are harmless or even helpful, such as those that help digest food or decompose waste.",
    "To avoid contaminating a bacteria culture or risking illness, people performing a microbiology investigation should not bring food or drinks into the laboratory, and should wash their hands and wear gloves when handling samples.",
    "Scientists wear gloves and wash their hands when handling bacteria samples to protect themselves from infection and to keep the samples from being contaminated.",
    "An animal's life cycle is the series of stages it passes through from birth to death, which for many insects includes metamorphosis from egg to larva to pupa to adult.",
    "Vertebrates are animals with a backbone, such as fish, amphibians, reptiles, birds, and mammals, while invertebrates lack a backbone, such as insects and worms.",
    "Mammals are warm-blooded vertebrates that usually have hair or fur and feed their young with milk.",
    "Nonrenewable resources, such as coal, oil, and natural gas, exist in limited supplies and take far longer to form than humans use them.",
    "Developing renewable energy sources and more efficient technology helps reduce how quickly nonrenewable resources are used up.",
    "Wind energy is a renewable source of energy because wind is continuously produced by uneven heating of the atmosphere and does not run out.",
    "Recycling reuses materials such as paper, glass, metal, and plastic instead of making new materials from raw resources, which conserves resources and reduces waste.",
    "Pollution is the introduction of harmful substances into air, water, or soil, which can damage ecosystems and harm living things.",
    "Conservation is the careful use and protection of natural resources to make sure they remain available in the future.",
    "Improvements in food storage and shipping, such as refrigeration and faster transportation, let people in one region eat a wider variety of foods grown or raised in distant places.",
    "Refrigeration slows the growth of bacteria and the spoiling of food, which has allowed food to be transported and stored for longer distances and still arrive safe to eat.",
    "In a scientific investigation, a hypothesis is a testable explanation or prediction that scientists check with experiments and evidence.",
    "A controlled experiment changes only one variable, the independent variable, at a time while keeping other factors constant so results can be compared fairly.",
    "A dependent variable is the factor that is measured or observed in an experiment and that may change because of the independent variable.",
    "A thermometer measures temperature, a graduated cylinder or beaker measures volume of liquid, a balance measures mass, and a ruler or meter stick measures length.",
    "Scientists use models, such as diagrams or small physical replicas, to represent and better understand objects, systems, or processes that are too large, small, or complex to study directly.",
]


def words(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def build() -> dict[str, torch.Tensor]:
    vocab = [ln.strip() for ln in (HERE / "vocab.txt").read_text().splitlines() if ln.strip()]
    index = {w: i for i, w in enumerate(vocab)}
    v = len(vocab) + 2  # ids 0 (pad) and 1 (unknown) are never part of a fact's key

    # Inverse document frequency over the fact corpus: common words (e.g. "the", "energy") get a
    # low weight, rare topic-specific words (e.g. "covalent", "decomposer") get a high weight.
    doc_count = np.zeros(v, dtype=np.float64)
    fact_word_ids: list[list[int]] = []
    for fact in FACTS:
        ids = sorted({index[w] + 2 for w in words(fact) if w in index})
        fact_word_ids.append(ids)
        for i in ids:
            doc_count[i] += 1
    n_docs = len(FACTS)
    idf = np.log((n_docs + 1) / (doc_count + 1)) + 1.0  # smoothed idf, always positive

    facts = np.zeros((len(FACTS), v), dtype=np.float32)
    for row, ids in enumerate(fact_word_ids):
        for i in ids:
            facts[row, i] = idf[i]
    # Normalize each fact's key vector to unit length so a long fact sentence does not automatically
    # dominate the similarity score just by having more words.
    norms = np.linalg.norm(facts, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    facts = facts / norms

    return {
        "idf": torch.as_tensor(idf, dtype=torch.float32),
        "facts": torch.as_tensor(facts, dtype=torch.float32),
        "bias": torch.zeros(1, dtype=torch.float32),
    }
