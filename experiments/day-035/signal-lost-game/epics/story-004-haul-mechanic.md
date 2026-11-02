# Story 004: Haul/carry mechanic with limited capacity

> **Epic**: Signal Lost
> **Status**: Complete
> **Layer**: Core
> **Type**: Logic
> **Estimate**: M
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: 2026-11-02

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 3 — haul/carry mechanic with limited capacity

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Unity 6000.2.11f1 | **Risk**: MEDIUM
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**:
- N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md`, scoped to this story:*

- [ ] The player has a carry capacity (a fixed maximum number of parts they can hold at once)
- [ ] Picking up a revealed part (from Story 003) adds it to the player's held parts, up to capacity
- [ ] Attempting to pick up a part while at capacity is rejected (no overflow)
- [ ] The player can deliver held parts to the station, clearing them from their held parts
- [ ] The player's current held-parts count is readable by other systems (e.g. for UI display)

---

## Implementation Notes

No ADR exists at this tier. Implement as a plain, unit-testable class (capacity,
current held parts, add/remove methods) decoupled from movement/input so it can
be tested without the Unity runtime. This is the mechanic that creates the
brief's core tension (limited trips under a ticking clock) — keep the capacity
value data-driven, not hardcoded.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- Story 003: revealing/depleting the salvage spot the part comes from
- Story 006: what happens to a delivered part (the repair action)

---

## Files

- Assets/Scripts/Player/HaulController.cs

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above.*

---

## Test Evidence

*Governed by `qa.level: minimal` — tests are waived (advisory).*

**Story Type**: Logic
**Required evidence**:
- Logic: `Assets/Tests/EditMode/Player/HaulControllerTests.cs` — advisory at `qa.level: minimal`

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: production/epics/signal-lost/story-003-debris-field.md
- Unlocks: production/epics/signal-lost/story-006-repair-action.md

## Completion Notes
**Completed**: 2026-11-02
**Criteria**: 5/5 passing (none deferred)
**Deviations**: None
**Test Evidence**: waived at qa.level minimal
**Reviewed by**: self, no independent review (solo mode)
