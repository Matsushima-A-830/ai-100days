# Story 001: Orbital decay timer

> **Epic**: Signal Lost
> **Status**: Complete
> **Layer**: Foundation
> **Type**: Logic
> **Estimate**: S
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: 2026-11-02

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 1 — orbital decay timer that drives urgency

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

- [ ] A countdown timer exists that represents the station's orbital decay, counting down from a configured starting value
- [ ] The timer ticks down continuously during a run
- [ ] Reaching zero triggers a "decay complete" event/signal that other systems (win/loss screen) can observe
- [ ] Repairing a system (future story) can extend or slow the timer — expose a method to add time or adjust decay rate
- [ ] The current timer value is readable by other systems (e.g. for UI display)

---

## Implementation Notes

No ADR exists at this tier. Implement as a simple, testable countdown component
(e.g. a plain C# class driving the countdown logic, decoupled from any MonoBehaviour
so it can be unit tested without the Unity runtime). Expose an event for "timer
expired" and a method for extending time, since Story 006 (repair action) will
call into this.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- Story 002: the win/loss screen itself (this story only fires the expiry event)
- Story 006: the repair action that extends the timer (this story only exposes the hook)

---

## Files

- Assets/Scripts/Station/DecayTimer.cs

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above.*

---

## Test Evidence

*Governed by `qa.level: minimal` — tests are waived (advisory).*

**Story Type**: Logic
**Required evidence**:
- Logic: `Assets/Tests/EditMode/Station/DecayTimerTests.cs` — advisory at `qa.level: minimal`

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
