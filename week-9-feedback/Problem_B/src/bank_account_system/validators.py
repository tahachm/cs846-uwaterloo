from .exceptions import InvalidAmountError, NegativeBalanceError, OverdraftError


def validate_initial_balance(initial_balance):
    if initial_balance < 0:
        raise NegativeBalanceError("Initial balance cannot be negative.")


def validate_deposit_amount(amount):
    if amount <= 0:
        raise InvalidAmountError("Deposit amount must be positive.")


def validate_withdrawal_amount(amount, current_balance):
    if amount <= 0:
        raise InvalidAmountError("Withdrawal amount must be positive.")
    if amount > current_balance:
        raise OverdraftError("Cannot withdraw more than the current balance.")