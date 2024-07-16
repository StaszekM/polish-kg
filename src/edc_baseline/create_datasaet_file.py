import pandas as pd
import os
from .remove_entity_tags import remove_entity_tags


def create_dataset_file(tsv_path: str, output_path: str, verbose: bool = False):
    directory = os.path.dirname(output_path)

    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        if verbose:
            print(f"Directory {directory} missing, created")

    df = pd.read_csv(tsv_path, sep="\t")

    required_columns = ["text"]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' is missing in the DataFrame.")
        if df[column].dtype != "object":
            raise TypeError(f"Column '{column}' should have dtype 'object' (string).")

    if verbose:
        print(f"Loaded {tsv_path} with {len(df)} rows")

    result_series = df.apply(
        lambda row: remove_entity_tags(row["text"]),
        axis=1,
    )

    if verbose:
        print("Writing to", output_path)

    result_series.to_csv(output_path, index=False, header=False)
