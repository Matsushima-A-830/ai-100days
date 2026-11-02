# Game Brief: Signal Lost

**One-sentence pitch:** Scavenge, repair, and reboot a dying satellite relay station before its orbit decays and the signal is lost forever.

## Core loop
- Scan nearby debris field for salvageable parts
- Haul parts back to the station under a ticking orbital-decay clock
- Repair/install a module, restoring one system
- Each repaired system buys more time or reveals new debris to scan further out

## Player goal & fail state — what "working" looks like
Fully restore the relay station (all core systems repaired) before the orbital decay timer hits zero, re-establishing the signal. Fail state: the decay timer reaches zero with critical systems still offline — the station burns up and the run ends.

## MVP — what must exist to be the game
- Orbital decay timer that drives urgency
- Debris field with scannable salvage spots
- Haul/carry mechanic with limited capacity
- Station with 3–4 repairable systems/modules
- Repair action that consumes parts and restores a system
- Win/loss screen on full-repair or timer expiry

## Out of scope — not building this
- No multiplayer
- No persistent meta-progression between runs
- No crafting/combining parts (parts map 1:1 to systems)
- One station layout only
- No enemies/hazards in the debris field

## Build order
1. Decay timer + win/loss screen (prove the core tension)
2. Debris field + scan + haul
3. Station + repair action tying it together

---
**Who it's for / what they feel:** Solo players who like tense, short "just one more repair" sessions, ~10–15 min per run.

**Art & audio direction:** Dim functional sci-fi — flickering readouts, muted metal tones, low hum/alarm audio cues.

**Reference game:** Keep Talking and Nobody Explodes — the ticking-clock task-under-pressure feel, without the multiplayer/communication gimmick.
