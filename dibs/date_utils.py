'''
date_utils.py: miscellaneous date-handling utilities for DIBS

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import arrow
from   datetime import datetime as dt
from   datetime import timedelta


# Exported functions.
# .............................................................................

def human_datetime(value, format = "%I:%M %p (%Z) on %Y-%m-%d"):
    '''Return a human-friendly string for the given datetime in local time.'''
    if not value:
        return None
    time = arrow.get(value).to('local').strftime(format)
    # Stftime has no option to *not* zero-pad the numbers, so we have to do it:
    return time.lstrip('0')


def round_minutes(time, direction):
    '''Round the given time to the minute according in the desired direction.'''
    new_minute = (time.minute + (1 if direction == 'up' else 0))
    new_time = time + timedelta(minutes = new_minute - time.minute)
    return new_time.replace(second = 0, microsecond = 0)


def time_now():
    '''Return datetime.utcnow() but with microseconds zeroed out.'''
    return dt.utcnow().replace(microsecond = 0)
