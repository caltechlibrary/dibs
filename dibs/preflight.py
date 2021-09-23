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
        verified('LSP_TYPE'),
        verified('IIIF_BASE_URL'),
        verified('DATABASE_FILE',  write_parent = True),
        verified('MANIFEST_DIR',   read = True),
        verified('PROCESS_DIR',    read = True, write = True),
        verified('THUMBNAILS_DIR', read = True, write = True),
    ]

    if all(successes):
        log(f'preflight tests succeeded')
        return True
    else:
        log(f'preflight tests failed')
        return False


def verified(variable, read = False, write = False, write_parent = False):
    if not config(variable, default = None):
        print_boxed(f'Variable {variable} is not set.\n'
                    ' DIBS cannot function properly.',
                    title = 'DIBS Fatal Error')
        return False
    dir = resolved_path(config(variable))
    success = True
    if read and not readable(dir):
        print_boxed(f'Cannot read the directory indicated by the configuration\n'
                    f'variable {variable}. The directory located at\n\n'
                    f'{dir}\n\nis not readable. DIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    if write and not writable(dir):
        print_boxed(f'Cannot write the directory indicated by the configuration\n'
                    f'variable {variable}. The directory located at\n\n'
                    f'{dir}\n\nis not writable. DIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    if write_parent and not writable(dirname(dir)):
        parent = dirname(dir)
        print_boxed(f'Cannot write in the parent directory of the value indicated by\n'
                    f'the configuraton variable {variable}. The directory located at\n\n'
                    + f'{parent}\n\nis not writable. DIBS cannot function properly.',
                    title = 'DIBS configuration error')
        success = False
    return success
