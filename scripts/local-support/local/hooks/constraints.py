import argparse
import pathlib
import sys
from typing import List

from local import utils


def run(updated_filenames: List[str], root_filename: str) -> int:
    root_file = pathlib.Path(root_filename)
    updated_files = {pathlib.Path(updated_filename) for updated_filename in updated_filenames}

    if not root_file.is_file():
        raise ValueError(f"Root file ({root_filename}) not found")
    if not all(updated_file.is_file() for updated_file in updated_files):
        raise ValueError("Updated file not found")

    root_requirements = utils.parse_requirements(root_file)

    result = 0
    for updated_file in updated_files:
        updated_file_requirements = utils.parse_requirements(updated_file)
        not_root = updated_file_requirements - root_requirements
        if not_root:
            print(f"File {updated_file} contains version that is not in the root file: {not_root}", file=sys.stderr)
            result += 1
    return result


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("updated_filenames", nargs="+", default=[])
    parser.add_argument("--root-filename", type=str, default="constraints.txt")
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Check requirements.txt by root constraints.txt"))
    args = parser.parse_args()
    exit(run(updated_filenames=args.updated_filenames, root_filename=args.root_filename))


if __name__ == "__main__":
    main()
