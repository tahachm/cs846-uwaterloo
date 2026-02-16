# dataset.py
class ToyDataset:
    """
    Loads lines of text from a file and exposes them as samples.
    """
    def __init__(self, path: str):
        self.path = path
        # Pretend we loaded file content (avoid actual I/O for the exercise)
        self.samples = [
            "doc about cats",
            "doc about dogs",
            "doc about birds",
            "doc about fish",
            "doc about horses",
        ]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> str:
        return self.samples[idx]
