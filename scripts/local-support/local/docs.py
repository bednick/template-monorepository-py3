"""
local.docs example-service
local.docs __all__
"""

import argparse
import functools
import json
import pathlib
import re
import sys
from typing import Optional

import fastapi
import yaml
from fastapi.openapi.utils import get_openapi

from local import utils


class NotGenDocs(Exception):
    pass


class ProjectNotFound(NotGenDocs):
    pass


class ApplicationNotFound(NotGenDocs):
    pass


SERIALIZERS = {
    "yaml": functools.partial(yaml.dump, sort_keys=False, encoding="utf-8", allow_unicode=True),
    "json": functools.partial(json.dump, ensure_ascii=False, indent=2),
}

DESERIALIZERS = {
    "yaml": yaml.safe_load,
    "json": json.load,
}


def run(project_name: str, app_template: str, format_: str, filename: str) -> Optional[str]:
    project_name = utils.clear_project_name(project_name)
    project_dir = pathlib.Path(f"./services/{project_name}")

    if not project_dir.is_dir():
        raise ProjectNotFound(f'Service "{project_name}" not found')

    # add path to source
    sys.path.append(str(project_dir.resolve()))
    module_name = utils.gen_module_name(project_name)
    app = app_template.format(module_name=module_name)
    module, application = app.split(":", maxsplit=1)

    try:
        fastapi_app = getattr(__import__(module, fromlist=[module]), application)
    except (AttributeError, ModuleNotFoundError) as exc:
        raise ApplicationNotFound(f"Error app value, {exc}")

    if not isinstance(fastapi_app, fastapi.FastAPI):
        raise ApplicationNotFound(f"Incorrect type fastapi application ({application}): {type(fastapi_app)}")

    openapi = get_openapi(
        title=fastapi_app.title,
        version=fastapi_app.version,
        openapi_version=fastapi_app.openapi_version,
        description=fastapi_app.description,
        routes=fastapi_app.routes,
    )

    docs_dir = project_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    docs_filename = docs_dir / f"{filename}.{format_}"

    if docs_filename.exists():
        try:
            with open(docs_filename, "r", encoding="utf-8") as fp:
                old_docs = DESERIALIZERS[format_](fp)  # type: ignore
            if old_docs == openapi:
                return None
        except Exception:  # noqa: ignore error file
            print(f"Incorrect yaml file {docs_filename}", file=sys.stderr)

    with open(docs_filename, "w", encoding="utf-8", newline="\n") as fp:
        SERIALIZERS[format_](openapi, fp)
    return str(docs_filename)


def app_template_regex_type(arg_value, pat=re.compile(r"^{module_name}.[_a-zA-Z]+:[_a-zA-Z]+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value, correct format: <package>.<module>:<app>")
    return arg_value


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("project_names", nargs="+", default=[], help="services names")
    parser.add_argument("--app-template", default="{module_name}.asgi:app", type=app_template_regex_type)
    parser.add_argument("--format", default="yaml", type=str, choices=list(SERIALIZERS.keys()))
    parser.add_argument("--filename", default="api", type=str)
    return parser


def _exec(project_name: str, app_template: str, format_: str, filename: str) -> int:
    try:
        new_docs_filename = run(project_name, app_template, format_, filename)
        if new_docs_filename:
            print(f"{project_name} service write docs file: {new_docs_filename}")
        else:
            print(f"{project_name} service documentation up-to-date, skip generate docs")
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Gen service docs"))
    args = parser.parse_args()
    if "__all__" in args.project_names:
        error_count = sum(
            _exec(
                project_name=service.name,
                app_template=args.app_template,
                format_=args.format,
                filename=args.filename,
            )
            for service in pathlib.Path("services").glob("*")
        )
    else:
        error_count = sum(
            _exec(
                project_name=project_name,
                app_template=args.app_template,
                format_=args.format,
                filename=args.filename,
            )
            for project_name in args.project_names
        )
    exit(error_count)


if __name__ == "__main__":
    main()
