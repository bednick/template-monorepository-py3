"""
local.requirements example-service

local.requirements __all__
"""

import argparse
import pathlib
import re
import sys
from typing import Set, Tuple

from local import utils


class NotGenRequirements(Exception):
    pass


class LibraryNotFound(NotGenRequirements):
    pass


class ProjectNotFound(NotGenRequirements):
    pass


def get_libraries_requirements(library_name: str) -> Tuple[Set[str], Set[str]]:
    library_dir = pathlib.Path(f"./libraries/{library_name}")
    if not library_dir.is_dir():
        raise LibraryNotFound(f'Library "{library_name}" not found')
    return (
        utils.parse_requirements(library_dir / "requirements.txt"),
        utils.parse_requirements(library_dir / "requirements-editable.txt"),
    )


def run(service_name: str, filename: str):
    service_dir = pathlib.Path(f"./services/{service_name}")
    if not service_dir.is_dir():
        raise ProjectNotFound(f'Service "{service_name}" not found')

    service_in = utils.parse_requirements(service_dir / "requirements.in")
    service_editable = utils.parse_requirements(service_dir / "requirements-editable.txt")

    service_requirements = set(service_in)
    checked_libraries = set()
    need_check_libraries = list(service_editable)
    while need_check_libraries:
        library_name = need_check_libraries.pop().split("[", maxsplit=1)[0]
        if library_name in checked_libraries:
            continue
        checked_libraries.add(library_name)
        library_requirements, library_editable = get_libraries_requirements(library_name)
        need_check_libraries.extend(library_editable)
        service_requirements.update(library_requirements)

    old_service_requirements = utils.parse_requirements(service_dir / filename)
    if old_service_requirements == service_requirements:
        return

    print(f"Update file {service_dir / filename}")
    with open(service_dir / filename, "w", encoding="utf-8", newline="\n") as fp:
        fp.write("\n".join(sorted(service_requirements, key=lambda line: line.split("=", maxsplit=1)[0])))
        fp.write("\n")


def app_regex_type(arg_value, pat=re.compile(r"^[_a-zA-Z.]+:[_a-zA-Z]+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value, correct format: <package>.<module>:<app>")
    return arg_value


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("service_name", type=str, help="service name")
    parser.add_argument("--filename", default="requirements.txt", type=str)
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Gen service requirements.txt"))
    args = parser.parse_args()

    try:
        if args.service_name == "__all__":
            for service in pathlib.Path("services").glob("*"):
                run(service_name=service.name, filename=args.filename)
        else:
            run(service_name=args.service_name, filename=args.filename)
        exit(0)
    except NotGenRequirements as exc:
        print(exc, file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
