import argparse
import pathlib
import re
from typing import List, Set

from local import docs, requirements


def run(updated_files: List[str], filename: str):
    updated_libraries = set()
    for updated_file in updated_files:
        search = re.search("^libraries/(.*?)/requirements(.*)txt", updated_file)
        if search:
            updated_libraries.add(search.group(1))

    updated_services: Set[str] = set()
    for updated_file in updated_files:
        search = re.search("^services/(.*?)/requirements(.*)txt", updated_file)
        if search:
            updated_services.add(search.group(1))

    if updated_libraries:
        gen_services = {lib.name for lib in pathlib.Path("services").glob("*")}
    else:
        gen_services = updated_services

    for service_name in gen_services:
        requirements.run(service_name, filename=filename)


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("updated_files", nargs="+", default=[])
    parser.add_argument("--format", default="yaml", type=str, choices=list(docs.SERIALIZERS.keys()))
    parser.add_argument("--filename", default="requirements.txt", type=str)
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Generate service requirements"))
    args = parser.parse_args()
    run(updated_files=args.updated_files, filename=args.filename)
    exit(0)


if __name__ == "__main__":
    main()
