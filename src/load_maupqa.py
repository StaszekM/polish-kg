from typing import cast
from datasets import load_dataset, DatasetDict


def load_maupqa() -> DatasetDict:
    dataset = cast(
        DatasetDict,
        load_dataset("ipipan/maupqa", cache_dir="data/maupqa", trust_remote_code=True),
    )
    return dataset
