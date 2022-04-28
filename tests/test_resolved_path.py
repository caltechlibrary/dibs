import os
from   os.path import join, dirname, abspath
import sys

try:
    thisdir = dirname(abspath(__file__))
    sys.path.append(join(thisdir, '..'))
except Exception:
    sys.path.append('..')

from dibs.settings import resolved_path


def test_relative_to_caller():
    me = __file__
    d = resolved_path('tests/test_resolved_path.py')
    assert d == abspath(me)


def test_relative_to_settings():
    here = dirname(__file__)
    other = abspath(join(here, os.pardir, 'admin/run-server'))
    d = resolved_path('admin/run-server')
    assert d == other
