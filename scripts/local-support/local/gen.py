"""
local.gen -l logging-settings

local.gen -s example-workers
local.gen -s --type fastapi example-service
"""

import argparse

from local import generator


def run(gen_type: str, project_name: str, type_: str) -> bool:
    print(f'Generate {gen_type} "{project_name}" ...')

    if gen_type == "library":
        return generator.gen_module(project_name, "libraries", f"library/{type_}")
    elif gen_type == "service":
        return generator.gen_module(project_name, "services", f"service/{type_}")
    else:
        raise NotImplementedError


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("project_name", type=str, help="new project name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--library", dest="gen_type", action="store_const", const="library")
    group.add_argument("-s", "--service", dest="gen_type", action="store_const", const="service")
    parser.add_argument("--type", type=str, default="default", help="template type")
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Gen library or service/worker by template"))
    args = parser.parse_args()
    is_gen = run(gen_type=args.gen_type, project_name=args.project_name, type_=args.type)
    exit(int(not is_gen))


if __name__ == "__main__":
    main()
