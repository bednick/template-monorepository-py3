"""
local.install -l
local.install -s
local.install -ls
local.install --libraries --services
"""

import argparse
import pathlib
from typing import Literal

from local import utils


def install(prefix: str) -> int:
    root = pathlib.Path(prefix)
    result = 0
    for lib in root.glob("*"):
        result += utils.cmd(["pip", "install", "--no-deps", "-e", str(lib)])
    return result


def run(install_type: Literal["libraries", "services"]) -> bool:
    print(f'Install "{install_type}" ...')
    return not bool(install(f"./{install_type}"))


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-l", "--libraries", dest="libraries", action="store_true")
    parser.add_argument("-s", "--services", dest="services", action="store_true")
    parser.set_defaults(libraries=False, services=False)
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description=""))
    args = parser.parse_args()
    if args.libraries:
        run(install_type="libraries")
    if args.services:
        run(install_type="services")
    exit(0)


if __name__ == "__main__":
    main()
