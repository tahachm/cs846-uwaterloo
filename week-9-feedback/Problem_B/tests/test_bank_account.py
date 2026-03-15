from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from bank_account_system import BankAccount  # noqa: E402
from bank_account_system.exceptions import (  # noqa: E402
    InvalidAmountError,
    NegativeBalanceError,
    OverdraftError,
)


class NotificationChannelStub:
    def __init__(self):
        self.messages = []

    def notify(self, message):
        self.messages.append(message)


class BankAccountTests(unittest.TestCase):
    def test_deposit_updates_balance(self):
        account = BankAccount(initial_balance=100)

        account.deposit(25)

        self.assertEqual(account.get_balance(), 125)

    def test_withdraw_updates_balance(self):
        account = BankAccount(initial_balance=100)

        account.withdraw(40)

        self.assertEqual(account.get_balance(), 60)

    def test_negative_initial_balance_rejected(self):
        with self.assertRaises(NegativeBalanceError):
            BankAccount(initial_balance=-1)

    def test_non_positive_deposit_rejected(self):
        account = BankAccount(initial_balance=100)

        with self.assertRaises(InvalidAmountError):
            account.deposit(0)

    def test_overdraft_rejected(self):
        account = BankAccount(initial_balance=100)

        with self.assertRaises(OverdraftError):
            account.withdraw(101)

    def test_notification_sent_after_deposit(self):
        notification_channel = NotificationChannelStub()
        account = BankAccount(initial_balance=100, notification_system=notification_channel)

        account.deposit(20)

        self.assertEqual(notification_channel.messages, ["Deposited 20, new balance: 120"])


if __name__ == "__main__":
    unittest.main()