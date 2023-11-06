import setuptools

setuptools.setup(
    name="local-support",
    version="1.0.0",
    author="https://github.com/bednick",
    packages=["local"],
    install_requires=["wheel==0.37.1"],
    extras_require={
        "gen": ["jinja2==3.1.3"],
        "docs": ["pyyaml==6.0.1", "fastapi==0.110.0"],
    },
    entry_points={
        "console_scripts": [
            "local.docs = local.docs:main",
            "local.gen = local.gen:main",
            "local.install = local.install:main",
            "local.req = local.requirements:main",
            "local.requirements = local.requirements:main",
            # hooks
            "local.hooks.constraints = local.hooks.constraints:main",
            "local.hooks.docs = local.hooks.docs:main",
            "local.hooks.isort = local.hooks.isort:main",
            "local.hooks.requirements = local.hooks.requirements:main",
        ],
    },
)
