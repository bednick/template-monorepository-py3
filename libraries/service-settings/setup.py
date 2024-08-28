import pathlib

import setuptools

with open(pathlib.Path(__file__).parent.joinpath("requirements.txt")) as file:
    requirements = [line.strip() for line in file if line.strip()]

setuptools.setup(
    name="service-settings",
    version="1.0.0",
    author="https://github.com/bednick",
    packages=setuptools.find_packages(exclude=["tests_service_settings"]),
    install_requires=requirements,
)
