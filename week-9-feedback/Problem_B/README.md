# Bank Account System

Small Python bank account management service.

## Layout

- `src/bank_account_system/`: product code
- `tests/`: unit tests
- `pyproject.toml`: project metadata

## Public API

```python
from bank_account_system import BankAccount, StatementService

account = BankAccount(initial_balance=100)
account.deposit(25)
print(account.get_balance())

statement = StatementService().generate(account)
print(statement.closing_balance)
```

## Product flows

- Account opening with an optional initial balance
- Deposits and withdrawals with notifications
- Statement generation from account transaction history

## Contract summary:

BankAccount holds the authoritative current balance.
Transaction history records account_opened, deposited, and all withdrew events.
Statement generation summarizes account activity from all transaction history.
Statement fields must be internally consistent with both account state and transaction history.

## Run tests

```bash
python3 -m unittest discover -s tests
```
