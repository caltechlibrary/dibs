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

from dibs.settings import config, dibs_path

def test_config_path():
    here = dirname(__file__)
    parent = join(here, os.path.pardir)
    assert abspath(dirname(config.config_file)) == abspath(parent)

def test_relative_to_caller():
    me = __file__
    d = dibs_path('tests/test_dibs_path.py')
    assert d == abspath(me)

def test_relative_to_settings():
    here = dirname(__file__)
    other = abspath(join(here, os.pardir, 'admin/run-server'))
    d = dibs_path('admin/run-server')
    assert d == other
