import argparse
import os
import pathlib
import sys
from typing import List, Optional

from local import utils

ALL = "__all__"


def build_docker(dockerfile: str, project_name: str, build_arg: Optional[List[str]], quiet: bool = False) -> int:
    command = ["docker", "build", "-t", project_name, "-f", dockerfile, "."]
    for arg in build_arg or []:
        command.extend(["--build-arg", arg])
    return utils.cmd(command, quiet=quiet)


def run(project_name: str, dockerfile: str, build_arg: Optional[List[str]], quiet: bool) -> int:
    if project_name == ALL:
        subdirectories = next(os.walk("services"))[1]
        return sum(
            build_docker(f"./services/{subdirectory}/{dockerfile}", subdirectory, build_arg, quiet=quiet)
            for subdirectory in subdirectories
        )
    else:
        if not pathlib.Path(f"./services/{project_name}").is_dir():
            print(f'Service "{project_name}" not found', file=sys.stderr)
            return -1

        return build_docker(f"./services/{project_name}/{dockerfile}", project_name, build_arg, quiet=quiet)


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("project_name", type=str, help=f"service name or {ALL}")
    parser.add_argument("--dockerfile", type=str, default="Dockerfile", help="dockerfile filename")
    parser.add_argument("--build-arg", action="append")
    parser.add_argument("--quiet", "-q", dest="quiet", action="store_true")
    parser.set_defaults(quiet=False)
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Build docker image"))
    args = parser.parse_args()
    exit(run(project_name=args.project_name, dockerfile=args.dockerfile, build_arg=args.build_arg, quiet=args.quiet))


if __name__ == "__main__":
    main()
