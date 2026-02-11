from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = os.getenv("QUEUE_KEY", "applications:queue")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "3"))


class ATSClient:
    def submit(self, application: dict) -> dict:
        # Stubbed ATS integration point. Replace with vendor-specific adapters.
        return {
            "application_id": application["application_id"],
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": "submitted",
            "destination": application["job"]["apply_url"],
        }


def main() -> None:
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    ats = ATSClient()

    while True:
        _, payload = redis.blpop(QUEUE_KEY, timeout=POLL_SECONDS) or (None, None)
        if not payload:
            continue

        app_data = json.loads(payload)
        if app_data.get("auto_submit"):
            result = ats.submit(app_data)
            print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
