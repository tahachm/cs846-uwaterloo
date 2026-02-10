# utils.py
def log(msg: str) -> None:
    print(f"[LOG] {msg}")

def save_checkpoint(model, path: str) -> None:
    # Pretend checkpointing: just return a dict that would be saved.
    payload = {"hidden": model.hidden, "weights": model.weights}
    # No real file write to keep it simple for the exercise.
    log(f"Checkpoint payload prepared for path={path}: keys={list(payload.keys())}")
