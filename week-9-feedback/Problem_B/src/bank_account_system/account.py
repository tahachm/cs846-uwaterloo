from datetime import datetime, timezone

from .ledger import Transaction, TransactionLedger
from .notifications import AccountNotifier
from .validators import (
    validate_deposit_amount,
    validate_initial_balance,
    validate_withdrawal_amount,
)


class BankAccount:
    def __init__(self, initial_balance=0, notification_system=None, owner_name="Customer"):
        validate_initial_balance(initial_balance)
        self._balance = initial_balance
        self.owner_name = owner_name
        self._ledger = TransactionLedger()
        self._notifier = AccountNotifier(notification_system)
        self._ledger.record("account_opened", initial_balance, initial_balance)

    def deposit(self, amount):
        validate_deposit_amount(amount)
        next_balance = self._balance + amount
        transaction = self._build_pending_transaction("deposited", amount, next_balance)
        self._notifier.send_transaction_alert(transaction)
        self._balance = next_balance
        self._ledger.record("deposited", amount, self._balance)

    def withdraw(self, amount):
        validate_withdrawal_amount(amount, self._balance)
        next_balance = self._balance - amount
        transaction = self._build_pending_transaction("withdrew", amount, next_balance)
        self._notifier.send_transaction_alert(transaction)
        self._balance = next_balance
        self._ledger.record("withdrew", amount, self._balance)

    def get_balance(self):
        return self._balance

    def get_transaction_history(self):
        return self._ledger.all_entries()

    @property
    def balance(self):
        return self._balance

    def _build_pending_transaction(self, transaction_type, amount, balance_after):
        return Transaction(
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance_after,
            created_at=datetime.now(timezone.utc),
        )