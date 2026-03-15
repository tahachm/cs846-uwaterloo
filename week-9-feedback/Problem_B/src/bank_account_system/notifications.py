class AccountNotifier:
    def __init__(self, notification_channel=None):
        self._notification_channel = notification_channel

    def send_transaction_alert(self, transaction):
        if not self._notification_channel:
            return

        message = (
            f"{transaction.transaction_type.title()} {transaction.amount}, "
            f"new balance: {transaction.balance_after}"
        )
        self._notification_channel.notify(message)