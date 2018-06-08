#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re
import codecs
import os


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
		author="Gilles Arcas",
		description='Program that gives a reputation score to url\'s\n.',
		packages=find_packages(),
        py_package='test.suite.py',
		entry_points = {
			'console_scripts': ['numsed = numsed.numsed:numsed']
    },
    zip_safe=True,
   )
