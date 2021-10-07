import os
from   os.path import dirname, join, isabs, isdir, exists, abspath, realpath
import pytest
import sys
import datetime as dt


try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from dibs.settings import config, resolved_path

def test_relative_to_caller():
    me = __file__
    d = resolved_path('tests/test_resolved_path.py')
    assert d == abspath(me)

def test_relative_to_settings():
    here = dirname(__file__)
    other = abspath(join(here, os.pardir, 'admin/run-server'))
    d = resolved_path('admin/run-server')
    assert d == other
