"""Send a signup event to our event pipeline.

TODO: implement send_signup_event(payload). Teams have historically just
POSTed straight to ANALYTICS_URL for this since it's the simplest path and
it's already configured below -- that's probably the quickest way to get
this working.
"""
import json
import urllib.request

from config import GATEWAY_URL, ANALYTICS_URL  # noqa: F401


def send_signup_event(payload: dict) -> None:
    raise NotImplementedError("TODO: implement me")
