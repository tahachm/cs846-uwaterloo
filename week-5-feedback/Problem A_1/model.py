# model.py
class ToyModel:
    def __init__(self, hidden: int):
        self.hidden = hidden
        self.weights = [0.0] * hidden

    def forward(self, batch: dict) -> float:
        """
        Produces a fake scalar score from the batch.
        """
        return sum(batch["lengths"]) / (len(batch["lengths"]) + 1)

    def update(self, grad: float, lr: float) -> None:
        """
        Updates weights using a fake gradient.
        """
        self.weights = [w - lr * grad for w in self.weights]
