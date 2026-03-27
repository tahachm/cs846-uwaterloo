import random
from models import Event


NORMAL_USERS = list(range(1000, 1031))
RESERVED_INVALID_USERS = [2001, 2002, 2003, 2004]


def generate_events(n: int = 20000) -> list[Event]:
    random.seed(11)

    events: list[Event] = []
    active_sessions: dict[int, int] = {}
    current_ts = 1_000_000

    # Generate a mostly valid stream using only NORMAL_USERS.
    for i in range(n - 4):
        current_ts += random.randint(1, 3)
        user_id = random.choice(NORMAL_USERS)

        if user_id not in active_sessions:
            event = Event(
                event_id=i,
                user_id=user_id,
                event_type="login",
                value=0,
                ts=current_ts,
            )
            active_sessions[user_id] = current_ts
        else:
            event_type = random.choices(
                ["click", "purchase", "logout"],
                weights=[70, 20, 10],
                k=1,
            )[0]

            if event_type == "click":
                event = Event(
                    event_id=i,
                    user_id=user_id,
                    event_type="click",
                    value=0,
                    ts=current_ts,
                )

            elif event_type == "purchase":
                event = Event(
                    event_id=i,
                    user_id=user_id,
                    event_type="purchase",
                    value=random.randint(100, 5000),
                    ts=current_ts,
                )

            else:  # logout
                event = Event(
                    event_id=i,
                    user_id=user_id,
                    event_type="logout",
                    value=0,
                    ts=current_ts,
                )
                active_sessions.pop(user_id, None)

        events.append(event)

    # Append exactly 4 isolated invalid events at the very end.
    # These use reserved user IDs that never appear in the normal stream,
    # so they cannot create downstream cascades.

    current_ts += 10
    events.append(
        Event(
            event_id=n - 4,
            user_id=RESERVED_INVALID_USERS[0],
            event_type="purchase",
            value=3200,
            ts=current_ts,
        )
    )  # purchase without active session

    current_ts += 10
    events.append(
        Event(
            event_id=n - 3,
            user_id=RESERVED_INVALID_USERS[1],
            event_type="logout",
            value=0,
            ts=current_ts,
        )
    )  # logout without active session

    current_ts += 10
    events.append(
        Event(
            event_id=n - 2,
            user_id=RESERVED_INVALID_USERS[2],
            event_type="purchase",
            value=-900,
            ts=current_ts,
        )
    )  # negative purchase value

    # Create a valid login first for reserved user 2004, but do it outside the returned stream
    # by seeding the processor's eventual state via a synthetic earlier timestamp in the invalid logout.
    # Since the processor only sees returned events, we instead force negative duration by having
    # the user log in immediately before in the normal stream would not be safe. So the cleanest way
    # is to make the processor track a seeded session for this reserved user from a bootstrap event.
    # To avoid changing processor logic, we include a real login event as the final valid event and
    # then one invalid logout after it.

    # Replace the previous last valid event with a deterministic login for reserved user 2004.
    bootstrap_ts = current_ts + 10
    events[-5] = Event(
        event_id=n - 5,
        user_id=RESERVED_INVALID_USERS[3],
        event_type="login",
        value=0,
        ts=bootstrap_ts,
    )

    events.append(
        Event(
            event_id=n - 1,
            user_id=RESERVED_INVALID_USERS[3],
            event_type="logout",
            value=0,
            ts=bootstrap_ts - 50,
        )
    )  # negative session duration

    return events