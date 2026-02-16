# trainer.py
from utils import log

def train_epoch(model, dataset, batch_size: int, lr: float, collate_fn):
    """
    Runs one training epoch over the dataset.
    """
    total_loss = 0.0
    n_batches = 0

    for start in range(0, len(dataset), batch_size):
        batch_texts = [dataset[i] for i in range(start, min(start + batch_size, len(dataset)))]
        batch = collate_fn(batch_texts)

        score = model.forward(batch)
        loss = 1.0 / (score + 1.0)  # fake "loss"

        # fake "gradient"
        grad = loss * 0.1
        model.update(grad=grad, lr=lr)

        total_loss += loss
        n_batches += 1

        log(f"batch_start={start} loss={loss:.4f}")

    return {"avg_loss": total_loss / max(n_batches, 1)}
