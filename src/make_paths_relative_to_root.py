from os import chdir, getenv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def make_paths_relative_to_root():
    """Always use the same, absolute (relative to root) paths

    which makes moving the notebooks around easier.
    """
    top_level = getenv("PYTHONPATH")
    if top_level is None:
        raise ValueError("PYTHONPATH not set, check .env file")

    chdir(top_level)


make_paths_relative_to_root()
