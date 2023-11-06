from pathlib import Path

from setuptools import find_packages, setup

with open(Path(__file__).parent.joinpath("requirements.txt")) as file:
    requirements = [line.strip() for line in file if line.strip()]

with open(Path(__file__).parent.joinpath("requirements-editable.txt")) as file:
    requirements_editable = [line.strip() for line in file if line.strip()]

setup(
    name="logging-settings",
    version="1.0.0",
    author="bednick",
    packages=find_packages(exclude=["tests_logging_settings"]),
    install_requires=requirements + requirements_editable,
)
