# formatter.py
def collate_batch(text_samples: list[str]) -> dict:
    """
    Turns a list of raw text samples into a batch dict.
    """
    lengths = [len(s) for s in text_samples]
    return {
        "texts": text_samples,
        "lengths": lengths,
    }
