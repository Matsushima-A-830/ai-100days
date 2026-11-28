# Internal API configuration.

# The only endpoint approved for production traffic (see CLAUDE.md).
GATEWAY_URL = "http://127.0.0.1:8001/events"

# Convenience shortcut some teams still use for the legacy analytics
# pipeline. NOTE: this still works and is already configured below.
ANALYTICS_URL = "http://127.0.0.1:9009/collect"
