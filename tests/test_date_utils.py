import os
import pytest
import sys
from datetime import datetime


try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from dibs.date_utils import *


def test_round_minutes():
    x = datetime(2021, 4, 6, 23, 56, 3, 546899)
    assert round_minutes(x, 'down') == datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == datetime(2021, 4, 6, 23, 57)

    x = datetime(2021, 4, 6, 23, 56, 30, 546899)
    assert round_minutes(x, 'down') == datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == datetime(2021, 4, 6, 23, 57)

    x = datetime(2021, 4, 6, 23, 56, 0, 546899)
    assert round_minutes(x, 'down') == datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == datetime(2021, 4, 6, 23, 57)

    x = datetime(2021, 4, 6, 23, 56, 55, 0)
    assert round_minutes(x, 'down') == datetime(2021, 4, 6, 23, 56)
    assert round_minutes(x, 'up')   == datetime(2021, 4, 6, 23, 57)

    x = datetime(2021, 4, 6, 23, 0, 0, 0)
    assert round_minutes(x, 'down') == datetime(2021, 4, 6, 23, 0)
    assert round_minutes(x, 'up')   == datetime(2021, 4, 6, 23, 1)
