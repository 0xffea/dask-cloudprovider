#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

import versioneer

setup(
    name="dask-cloud",
    cmdclass=versioneer.get_cmdclass(),
    version=versioneer.get_version(),
    description="Native Cloud integration for Dask",
    url="https://github.com/jacobtomlinson/dask-cloud",
    keywords="dask,cloud,distributed",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    long_description=(open("README.rst").read() if exists("README.rst") else ""),
    zip_safe=False,
    install_requires=list(open("requirements.txt").read().strip().split("\n")),
    python_requires=">=3.5",
)
