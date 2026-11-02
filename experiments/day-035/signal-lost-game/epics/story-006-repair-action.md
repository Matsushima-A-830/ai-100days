# Story 006: Repair action

> **Epic**: Signal Lost
> **Status**: Complete
> **Layer**: Core
> **Type**: Logic
> **Estimate**: M
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: 2026-11-02

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 5 — repair action that consumes parts and restores a system

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

- [ ] The player can trigger a repair action on an Offline station system while holding the matching part (delivered via Story 004)
- [ ] A successful repair consumes the part (removes it from held parts) and sets the targeted system to Repaired (via Story 005)
- [ ] Repair is rejected if the player does not hold the required part, or the system is already Repaired
- [ ] A successful repair extends or slows the orbital decay timer (Story 001), per the brief's core loop ("each repaired system buys more time")
- [ ] Parts map 1:1 to systems — no crafting or combining parts (per the brief's out-of-scope list)

---

## Implementation Notes

No ADR exists at this tier. This story is the integration point that ties
Stories 001, 004 and 005 together — keep it as a single orchestrating method
(check held part → consume part → set system state → extend timer) rather than
scattering the logic across the other stories' classes.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- Story 001: the timer's own countdown logic (this story only calls its "extend" hook)
- Story 004: carrying/holding the part (this story only consumes it)
- Story 005: the system's Offline/Repaired state storage (this story only calls its state-change method)

---

## Files

- Assets/Scripts/Station/RepairAction.cs
- Assets/Scripts/Player/HaulController.cs (modified: added TryRemove)
- Assets/Scripts/Debris/PartDefinition.cs (modified: added TargetSystemName)

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above.*

---

## Test Evidence

*Governed by `qa.level: minimal` — tests are waived (advisory).*

**Story Type**: Logic
**Required evidence**:
- Logic: `Assets/Tests/EditMode/Station/RepairActionTests.cs` — advisory at `qa.level: minimal`

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: production/epics/signal-lost/story-001-decay-timer.md, production/epics/signal-lost/story-004-haul-mechanic.md, production/epics/signal-lost/story-005-station-systems.md
- Unlocks: None

## Completion Notes
**Completed**: 2026-11-02
**Criteria**: 5/5 passing (none deferred)
**Deviations**: HaulController.TryRemove() and PartDefinition.TargetSystemName added beyond the original Files list, to satisfy acceptance criteria 2 and 5; approved before writing
**Test Evidence**: waived at qa.level minimal
**Reviewed by**: self, no independent review (solo mode)
