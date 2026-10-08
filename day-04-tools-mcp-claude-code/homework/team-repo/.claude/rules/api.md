---
paths: ["src/api/**"]
---

Every handler returns `{"data": ...}` on success or `{"error": {"code", "message"}}` on failure.
Error codes are snake_case: not_found, invalid_input, forbidden.
Never raise from a handler; return the error shape.
