"""
local.docs --format yaml rcsc-packages
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


def run(project_name: str, app: Optional[str], format_: str, filename: str) -> Optional[str]:
    project_dir = pathlib.Path(f"./services/{project_name}")

    if not project_dir.is_dir():
        raise ProjectNotFound(f'Service "{project_name}" not found')

    # add path to source
    sys.path.append(str(project_dir.resolve()))
    app = app or f"{utils.gen_module_name(project_name)}.routers:app"
    module, application = app.split(":")

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
        with open(docs_filename, "r", encoding="utf-8") as fp:
            old_docs = DESERIALIZERS[format_](fp)  # type: ignore
        if old_docs == openapi:
            return None

    print("openapiopenapi", openapi.keys())

    with open(docs_filename, "w", encoding="utf-8", newline="\n") as fp:
        SERIALIZERS[format_](openapi, fp)
    return str(docs_filename)


def app_regex_type(arg_value, pat=re.compile(r"^[_a-zA-Z.]+:[_a-zA-Z]+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value, correct format: <package>.<module>:<app>")
    return arg_value


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("project_name", type=str, help="service name")
    parser.add_argument("--app", type=app_regex_type, required=False)
    parser.add_argument("--format", default="yaml", type=str, choices=list(SERIALIZERS.keys()))
    parser.add_argument("--filename", default="api", type=str)
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Gen service docs"))
    args = parser.parse_args()

    try:
        new_docs_filename = run(
            project_name=args.project_name,
            app=args.app,
            format_=args.format,
            filename=args.filename,
        )
        if new_docs_filename:
            print(f"write docs file: {new_docs_filename}")
        else:
            print(f"{args.project_name} service documentation up-to-date, skip generate docs")
        exit(0)
    except NotGenDocs as exc:
        print(exc, file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
