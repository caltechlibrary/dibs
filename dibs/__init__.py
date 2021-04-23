'''
Caltech DIBS (Digital Borrowing System), an implementation of controlled
digital lending by the Caltech Library.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

# Package metadata ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  ╭────────────────────── Notice ── Notice ── Notice ─────────────────────╮
#  |    The following values are automatically updated at every release    |
#  |    by the Makefile. Manual changes to these values will be lost.      |
#  ╰────────────────────── Notice ── Notice ── Notice ─────────────────────╯

__version__     = '0.2.1'
__description__ = 'An implementation of Controlled Digital Lending'
__url__         = 'https://github.com/caltechlibrary/dibs'
__author__      = 'Michael Hucka, Robert S. Doiel, Tommy Keswick, Stephen Davison'
__email__       = 'helpdesk@library.caltech.edu'
__license__     = 'BSD 3-clause'


# Exports.
# .............................................................................

from .server import dibs


# Miscellaneous utilities.
# .............................................................................

def print_version():
    print(f'{__name__} version {__version__}')
    print(f'Authors: {__author__}')
    print(f'URL: {__url__}')
    print(f'License: {__license__}')
