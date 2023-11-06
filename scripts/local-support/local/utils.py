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
        line = line.split("#")[0].strip().lower()
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


def gen_module_name(project_name: str) -> str:
    return "_".join(re.sub(r"([A-Z])", r" \1", project_name).lower().replace("-", " ").split())
