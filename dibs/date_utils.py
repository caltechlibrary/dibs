'''
date_utils.py: miscellaneous date-handling utilities for DIBS

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import arrow


# Exported functions.
# .............................................................................

def human_datetime(value):
    '''Return a human-friendly string for the given datetime in local time.'''
    if not value:
        return None
    return arrow.get(value).to('local').strftime("%I:%M %p (%Z) on %Y-%m-%d")
