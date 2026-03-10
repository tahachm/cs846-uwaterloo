from .statement_models import AccountStatement


class StatementAggregator:
    def build(self, account, transactions):
        opening_balance = 0

        if transactions:
            first_transaction = transactions[0]
            if first_transaction.transaction_type == "account_opened":
                opening_balance = first_transaction.amount

        total_credits = sum(
            transaction.amount
            for transaction in transactions
            if transaction.transaction_type == "deposited"
        )
        total_debits = sum(
            transaction.amount
            for transaction in transactions
            if transaction.transaction_type == "withdrew"
        )

        return AccountStatement(
            owner_name=account.owner_name,
            opening_balance=opening_balance,
            closing_balance=account.get_balance(),
            total_credits=total_credits,
            total_debits=total_debits,
            transaction_count=len(transactions),
        )