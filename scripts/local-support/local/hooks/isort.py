import argparse
import collections
import re
import subprocess
import sys
from typing import List


def _run(command: List[str]) -> int:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode:
        print(" ".join(command))

    print(stderr.decode(), file=sys.stderr)
    print(stdout.decode())
    return process.returncode


def run_isort(updated_files: List[str], known_local_folder: str) -> int:
    if known_local_folder:
        return _run(["isort", "--known-local-folder", known_local_folder, "--filter-files", *updated_files])
    else:
        return _run(["isort", "--filter-files", *updated_files])


def run(updated_files: List[str]) -> int:
    module_names = collections.defaultdict(list)
    for updated_file in updated_files:
        search = re.search("^(libraries|services|scripts)/.*?/(.*?)/", updated_file)
        module_name = search.group(2) if search else ""
        module_names[module_name].append(updated_file)

    result = 0
    for module_name, module_updated_files in module_names.items():
        result += run_isort(module_updated_files, module_name)
    return result


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("updated_files", nargs="+", default=[])
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Run isort with --known-local-folder"))
    args = parser.parse_args()
    exit(run(updated_files=args.updated_files))


if __name__ == "__main__":
    main()
