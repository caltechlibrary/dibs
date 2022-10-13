from datetime import datetime


def test_round_minutes():
    from dibs.date_utils import round_minutes

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


def test_human_datetime():
    from dibs.date_utils import human_datetime

    x = datetime(2021, 4, 6, 23, 0, 0, 0)
    hx = human_datetime(x)
    assert hx[0:8] == '4:00 PM '
    assert hx[13:] == ' on 2021-04-06'

    x = datetime(2021, 4, 6, 23, 5, 6, 7)
    hx = human_datetime(x)
    assert hx[0:8] == '4:05 PM '
    assert hx[13:] == ' on 2021-04-06'

    x = datetime(2021, 4, 6, 23, 5, 6, 7)
    hx = human_datetime(x, "%I:%M %p on %Y-%m-%d")
    assert hx == '4:05 PM on 2021-04-06'

    hx = human_datetime('')
    assert hx == ''
