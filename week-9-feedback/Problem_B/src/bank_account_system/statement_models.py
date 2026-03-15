from dataclasses import dataclass


@dataclass(frozen=True)
class AccountStatement:
    owner_name: str
    opening_balance: float
    closing_balance: float
    total_credits: float
    total_debits: float
    transaction_count: int