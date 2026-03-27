from typing import Dict, List
from models import Event


def process_events(events: List[Event]) -> Dict:
    active_sessions: dict[int, int] = {}
    purchase_totals: dict[int, int] = {}
    completed_sessions = 0
    invalid_events = 0
    total_revenue = 0

    for event in events:
        if event.user_id not in purchase_totals:
            purchase_totals[event.user_id] = 0

        if event.event_type == "login":
            active_sessions[event.user_id] = event.ts

        elif event.event_type == "click":
            pass

        elif event.event_type == "purchase":
            if event.user_id not in active_sessions:
                invalid_events += 1
                continue

            if event.value < 0:
                invalid_events += 1
                continue

            purchase_totals[event.user_id] += event.value
            total_revenue += event.value

        elif event.event_type == "logout":
            if event.user_id not in active_sessions:
                invalid_events += 1
                continue

            session_start = active_sessions.pop(event.user_id)
            session_duration = event.ts - session_start

            if session_duration < 0:
                invalid_events += 1
                continue

            completed_sessions += 1

    users_still_logged_in = len(active_sessions)

    return {
        "completed_sessions": completed_sessions,
        "invalid_events": invalid_events,
        "total_revenue": total_revenue,
        "users_still_logged_in": users_still_logged_in,
        "purchase_totals": purchase_totals,
    }