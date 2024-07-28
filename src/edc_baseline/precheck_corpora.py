import pandas as pd
from argparse import ArgumentParser
import os


def precheck_corpora(tsv_path: str, output_path: str, verbose: bool = False):
    directory = os.path.dirname(output_path)

    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        if verbose:
            print(f"Directory {directory} missing, created")
    df = pd.read_csv(tsv_path, sep="\t")

    if verbose:
        print(f"Loaded {tsv_path} with {len(df)} rows")

        print("Missing values:")
        print(pd.isna(df).sum())

    df = df.dropna()

    df.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    from src.make_paths_relative_to_root import *

    parser = ArgumentParser()
    parser.add_argument("--tsv_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    precheck_corpora(args.tsv_path, args.output_path, args.verbose)
