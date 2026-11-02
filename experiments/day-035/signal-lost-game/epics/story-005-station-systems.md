# Story 005: Station with repairable systems

> **Epic**: Signal Lost
> **Status**: Complete
> **Layer**: Core
> **Type**: Integration
> **Estimate**: M
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: 2026-11-02

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 4 — station with 3-4 repairable systems/modules

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

- [ ] The station has 3-4 named systems/modules, each with an Offline/Repaired state
- [ ] Each system starts Offline at the beginning of a run
- [ ] A system's state change (Offline → Repaired) is observable by other systems (win condition, UI)
- [ ] A "all systems repaired" check/event is exposed for Story 002's win screen to consume
- [ ] There is exactly one station layout for the MVP (no alternate layouts, per the brief's out-of-scope list)

---

## Implementation Notes

No ADR exists at this tier. Model each system as a simple data object (name,
state) rather than a full subclass hierarchy, since all MVP systems behave
identically (Offline/Repaired, no unique behaviour per system type). Story 006
calls into this to flip a system's state.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- Story 006: the repair action itself (consuming a part, calling into this story's state-change method)
- Story 002: the win/loss screen presentation

---

## Files

- Assets/Scripts/Station/RepairableSystem.cs
- Assets/Scripts/Station/Station.cs

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above.*

---

## Test Evidence

*Governed by `qa.level: minimal` — tests are waived (advisory).*

**Story Type**: Integration
**Required evidence**:
- Integration: `Assets/Tests/EditMode/Station/StationTests.cs` OR playtest doc — advisory at `qa.level: minimal`

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: None
- Unlocks: production/epics/signal-lost/story-002-win-loss-screen.md, production/epics/signal-lost/story-006-repair-action.md

## Completion Notes
**Completed**: 2026-11-02
**Criteria**: 5/5 passing (none deferred)
**Deviations**: None
**Test Evidence**: waived at qa.level minimal
**Reviewed by**: self, no independent review (solo mode)
