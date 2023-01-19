#!/usr/bin/env python3
# =============================================================================
# @file    setup.py
# @brief   Installation setup file
# @created 2021-05-21
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/dibs
#
# Note: configuration metadata is maintained in setup.cfg.  This file exists
# primarily to hook in setup.cfg and requirements.txt.
# =============================================================================

from   os.path import exists, join, abspath, dirname
from   setuptools import setup

here = abspath(dirname(__file__))

requirements = []
if exists(join(here, 'requirements.txt')):
    with open(join(here, 'requirements.txt')) as f:
        requirements = f.read().rstrip().splitlines()

setup(
    setup_requires = ['wheel'],
    install_requires = requirements,
)
