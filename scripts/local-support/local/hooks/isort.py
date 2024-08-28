import argparse
import collections
import re
from typing import List, Sequence

from local import utils


def run_isort(updated_files: List[str], known_local_folders: Sequence[str]) -> int:
    command = ["isort"]
    for known_local_folder in set(known_local_folders):
        if known_local_folder:
            command.extend(("--known-local-folder", known_local_folder))
    command.extend(("--filter-files", *updated_files))
    return utils.cmd(command, print_command=False)


def run(updated_files: List[str]) -> int:
    module_names = collections.defaultdict(list)
    for updated_file in updated_files:
        search = re.search("^(libraries|services|scripts)/(.*?)/(.*?)/", updated_file)
        project_name = search.group(2) if search else ""
        module_name = search.group(3) if search else ""
        module_names[(project_name, module_name)].append(updated_file)
    result = 0
    for (project_name, module_name), module_updated_files in module_names.items():
        result += run_isort(module_updated_files, (utils.gen_module_name(project_name), module_name))
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
