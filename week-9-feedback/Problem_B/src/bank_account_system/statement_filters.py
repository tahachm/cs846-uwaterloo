class StatementTransactionFilter:
    def select(self, transactions, closing_balance):
        if closing_balance != 0:
            return tuple(transactions)

        return tuple(
            transaction
            for transaction in transactions
            if not self._is_terminal_zero_marker(transaction)
        )

    def _is_terminal_zero_marker(self, transaction):
        return transaction.transaction_type == "withdrew" and transaction.balance_after == 0