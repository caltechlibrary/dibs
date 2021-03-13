'''
date_utils.py: miscellaneous date-handling utilities for DIBS

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   datetime import datetime, timedelta


# Exported functions.
# .............................................................................

def human_datetime(dt):
    '''Return a more human-friendly string representing the given datetime.'''
    return dt.strftime("%I:%M %p on %Y-%m-%d") if dt else None
