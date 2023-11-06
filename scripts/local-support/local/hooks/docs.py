import argparse
import re
from typing import List

from local import docs


def run(updated_files: List[str], format_: str, filename: str) -> bool:
    updated_services = set()
    for updated_file in updated_files:
        search = re.search("^services/(.*?)/", updated_file)
        if search:
            updated_services.add(search.group(1))
    updated: bool = False
    for project_name in updated_services:
        try:
            new_docs_filename = docs.run(
                project_name=project_name,
                app_template="{module_name}.routers:app",
                format_=format_,
                filename=filename,
            )
            if new_docs_filename:
                print(f"Service {project_name} update docs file: {new_docs_filename}")
                updated = True
        except docs.NotGenDocs:
            # skip if service doesn't match pattern
            pass
    return updated


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("updated_files", nargs="+", default=[])
    parser.add_argument("--format", default="yaml", type=str, choices=list(docs.SERIALIZERS.keys()))
    parser.add_argument("--filename", default="api", type=str)
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Search updated service and gen docs"))
    args = parser.parse_args()
    updated = run(updated_files=args.updated_files, format_=args.format, filename=args.filename)
    exit(int(updated))


if __name__ == "__main__":
    main()
