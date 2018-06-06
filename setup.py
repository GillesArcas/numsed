#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import codecs
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^VERSION = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


if __name__ == "__main__":
    setup(
        name='numsed',
        version=find_version("numsed", "numsed.py"),
        url = 'https://github.com/gillesArcas/numsed',
        author = 'Gilles Arcas',
        author_email = 'gilles.arcas@gmail.com',
        description='Computing with sed: a compiler from python to sed\n',
        packages=find_packages(),
        entry_points = {
            'console_scripts': ['numsed = numsed.numsed:numsed_main']
        },
        zip_safe=True,
   )
