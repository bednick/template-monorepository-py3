import argparse
import pathlib
import subprocess
import sys
from typing import List, Optional


def _run(command: List[str]) -> int:
    print(" ".join(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(stderr.decode(errors="ignore"), file=sys.stderr)
    print(stdout.decode(errors="ignore"))

    return process.returncode


def build_service(
    root: str,
    wheels: List[str],
    dist: str = "dist",
    progress_bar: Optional[str] = None,
    trusted_host: Optional[str] = None,
    index_url: Optional[str] = None,
    use_deprecated: Optional[str] = None,
) -> int:
    command = ["pip", "wheel", "-w", dist, "-e", root]
    for wheel in wheels:
        command.extend(["--find-links", wheel])
    if trusted_host:
        command.extend(["--trusted-host", trusted_host])
    if index_url:
        command.extend(["--index-url", index_url])
    if use_deprecated:
        command.extend(["--use-deprecated", use_deprecated])
    if progress_bar:
        command.extend(["--progress-bar", progress_bar])

    return _run(command)


def run(
    project_name: str,
    wheels: List[str],
    dist: str,
    progress_bar: Optional[str],
    trusted_host: Optional[str],
    index_url: Optional[str],
    use_deprecated: Optional[str],
) -> int:
    if not pathlib.Path(f"./services/{project_name}").is_dir():
        print(f'Service "{project_name}" not found', file=sys.stderr)
        return 0

    result = build_service(
        f"./services/{project_name}",
        wheels=wheels,
        dist=dist,
        progress_bar=progress_bar,
        trusted_host=trusted_host,
        index_url=index_url,
        use_deprecated=use_deprecated,
    )

    return result


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("project_name", type=str, help="service name")
    parser.add_argument("--wheels", nargs="+", default=["./wheels", "./external-libraries"], help="path to wheels")
    parser.add_argument("--dist", default="./services/{project_name}/dist", type=str, help="path to dist")
    parser.add_argument("--progress-bar", type=str, help="", choices=["on", "off"])
    parser.add_argument("--trusted-host", type=str, help="")
    parser.add_argument("--index-url", type=str, help="")
    parser.add_argument("--use-deprecated", type=str, help="")
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Build service"))
    args = parser.parse_args()
    result = run(
        project_name=args.project_name,
        wheels=[wheel.format(project_name=args.project_name) for wheel in args.wheels],
        dist=args.dist.format(project_name=args.project_name),
        progress_bar=args.progress_bar,
        trusted_host=args.trusted_host,
        index_url=args.index_url,
        use_deprecated=args.use_deprecated,
    )
    exit(result)


if __name__ == "__main__":
    main()
