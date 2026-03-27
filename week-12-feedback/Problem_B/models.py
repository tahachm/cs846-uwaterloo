from dataclasses import dataclass


@dataclass
class Event:
    event_id: int
    user_id: int
    event_type: str   # login, click, purchase, logout
    value: int        # purchase value for purchase, otherwise 0
    ts: int           # simulated timestamp