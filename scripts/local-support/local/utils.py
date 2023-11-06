import re
import subprocess
import sys
from typing import List


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
