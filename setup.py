#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# Copyright (c) 2019--, Clean development team.
#
# NOTE: This file is derived from Qurro's setup.py file.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import re, ast
from setuptools import find_packages, setup

classes = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Bio-Informatics
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: 3 :: Only
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
"""

description = (
    "metadata_clean is a metadata curation tool that applies rules form the user and passed as a yaml file."
)

with open("README.md") as f:
    long_description = f.read()


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("metadata_cleaning/__init__.py", "rb") as f:
    hit = _version_re.search(f.read().decode("utf-8")).group(1)
    version = str(ast.literal_eval(hit))

setup(
    name="metadata_cleaning",
    version=version,
    license="BSD",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Clean development team",
    author_email="flejzerowicz@ucsd.edu",
    maintainer="Clean development team",
    maintainer_email="flejzerowicz@ucsd.edu",
    #url="https://github.com/biocore/metadata_cleaning",
    packages=find_packages(),
    # Needed in order to ensure that support_files/*, etc. are installed (in
    # turn, these files are specified in MANIFEST.in).
    # See https://python-packaging.readthedocs.io/en/latest/non-code-files.html
    # for details.
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
        "jsonschema",
        "numpy",
        "pytest",
        "pandas"
    ],
    ## Based on how Altair splits up its requirements:
    ## https://github.com/altair-viz/altair/blob/master/setup.py
    #extras_require={
    #    "dev": ["pytest >= 4.2", "pytest-cov >= 2.0", "flake8", "black"]
    #},
    #classifiers=classifiers,
    #entry_points={
    #    "qiime2.plugins": ["q2-qurro=qurro.q2.plugin_setup:plugin"],
    #    "console_scripts": ["qurro=qurro.scripts._plot:plot"],
    #},
    #zip_safe=False,
)
