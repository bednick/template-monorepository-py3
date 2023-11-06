"""
local.install -l
"""
import argparse
import pathlib
from typing import Literal

from local import utils


def install(prefix: str) -> int:
    root = pathlib.Path(prefix)

    result = 0
    for lib in root.glob("*"):
        command = ["pip", "install", "--no-deps", "-e", str(lib)]
        result += utils.cmd(command)
    return result


def run(install_type: Literal["libraries", "services"]) -> bool:
    print(f'Install  {install_type}" ...')
    return not bool(install(f"{install_type}"))


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--libraries", dest="install_type", action="store_const", const="libraries")
    group.add_argument("-s", "--services", dest="install_type", action="store_const", const="services")
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description=""))
    args = parser.parse_args()
    is_install = run(install_type=args.install_type)
    exit(int(not is_install))


if __name__ == "__main__":
    main()
