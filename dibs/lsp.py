'''
lsp.py: DIBS interface to LSPs.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pokapi import Folio
from sidetrack import log
from topi import Tind

from .settings import config


# Classes implementing interface to specific LSPs.
# .............................................................................

@dataclass
class LSPRecord():
    '''Common abstraction for records returned by different LSP's.'''
    id            : str
    details_page  : str
    title         : str
    author        : str
    publisher     : str
    edition       : str
    year          : str
    isbn_issn     : str
    thumbnail_url : str


class LSPInterface(ABC):
    '''Abstract interface class for getting a record from an LSP.

    All concrete implementations of this class are assumed to have at least
    a URL for the API of the server, and may have additional parameters on
    a per-class basis.
    '''

    def __init__(self, url = None):
        '''Create an interface for the server at "url".'''
        self.url = url


    def __repr__(self):
        '''Return a string representing this interface object.'''
        return "<{} for {}>".format(self.__class__.__name__, self.url)


    @abstractmethod
    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        pass


class TindInterface(LSPInterface):
    '''Interface layer for TIND hosted LSP servers.'''

    def __init__(self, url = None):
        '''Create an interface for the server at "url".'''
        self.url = url
        self._tind = Tind(url)


    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        try:
            rec = self._tind.item(barcode = barcode).parent
            title = rec.title
            if rec.subtitle:
                title += ': ' + rec.subtitle
            log(f'record for {barcode} has id {rec.id} in {self.url}')
            return LSPRecord(id            = rec.tind_id,
                             details_page  = rec.tind_url,
                             title         = rec.title,
                             author        = rec.author,
                             publisher     = rec.publisher,
                             year          = rec.year,
                             edition       = rec.edition,
                             isbn_issn     = rec.isbn_issn,
                             thumbnail_url = rec.thumbnail_url)
        except:
            log(f'could not find {barcode} in TIND')
            raise ValueError('No such barcode {barcode} in {self.url}')



class FolioInterface(LSPInterface):
    '''Interface layer for FOLIO hosted LSP servers.'''

    def __init__(self, url = None, token = None, tenant_id = None):
        '''Create an interface for the server at "url".'''
        self.url = url
        self._token = token
        self._tenant_id = tenant_id
        self._folio = Folio(okapi_url = url, okapi_token = token,
                            tenant_id = tenant_id)


    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        try:
            rec = self._folio.record(barcode = barcode)
            log(f'record for {barcode} has id {rec.id} in {self.url}')
            return LSPRecord(id            = rec.id,
                             details_page  = rec.details_page,
                             title         = rec.title,
                             author        = rec.author,
                             publisher     = rec.publisher,
                             year          = rec.year,
                             edition       = rec.edition,
                             isbn_issn     = rec.isbn_issn,
                             thumbnail_url = rec.thumbnail_url)
        except:
            log(f'could not find {barcode} in FOLIO')
            raise ValueError('No such barcode {barcode} in {self.url}')


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
            log(f'type: {type(config)}')
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