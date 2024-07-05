import pathlib
import re
import subprocess
import sys
from typing import List, Set


def parse_requirements(filename: pathlib.Path) -> Set[str]:
    results: Set[str] = set()
    if not filename.is_file():
        return results
    for line in filename.read_text("utf-8").split("\n"):
        line = line.split("#", maxsplit=1)[0].strip().lower()
        if line:
            results.add(line)
    return results


def cmd(command: List[str], quiet: bool = False) -> int:
    print(" ".join(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if not quiet:
        print(stderr.decode(), file=sys.stderr)
        print(stdout.decode())
    if process.returncode and quiet:
        print(stderr.decode(), file=sys.stderr)
    return process.returncode


def clear_project_name(project_name: str) -> str:
    chars = []
    last_delimiter = True
    for char in re.sub(r"([A-Z])", r" \1", project_name).lower():
        if re.match(r"[a-z0-9]", char):
            chars.append(char)
            last_delimiter = False
        else:
            if not last_delimiter:
                chars.append("-")
            last_delimiter = True
    clean_project_name = "".join(chars).strip("-")
    if not clean_project_name.replace("-", "_").isidentifier():
        raise ValueError(f"Incorrect {project_name=} {clean_project_name=}")
    return clean_project_name


def gen_module_name(project_name: str) -> str:
    return clear_project_name(project_name).replace("-", "_")
