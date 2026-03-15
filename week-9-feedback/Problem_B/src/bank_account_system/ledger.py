from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Transaction:
    transaction_type: str
    amount: float
    balance_after: float
    created_at: datetime


class TransactionLedger:
    def __init__(self, entries=None):
        self._entries = list(entries) if entries is not None else []

    def record(self, transaction_type, amount, balance_after):
        transaction = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance_after,
            created_at=datetime.now(timezone.utc),
        )
        self._entries.append(transaction)
        return transaction

    def all_entries(self):
        return tuple(self._entries)