import os
from setuptools import setup


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="pyipums",
    author="Francisco Javier Arceo",
    author_email="franciscojavierarceo@users.noreply.github.com",
    url="https://github.com/franciscojavierarceo/pyipums",
    description="PyIPUMS is a library for working with data from IPUMS.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["pyipums"],
    keywords="ipums census ACS",
    python_requires=">=3.8",
    version="0.0.3",
)
