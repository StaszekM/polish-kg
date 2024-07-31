import pandas as pd
import os
from argparse import ArgumentParser
import dotenv

dotenv.load_dotenv()

translations_location = os.getenv("ENTITY_RELATION_MULTILINGUAL_TRANSLATIONS")
assert (
    translations_location is not None
), "Please set the environment variable ENTITY_RELATION_MULTILINGUAL_TRANSLATIONS"


def create_reference_file_from_df(
    df: pd.DataFrame, output_path: str, verbose: bool = False
) -> pd.Series:
    directory = os.path.dirname(output_path)

    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        if verbose:
            print(f"Directory {directory} missing, created")

    required_columns = ["entity_1", "entity_2", "label", "text"]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' is missing in the DataFrame.")
        if df[column].dtype != "object":
            raise TypeError(f"Column '{column}' should have dtype 'object' (string).")

    if verbose:
        print("Loading translations from", translations_location)

    translations = pd.read_csv(translations_location)

    df_merged = df.merge(translations, how="left", left_on="label", right_on="relation")
    if pd.isna(df_merged["translation"]).any():
        missing_translations = df_merged[pd.isna(df_merged["translation"])][
            "label"
        ].unique()
        raise ValueError("Missing translations for some labels: ", missing_translations)

    if verbose:
        print(f"Merged with translations, now have {len(df_merged)} rows")

    result_series = df_merged.apply(
        lambda row: [
            [row["entity_1"], row["translation"].replace("-", " "), row["entity_2"]]
        ],
        axis=1,
    )

    return result_series


def create_reference_file(tsv_path: str, output_path: str, verbose: bool = False):
    df = pd.read_csv(tsv_path, sep="\t")
    if verbose:
        print(f"Loaded {tsv_path} with {len(df)} rows")

    result_series = create_reference_file_from_df(df, output_path, verbose)

    if verbose:
        print("Writing to", output_path)

    with open(output_path, "w") as f:
        for line in result_series:
            f.write(str(line) + "\n")


if __name__ == "__main__":
    from src.make_paths_relative_to_root import *

    parser = ArgumentParser()
    parser.add_argument("--tsv_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    create_reference_file(args.tsv_path, args.output_path, args.verbose)
