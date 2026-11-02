# Epic: Signal Lost

> **Tier**: minimal
> **Source**: `design/game-brief.md`

## Goal

Scavenge, repair, and reboot a dying satellite relay station before its orbit
decays and the signal is lost forever.

## Scope

The brief's MVP list:
- Orbital decay timer that drives urgency
- Debris field with scannable salvage spots
- Haul/carry mechanic with limited capacity
- Station with 3-4 repairable systems/modules
- Repair action that consumes parts and restores a system
- Win/loss screen on full-repair or timer expiry

## Order

Per the brief's Build order:
1. Decay timer + win/loss screen (prove the core tension)
2. Debris field + scan + haul
3. Station + repair action tying it together

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Orbital decay timer | Logic | Ready | N/A (minimal) |
| 002 | Win/loss screen | UI | Ready | N/A (minimal) |
| 003 | Debris field with scannable salvage spots | Integration | Ready | N/A (minimal) |
| 004 | Haul/carry mechanic with limited capacity | Logic | Ready | N/A (minimal) |
| 005 | Station with repairable systems | Integration | Ready | N/A (minimal) |
| 006 | Repair action | Logic | Ready | N/A (minimal) |
