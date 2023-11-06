from setuptools import setup

setup(
    name="local-support",
    version="1.0.0",
    author="bednick",
    packages=["local"],
    install_requires=["wheel==0.37.1"],
    extras_require={
        "gen": ["Jinja2==3.1.2"],
        "docs": ["PyYAML==5.4.1", "fastapi==0.104.1"],
    },
    entry_points={
        "console_scripts": [
            "local.build_libraries = local.build_libraries:main",
            "local.build_service = local.build_service:main",
            "local.docker = local.docker:main",
            "local.docs = local.docs:main",
            "local.gen = local.gen:main",
            "local.install = local.install:main",
            # hooks
            "local.hooks.docs = local.hooks.docs:main",
            "local.hooks.isort = local.hooks.isort:main",
            "local.hooks.requirements = local.hooks.requirements:main",
        ],
    },
)
