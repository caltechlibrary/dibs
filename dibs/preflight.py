'''
preflight.py: sanity checks to perform before starting server

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from commonpy.file_utils import delete_existing, writable, readable
from commonpy.string_utils import print_boxed
from os.path import realpath, dirname, join, exists
from sidetrack import log

# In order for this to work, it needs to avoid importing anything that might
# in turn cause data_models to be imported.  So, keep DIBS imports to a
# minimum and watch the dependencies in the code.

from .settings import config, resolved_path


def preflight_check(database = None):
    '''Verify certain critical things are set up & complain if they're not.'''

    successes = [
        verified('IIIF_BASE_URL'),
        verified('DATABASE_FILE'),
        verified('MANIFEST_DIR', test_read = True),
        verified('PROCESS_DIR', test_read = True, test_write = True),
        verified('THUMBNAILS_DIR', test_read = True, test_write = True),
    ]

    if all(successes):
        log(f'preflight tests succeeded')
        return True
    else:
        log(f'preflight tests failed')
        return False


def verified(variable, test_read = False, test_write = False):
    if not config(variable, default = None):
        print_boxed(f'Variable {variable} is not set.\n'
                    ' DIBS cannot function properly.',
                    title = 'DIBS Fatal Error')
        return False
    dir = resolved_path(config(variable))
    success = True
    if test_read and not readable(dir):
        print_boxed(f'Cannot read {variable} directory at\n{dir}\n'
                    + '\nDIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    if test_write and not writable(dir):
        print_boxed(f'Cannot write to {variable} directory at\n{dir}\n'
                    + '\nDIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    return success
