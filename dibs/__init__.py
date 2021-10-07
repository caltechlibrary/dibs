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
# This is set of variables is to identify the Python software package.  These
# values are _not_ presented in the user interface of DIBS, except for the
# version number.  The information presented to DIBS users, like the contact
# email address, are set elsewhere, not here.
#
#  ╭────────────────────── Notice ── Notice ── Notice ─────────────────────╮
#  |    The following values are automatically updated at every release    |
#  |    by the Makefile. Manual changes to these values will be lost.      |
#  ╰────────────────────── Notice ── Notice ── Notice ─────────────────────╯

__version__     = '0.5.0'
__description__ = 'DIBS (Digital Borrowing System) is an implementation of Controlled Digital Lending'
__url__         = 'https://github.com/caltechlibrary/dibs'
__author__      = 'Michael Hucka, Robert S. Doiel, Tommy Keswick, Stephen Davison'
__email__       = 'helpdesk@library.caltech.edu'
__license__     = 'BSD 3-clause'


# Miscellaneous utilities.
# .............................................................................

def print_version():
    print(f'{__name__} version {__version__}')
    print(f'Authors: {__author__}')
    print(f'URL: {__url__}')
    print(f'License: {__license__}')
