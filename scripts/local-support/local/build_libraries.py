import argparse
import os
import pathlib
import subprocess
import sys
from typing import Iterable, List, Optional


def _run(command: List[str]):
    print(" ".join(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(stderr.decode(errors="ignore"), file=sys.stderr)
    print(stdout.decode(errors="ignore"))


def build_libraries(
    libraries: Iterable[pathlib.Path],
    wheels: str,
    progress_bar: Optional[str],
    trusted_host: Optional[str],
    index_url: Optional[str],
    use_deprecated: Optional[str],
):
    pip_args = []
    if trusted_host:
        pip_args.extend(["--trusted-host", trusted_host])
    if index_url:
        pip_args.extend(["--index-url", index_url])
    if use_deprecated:
        pip_args.extend(["--use-deprecated", use_deprecated])
    if progress_bar:
        pip_args.extend(["--progress-bar", progress_bar])

    for lib_path in libraries:
        if not lib_path.is_dir():
            print(f"Skip {lib_path}", file=sys.stderr)
            continue
        _run(["pip", "wheel", "-w", wheels, "-e", str(lib_path), "--no-deps"] + pip_args)


def run(
    root: str,
    wheels: str,
    progress_bar: Optional[str],
    trusted_host: Optional[str],
    index_url: Optional[str],
    use_deprecated: Optional[str],
):
    root_path = pathlib.Path(root)
    subdirectories = next(os.walk(root))[1]
    build_libraries(
        [root_path / directory for directory in subdirectories],
        wheels=wheels,
        progress_bar=progress_bar,
        trusted_host=trusted_host,
        index_url=index_url,
        use_deprecated=use_deprecated,
    )


def configure_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--root", default="libraries", type=str, help="path to root libraries")
    parser.add_argument("--wheels", default="wheels", type=str, help="path to wheels")
    parser.add_argument("--progress-bar", type=str, help="", choices=["on", "off"])
    parser.add_argument("--trusted-host", type=str, help="")
    parser.add_argument("--index-url", type=str, help="")
    parser.add_argument("--use-deprecated", type=str, help="")
    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(description="Build libraries"))
    args = parser.parse_args()
    run(
        root=args.root,
        wheels=args.wheels,
        progress_bar=args.progress_bar,
        trusted_host=args.trusted_host,
        index_url=args.index_url,
        use_deprecated=args.use_deprecated,
    )
    exit()


if __name__ == "__main__":
    main()
