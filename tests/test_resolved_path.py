import os
from os.path import join, dirname, abspath


def test_relative_to_caller():
    from dibs.settings import resolved_path

    me = __file__
    d = resolved_path('tests/test_resolved_path.py')
    assert d == abspath(me)


def test_relative_to_settings():
    from dibs.settings import resolved_path

    here = dirname(__file__)
    other = abspath(join(here, os.pardir, 'admin/run-server'))
    d = resolved_path('admin/run-server')
    assert d == other
