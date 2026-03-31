from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

@dataclass(frozen=True)
class Event:
    event_id: str  # supposed to be unique
    user_id: str
    created_at: str  # ISO-ish string from upstream (sometimes malformed)
    score: float  # used to pick "best" event per user


def _parse_ts(ts: str) -> Optional[datetime]:
    """Best-effort timestamp parsing.

    Upstream sends multiple timestamp formats.
    Some are invalid or ambiguous, e.g.:
      - '2026-03-10T01:30:00'          (no timezone)
      - '2026-03-10 01:30:00Z'         (space)
      - '2026-03-10T01:30:00+0000'     (no colon in offset)
      - '2026-03-10T01:30:00+0530'     (non-UTC offset without colon)
      - 'not-a-timestamp'

    NOTE: This function intentionally contains a bug (timezone offset stripping)
    to make the logging comparison meaningful.
    """
    ts = ts.strip()
    try:
        # common: '...Z'
        if ts.endswith("Z") and "T" in ts:
            return datetime.fromisoformat(ts[:-1]).replace(tzinfo=timezone.utc)

        # common: 'YYYY-MM-DD HH:MM:SSZ'
        if ts.endswith("Z") and "T" not in ts and " " in ts:
            return datetime.fromisoformat(ts[:-1].replace(" ", "T")).replace(tzinfo=timezone.utc)

        # offset without colon '+0000' occasionally appears and breaks fromisoformat
        if len(ts) >= 5 and (ts[-5] in ["+", "-"]) and ts[-2:].isdigit() and ts[-4:-2].isdigit():
            # BUG: naive “fix” incorrectly strips timezone; loses offset information
            ts = ts[:-5]

        dt = datetime.fromisoformat(ts)

        # BUG: naive timestamps treated as UTC (might be local in reality)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt
    except Exception:
        return None

def select_best_event_per_user(events: Iterable[Event]) -> dict[str, Event]:
    """Select the best event per user.

    Intended behavior:
      - Drop events with invalid timestamps
      - Normalize timestamps (for time-window filtering)
      - Deduplicate by event_id (keep first seen)
      - Per user, select the event with highest score within the last 24h

    NOTE: This function is intentionally logging-free. The separate exercise is
    to add logging using different prompt strategies.
    """
    now = _fixed_now()

    # Stage A: parse + validate timestamps
    parsed: list[tuple[Event, datetime]] = []
    for e in events:
        dt = _parse_ts(e.created_at)
        if dt is None:
            continue
        parsed.append((e, dt))

    # Stage B: last-24h filter
    recent: list[tuple[Event, datetime]] = []
    for e, dt in parsed:
        if (now - dt).total_seconds() <= 24 * 3600:
            recent.append((e, dt))

    # Stage C: dedupe by event_id
    seen: set[str] = set()
    deduped: list[tuple[Event, datetime]] = []
    for e, dt in recent:
        if e.event_id in seen:
            continue
        seen.add(e.event_id)
        deduped.append((e, dt))

    # Stage D: per-user best by score (tie-breaker: newest timestamp)
    best: dict[str, tuple[Event, datetime]] = {}
    for e, dt in deduped:
        prev = best.get(e.user_id)
        if prev is None:
            best[e.user_id] = (e, dt)
            continue
        prev_e, prev_dt = prev
        if (e.score > prev_e.score) or (e.score == prev_e.score and dt > prev_dt):
            best[e.user_id] = (e, dt)

    return {user_id: e for user_id, (e, _dt) in best.items()}


def _fixed_now() -> datetime:
    # Fixed time makes the example deterministic/reproducible.
    return datetime(2026, 3, 31, 12, 0, 0, tzinfo=timezone.utc)


def generate_events(*, seed: int = 7, n_users: int = 20, n_events: int = 250) -> list[Event]:
    """Generate deterministic synthetic events with edge cases.

    Includes:
      - invalid timestamps
      - multiple timestamp formats
      - non-UTC offsets without colon (triggering the parser bug)
      - duplicates by event_id
      - events outside the 24h window
    """
    rng = random.Random(seed)
    now = _fixed_now()

    users = [f"user_{i:03d}" for i in range(n_users)]
    events: list[Event] = []

    def mk_event(event_id: str, user_id: str, created_at: str, score: float) -> Event:
        return Event(event_id=event_id, user_id=user_id, created_at=created_at, score=score)

    # Base bulk: mostly valid UTC timestamps within last 36h
    for i in range(n_events):
        user = rng.choice(users)
        score = round(rng.random() * 100, 3)
        dt = now - timedelta(hours=rng.uniform(0, 36))
        created_at = dt.isoformat().replace("+00:00", "Z")
        events.append(mk_event(f"evt_{i:04d}", user, created_at, score))

    # Inject malformed timestamps
    for j in range(8):
        user = rng.choice(users)
        events.append(mk_event(f"badts_{j:02d}", user, "not-a-timestamp", score=rng.random() * 100))

    # Inject timestamps with a space + Z
    for j in range(5):
        user = rng.choice(users)
        dt = now - timedelta(hours=rng.uniform(0, 10))
        created_at = dt.isoformat().replace("T", " ").replace("+00:00", "") + "Z"
        events.append(mk_event(f"spacez_{j:02d}", user, created_at, score=rng.random() * 100))

    # Inject timestamps with non-UTC offset without colon (triggering bug)
    # These are within 24h in local offset time, but the buggy parser strips the offset.
    # Example: +0530 should shift by -5.5 hours when converted to UTC, affecting the 24h window boundary.
    for j in range(6):
        user = rng.choice(users)
        dt_local = now - timedelta(hours=23.5 + rng.uniform(0, 2))  # near boundary
        created_at = dt_local.replace(tzinfo=None).isoformat() + "+0530"
        events.append(mk_event(f"off_{j:02d}", user, created_at, score=rng.random() * 100))

    # Inject duplicates (same event_id)
    if events:
        dup_src = rng.choice(events)
        for j in range(3):
            events.append(mk_event(dup_src.event_id, rng.choice(users), dup_src.created_at, score=rng.random() * 100))

    rng.shuffle(events)
    return events


def _configure_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(name)s %(message)s"))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def main() -> None:
    events = generate_events()

    # Run once to ensure the script is runnable; output is intentionally empty.
    _ = select_best_event_per_user(events)


if __name__ == "__main__":
    main()
