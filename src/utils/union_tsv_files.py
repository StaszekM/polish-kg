from typing import List
import pandas as pd
from argparse import ArgumentParser


def union_tsv_files(paths: List[str], output_tsv: str):
    """Union multiple TSV files into one.

    Args:
        paths (List[str]): List of paths to TSV files.
        output_tsv (str): Path to the output TSV file.
    """

    dfs = [pd.read_csv(path, sep="\t") for path in paths]
    df = pd.concat(dfs, ignore_index=True)

    df.to_csv(output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    from src.make_paths_relative_to_root import *

    parser = ArgumentParser()
    parser.add_argument("--paths", nargs="+", required=True)
    parser.add_argument("--output_tsv", type=str, required=True)

    args = parser.parse_args()

    union_tsv_files(args.paths, args.output_tsv)
