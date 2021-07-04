import pathlib as pt

from setuptools import find_packages, setup

base_filepath = pt.Path("requirements") / "base.in"
with open(base_filepath) as fh:
    install_reqs = fh.readlines()

setup(
    packages=find_packages(),
    package_data={
        "waterer_backend": ["config/*.json"],
    },
    install_requires=install_reqs,
)
