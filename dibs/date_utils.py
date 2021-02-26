'''
date_utils.py: miscellaneous date-handling utilities for DIBS
'''

from   datetime import datetime, timedelta


# Exported functions.
# .............................................................................

def human_datetime(dt):
    '''Return a more human-friendly string representing the given datetime.'''
    return dt.strftime("%I:%M %p on %Y-%m-%d") if dt else None
