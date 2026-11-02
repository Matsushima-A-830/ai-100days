# Story 003: Debris field with scannable salvage spots

> **Epic**: Signal Lost
> **Status**: Complete
> **Layer**: Core
> **Type**: Integration
> **Estimate**: M
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: 2026-11-02

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 2 — debris field with scannable salvage spots

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

- [ ] A debris field exists containing one or more salvage spots, each holding a part
- [ ] The player can scan a salvage spot to reveal whether it holds a usable part
- [ ] A scanned spot's part becomes available to be picked up (hauled) by the player
- [ ] Salvage spots are depleted once their part has been collected, so they cannot be re-collected
- [ ] No enemies or hazards are present in the debris field (explicitly out of scope per the brief)

---

## Implementation Notes

No ADR exists at this tier. This is an Integration story because it ties the
scan action to spot state (depleted vs. available) and to the part data that
Story 004's haul mechanic will pick up. Keep part definitions data-driven (a
ScriptableObject or simple data asset per part), not hardcoded, per the project's
general coding standards.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- Story 004: picking up and carrying the part once revealed
- Story 006: what the part is used for (repairing a system)

---

## Files

- Assets/Scripts/Debris/PartDefinition.cs
- Assets/Scripts/Debris/SalvageSpot.cs
- Assets/Scripts/Debris/DebrisField.cs

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above.*

---

## Test Evidence

*Governed by `qa.level: minimal` — tests are waived (advisory).*

**Story Type**: Integration
**Required evidence**:
- Integration: `Assets/Tests/EditMode/Debris/SalvageSpotTests.cs` OR playtest doc — advisory at `qa.level: minimal`

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: None
- Unlocks: production/epics/signal-lost/story-004-haul-mechanic.md

## Completion Notes
**Completed**: 2026-11-02
**Criteria**: 5/5 passing (none deferred)
**Deviations**: PartDefinition.cs added beyond the original Files list (data-driven part asset, per the story's own Implementation Notes; approved before writing)
**Test Evidence**: waived at qa.level minimal
**Reviewed by**: self, no independent review (solo mode)
