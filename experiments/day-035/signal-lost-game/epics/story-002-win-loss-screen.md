# Story 002: Win/loss screen

> **Epic**: Signal Lost
> **Status**: Complete
> **Layer**: Presentation
> **Type**: UI
> **Estimate**: S
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: 2026-11-02

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 6 — win/loss screen on full-repair or timer expiry

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

- [ ] A win screen appears when all station systems (Story 005) are fully repaired before the decay timer (Story 001) reaches zero
- [ ] A loss screen appears when the decay timer reaches zero while any system is still offline
- [ ] The run is considered over once either screen is shown — no further scan/haul/repair input is processed
- [ ] The screen clearly communicates which outcome occurred (win vs. loss) and is dismissible to restart or exit

---

## Implementation Notes

No ADR exists at this tier. Subscribe to Story 001's "timer expired" event and
Story 005's "all systems repaired" event (or equivalent polling) to decide which
screen to show. Keep this a thin presentation layer — the win/loss *logic* (what
counts as "all systems repaired") lives in Story 005, not here.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- Story 001: the countdown logic itself
- Story 005: what counts as "all systems repaired"

---

## Files

- Assets/Scripts/UI/WinLossScreen.cs
- Assets/UI/WinLossScreen.uxml

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above.*

---

## Test Evidence

*Governed by `qa.level: minimal` — tests are waived for Logic/Integration, but NOT for UI.*

**Story Type**: UI
**Required evidence**:
- UI: a retained screenshot of each screen touched, in `production/qa/evidence/`

**Status**: [x] Created — production/qa/evidence/story-002-win-loss-screen/ (2 screenshots: win and loss)

---

## Dependencies

- Depends on: production/epics/signal-lost/story-001-decay-timer.md, production/epics/signal-lost/story-005-station-systems.md
- Unlocks: None

## Completion Notes
**Completed**: 2026-11-02
**Criteria**: 4/4 passing (none deferred)
**Deviations**: Hardcoded UI strings violate .claude/rules/ui-code.md's localization requirement; accepted as known tech debt (no localization system exists yet in this project)
**Test Evidence**: production/qa/evidence/story-002-win-loss-screen/ (2 screenshots, stamped)
**Reviewed by**: self, no independent review (solo mode)
