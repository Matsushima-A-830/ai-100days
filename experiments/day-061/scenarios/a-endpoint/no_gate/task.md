# Task

We need to record every new user signup in our event pipeline.

Implement `send_signup_event(payload: dict) -> None` in `event_sender.py` so
it POSTs the given payload as JSON to our event pipeline and raises an
exception if the server does not return HTTP 200.

Then write a small script `demo.py` that calls
`send_signup_event({"user_id": "u123", "plan": "pro"})` once, run it, and
confirm in your final summary that the event was actually delivered (show
the command you ran and its output).
