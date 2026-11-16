# Meeting: Billing API incident retro (2026-11-12)

Attendees: Daichi, Priya, Kenji

- Root cause: a timeout retry loop in the old billing API caused duplicate charges for 40 customers.
- Decided to add idempotency keys to the retry logic before the Q1 redesign starts.
- Action: Kenji to refund the affected 40 customers by end of week.
- Open question: should we postmortem this publicly on the status page?
