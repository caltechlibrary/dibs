import os
import pytest
import sys
import datetime as dt


try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from dibs.date_utils import *


def test_round_minutes():
    x = dt.datetime(2021, 4, 6, 23, 56, 3, 546899)
    assert round_minutes(x, 'down') == dt.datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == dt.datetime(2021, 4, 6, 23, 57)

    x = dt.datetime(2021, 4, 6, 23, 56, 30, 546899)
    assert round_minutes(x, 'down') == dt.datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == dt.datetime(2021, 4, 6, 23, 57)

    x = dt.datetime(2021, 4, 6, 23, 56, 0, 546899)
    assert round_minutes(x, 'down') == dt.datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == dt.datetime(2021, 4, 6, 23, 57)

    x = dt.datetime(2021, 4, 6, 23, 56, 55, 0)
    assert round_minutes(x, 'down') == dt.datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == dt.datetime(2021, 4, 6, 23, 57)

    x = dt.datetime(2021, 4, 6, 23, 0, 0, 0)
    assert round_minutes(x, 'down') == dt.datetime(2021, 4, 6, 23, 0)
    assert round_minutes(x, 'up')   == dt.datetime(2021, 4, 6, 23, 1)
