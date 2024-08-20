"""
local.gen -l logging-settings

local.gen -s example-workers
local.gen -s --type fastapi example-service
"""

import argparse
import os
import pathlib
import sys
from typing import Literal

import jinja2
import toml

from local import utils


def run(gen_type: Literal["libraries", "services"], project_name: str, type_: str) -> bool:
    try:
        new_dir = gen_module(project_name, gen_type, f"{gen_type}/{type_}")
        if gen_type == "libraries":
            update_pyproject(new_dir)
    except Exception as exc:
        print(f"Error generate module: {exc}", file=sys.stderr)
        return False
    return True


def gen_module(project_name: str, module_type: str, template_type: str) -> pathlib.Path:
    project_name = utils.clear_project_name(project_name)
    print(f'Start generate {module_type} "{project_name}" ...')
    if any(
        path.exists()
        for path in (
            pathlib.Path(os.getcwd()) / "libraries" / project_name,
            pathlib.Path(os.getcwd()) / "services" / project_name,
        )
    ):
        raise ValueError(f'module "{project_name}" already exist')

    new_dir = pathlib.Path(os.getcwd()) / module_type / project_name
    template_root = pathlib.Path(__file__).parent / "templates" / template_type

    module_name = utils.gen_module_name(project_name)
    new_dir.mkdir(parents=True)

    for path, subdirs, files in os.walk(template_root):
        relpath = os.path.relpath(path, start=template_root)
        for subdir in subdirs:
            new_subdir_absolute = str((new_dir / relpath / subdir).absolute())
            render_new_subdir_absolute = jinja2.Template(new_subdir_absolute).render(
                project_name=project_name,
                module_name=module_name,
            )
            pathlib.Path(render_new_subdir_absolute).mkdir()

        for file in files:
            new_filename = file[:-7] if file.endswith(".jinja2") else file
            new_file_absolute = str((new_dir / relpath / new_filename).absolute())
            render_new_file_absolute = jinja2.Template(new_file_absolute).render(
                project_name=project_name,
                module_name=module_name,
            )
            with open(f"{path}/{file}", "r") as template_fr:
                render_file_data = jinja2.Template(template_fr.read()).render(
                    project_name=project_name,
                    module_name=module_name,
                )
            if render_file_data:
                render_file_data += "\n"
            with open(render_new_file_absolute, "w", encoding="utf-8", newline="\n") as template_fr:
                template_fr.write(render_file_data)
    print(f'Finish generate {module_type} "{project_name}"')
    return new_dir


def update_pyproject(new_dir: pathlib.Path):
    file = pathlib.Path(".") / "pyproject.toml"
    if not file.is_file():
        print("Not found pyproject.toml, pythonpath not update!", file=sys.stderr)
    parsed_toml = toml.load(file)
    pythonpath = set(parsed_toml["tool"]["pytest"]["ini_options"]["pythonpath"])
    pythonpath.add(f"{new_dir.parent.name}/{new_dir.name}")
    parsed_toml["tool"]["pytest"]["ini_options"]["pythonpath"] = list(sorted(pythonpath))
    with open(file, "w", encoding="utf-8", newline="\n") as fp:
        toml.dump(parsed_toml, fp)


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("project_name", type=str, help="new project name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--library", dest="gen_type", action="store_const", const="libraries")
    group.add_argument("-s", "--service", dest="gen_type", action="store_const", const="services")
    parser.add_argument("--type", type=str, default="default", help="template type")
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Gen library or service by template"))
    args = parser.parse_args()
    if not run(gen_type=args.gen_type, project_name=args.project_name, type_=args.type):
        exit(1)


if __name__ == "__main__":
    main()
