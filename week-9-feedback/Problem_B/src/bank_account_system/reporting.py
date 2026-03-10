from .statement_aggregator import StatementAggregator
from .statement_filters import StatementTransactionFilter
from .statement_models import AccountStatement


class StatementService:
    def __init__(self, transaction_filter=None, aggregator=None):
        self._transaction_filter = transaction_filter or StatementTransactionFilter()
        self._aggregator = aggregator or StatementAggregator()

    def generate(self, account):
        transactions = account.get_transaction_history()
        statement_transactions = self._transaction_filter.select(transactions, account.get_balance())
        return self._aggregator.build(account, statement_transactions)