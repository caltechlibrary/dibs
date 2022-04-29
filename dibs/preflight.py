'''
preflight.py: sanity checks to perform before starting server

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from commonpy.file_utils import writable, readable
from commonpy.string_utils import print_boxed
from os.path import dirname
from sidetrack import log

# In order for this to work, it needs to avoid importing anything that might
# in turn cause data_models to be imported.  So, keep DIBS imports to a
# minimum and watch the dependencies in the code.

from .settings import config, resolved_path


def preflight_check(database = None):
    '''Verify certain critical things are set up & complain if they're not.'''

    successes = [
        verified('LSP_TYPE'),
        verified('IIIF_BASE_URL'),
        verified('DATABASE_FILE',  check_parent_writable = True),
        verified('MANIFEST_DIR',   check_readable = True),
        verified('PROCESS_DIR',    check_readable = True, check_writable = True),
        verified('THUMBNAILS_DIR', check_readable = True, check_writable = True),
    ]

    if all(successes):
        log('preflight tests succeeded')
        return True
    else:
        log('preflight tests failed')
        return False


def verified(variable, check_readable = False, check_writable = False,
             check_parent_writable = False):
    '''Verify the given configuration 'variable' in various ways.'''

    if not config(variable, default = None):
        print_boxed(f'Variable {variable} is not set.\n'
                    ' DIBS cannot function properly.',
                    title = 'DIBS Fatal Error')
        return False
    dir = resolved_path(config(variable))  # noqa A001
    success = True
    if check_readable and not readable(dir):
        print_boxed(f'Cannot read the directory indicated by the configuration\n'
                    f'variable {variable}. The directory located at\n\n'
                    f'{dir}\n\nis not readable. DIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    if check_writable and not writable(dir):
        print_boxed(f'Cannot write the directory indicated by the configuration\n'
                    f'variable {variable}. The directory located at\n\n'
                    f'{dir}\n\nis not writable. DIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    if check_parent_writable and not writable(dirname(dir)):
        parent = dirname(dir)
        print_boxed(f'Cannot write in the parent directory of the value indicated by\n'
                    f'the configuraton variable {variable}. The directory located at\n\n'
                    f'{parent}\n\nis not writable. DIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    return success
