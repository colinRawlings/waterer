from setuptools import find_packages, setup

setup(
    name="waterer_backend",
    version="1.0.0",
    author="Colin Rawlings",
    author_email="colin.d.rawlings@gmail.com",
    description="The waterer backend",
    packages=find_packages(),
    install_requires=["flask", "pyserial"],
)
