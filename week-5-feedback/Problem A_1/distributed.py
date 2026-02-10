# distributed.py
from dataset import ToyDataset
from formatter import collate_batch
from model import ToyModel
from utils import save_checkpoint, log
from trainer import train_epoch

def main():
    # "Entry point" for the repo
    cfg = {
        "epochs": 2,
        "batch_size": 3,
        "lr": 0.1,
        "checkpoint_path": "checkpoints/model.pt",
    }

    log("Initializing dataset")
    ds = ToyDataset(path="data/train.txt")

    log("Building model")
    model = ToyModel(hidden=4)

    log("Starting training loop")
    for epoch in range(cfg["epochs"]):
        metrics = train_epoch(
            model=model,
            dataset=ds,
            batch_size=cfg["batch_size"],
            lr=cfg["lr"],
            collate_fn=collate_batch,
        )
        log(f"epoch={epoch} metrics={metrics}")

    log("Saving checkpoint")
    save_checkpoint(model, cfg["checkpoint_path"])
    log("Done")

if __name__ == "__main__":
    main()
