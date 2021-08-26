'''
lsp.py: DIBS interface to LSPs.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from abc import ABC, abstractmethod
from pokapi import Folio
from sidetrack import log
from topi import Tind

from .settings import config


# Classes implementing interface to specific LSPs.
# .............................................................................

class LSPInterface(ABC):
    '''Abstract interface class for getting data from an LSP.'''

    # The name of this type of LSP.  Used for printing messages.
    name = ''

    def __init__(self):
        pass


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.name


    @abstractmethod
    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        pass


class TindInterface(LSPInterface):
    name = 'TIND'

    def __init__(self, url = None):
        self._url = url
        self._tind = Tind(url)


    def record(self, barcode = None):
        try:
            return self._tind.item(barcode = barcode).parent
        except:
            log(f'could not find {barcode} in TIND')
            raise ValueError('No such barcode {barcode} in {self._url}')



class FolioInterface(LSPInterface):
    name = 'FOLIO'

    def __init__(self, url = None, token = None, tenant_id = None):
        self._url = url
        self._token = token
        self._tenant_id = tenant_id
        self._folio = Folio(okapi_url = url, okapi_token = token,
                            tenant_id = tenant_id)


    def record(self, barcode = None):
        try:
            return self._folio.record(barcode = barcode)
        except:
            log(f'could not find {barcode} in Folio')
            raise ValueError('No such barcode {barcode} in {self._url}')


# Primary exported class.
# .............................................................................

class LSP(LSPInterface):
    '''LSP abstraction class.'''

    def __new__(cls, *args, **kwds):
        # This implements a Singleton pattern by storing the object we create
        # and returning the same one if the class constructor is called again.
        lsp = cls.__dict__.get("__lsp_interface__")
        if lsp is not None:
            log(f'Using previously-created LSP object {str(cls)}')
            return lsp

        # Select the appropriate interface type and create the object.
        lsp_type = config('LSP_TYPE').lower()
        if lsp_type == 'folio':
            url       = config('FOLIO_OKAPI_URL',       section = 'folio')
            token     = config('FOLIO_OKAPI_TOKEN',     section = 'folio')
            tenant_id = config('FOLIO_OKAPI_TENANT_ID', section = 'folio')
            log(f'Using FOLIO URL {url} with tenant id {tenant_id}')
            lsp = FolioInterface(url = url, token = token, tenant_id = tenant_id)
        elif lsp_type == 'tind':
            url = config('TIND_SERVER_URL', section = 'tind')
            log(f'Using TIND URL {url}')
            lsp = TindInterface(url)
        else:
            raise ValueError('LSP_TYPE value is missing from settings.ini')

        # Store the interface object (to implement the Singleton pattern).
        cls.__lsp_interface__ = lsp
        return lsp
