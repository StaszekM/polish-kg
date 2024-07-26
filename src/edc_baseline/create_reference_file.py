import pandas as pd
import os
from argparse import ArgumentParser


def create_reference_file(tsv_path: str, output_path: str, verbose: bool = False):
    translations_location = os.getenv("ENTITY_RELATION_MULTILINGUAL_TRANSLATIONS")
    assert (
        translations_location is not None
    ), "Please set the environment variable ENTITY_RELATION_MULTILINGUAL_TRANSLATIONS"

    directory = os.path.dirname(output_path)

    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        if verbose:
            print(f"Directory {directory} missing, created")

    df = pd.read_csv(tsv_path, sep="\t")

    required_columns = ["entity_1", "entity_2", "label", "text"]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' is missing in the DataFrame.")
        if df[column].dtype != "object":
            raise TypeError(f"Column '{column}' should have dtype 'object' (string).")

    if verbose:
        print(f"Loaded {tsv_path} with {len(df)} rows")
        print("Loading translations from", translations_location)

    translations = pd.read_csv(translations_location)

    df = df.merge(translations, how="inner", left_on="label", right_on="relation")
    if pd.isna(df["translation"]).any():
        missing_translations = df[pd.isna(df["translation"])]["label"].unique()
        raise ValueError("Missing translations for some labels: ", missing_translations)

    if verbose:
        print(f"Merged with translations, now have {len(df)} rows")

    result_series = df.apply(
        lambda row: [
            [row["entity_1"], row["translation"].replace("-", " "), row["entity_2"]]
        ],
        axis=1,
    )

    if verbose:
        print("Writing to", output_path)

    result_series.to_csv(output_path, index=False, header=False, sep="\n")


if __name__ == "__main__":
    from src.make_paths_relative_to_root import *

    parser = ArgumentParser()
    parser.add_argument("--tsv_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    create_reference_file(args.tsv_path, args.output_path, args.verbose)
