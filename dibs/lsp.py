'''
lsp.py: DIBS interface to LSPs.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   abc import ABC, abstractmethod
from   coif import cover_image
from   commonpy.network_utils import net
from   dataclasses import dataclass
import os
from   os.path import realpath, dirname, join, exists, isabs
from   pokapi import Folio
import re
from   sidetrack import log
from   textwrap import wrap
from   topi import Tind

from .settings import config, resolved_path


# Classes implementing interface to specific LSPs.
# .............................................................................

@dataclass
class LSPRecord():
    '''Common abstraction for records returned by different LSP's.'''
    id            : str
    url           : str
    title         : str
    author        : str
    publisher     : str
    edition       : str
    year          : str
    isbn_issn     : str


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

    def __init__(self, url = None, thumbnails_dir = None):
        '''Create an interface for the server at "url".'''
        self.url = url
        self._thumbnails_dir = thumbnails_dir
        self._tind = Tind(url)


    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        try:
            rec = self._tind.item(barcode = barcode).parent
            title = rec.title
            if rec.subtitle:
                title += ': ' + rec.subtitle
            log(f'record for {barcode} has id {rec.tind_id} in {self.url}')
            thumbnail_file = join(self._thumbnails_dir, barcode + '.jpg')
            # Don't overwrite existing images.
            if not exists(thumbnail_file):
                if rec.thumbnail_url:
                    save_thumbnail(thumbnail_file, url = rec.thumbnail_url)
                elif rec.isbn_issn:
                    save_thumbnail(thumbnail_file, isbn = rec.isbn_issn)
                else:
                    log(f"{barcode} lacks ISBN & thumbnail URL => no thumbnail")
            else:
                log(f'thumbnail image already exists in {thumbnail_file}')
            return LSPRecord(id        = rec.tind_id,
                             url       = rec.tind_url,
                             title     = truncated_title(rec.title),
                             author    = rec.author,
                             publisher = rec.publisher,
                             year      = rec.year,
                             edition   = rec.edition,
                             isbn_issn = rec.isbn_issn)
        except:
            log(f'could not find {barcode} in TIND')
            raise ValueError('No such barcode {barcode} in {self.url}')


class FolioInterface(LSPInterface):
    '''Interface layer for FOLIO hosted LSP servers.'''

    def __init__(self, url = None, token = None, tenant_id = None,
                 an_prefix = None, page_template = None, thumbnails_dir = None):
        '''Create an interface for the server at "url".'''
        self.url = url
        self._token = token
        self._tenant_id = tenant_id
        self._an_prefix = an_prefix
        self._page_tmpl = page_template
        self._thumbnails_dir = thumbnails_dir
        self._folio = Folio(okapi_url     = url,
                            okapi_token   = token,
                            tenant_id     = tenant_id,
                            an_prefix     = an_prefix)


    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        try:
            rec = self._folio.record(barcode = barcode)
            if not all([rec.title, rec.author, rec.year]):
                raise ValueError('Got incomplete record for {barcode} in {self.url}')
            log(f'record for {barcode} has id {rec.id}')
            thumbnail_file = join(self._thumbnails_dir, barcode + '.jpg')
            # Don't overwrite existing images.
            if not exists(thumbnail_file):
                if rec.isbn_issn:
                    save_thumbnail(thumbnail_file, isbn = rec.isbn_issn)
                else:
                    log(f"{rec.id} has no ISBN/ISSN => can't get a thumbnail")
            else:
                log(f'thumbnail image already exists in {thumbnail_file}')
            url = self._page_tmpl.format(accession_number = rec.accession_number)
            return LSPRecord(id        = rec.id,
                             url       = url,
                             title     = truncated_title(rec.title),
                             author    = rec.author,
                             publisher = rec.publisher,
                             year      = rec.year,
                             edition   = rec.edition,
                             isbn_issn = rec.isbn_issn)
        except ValueError:
            raise
        except Exception as ex:
            log(f'could not find {barcode} in FOLIO: {str(ex)}')
            raise ValueError('No such barcode {barcode} in {self.url}')


class UnconfiguredInterface(LSPInterface):
    '''Dummy interface, for when no LSP is chosen.'''

    def __repr__(self):
        '''Return a string representing this interface object.'''
        return "<{}>".format(self.__class__.__name__)


    def record(self, barcode = None):
        '''Return a record for the item identified by the "barcode".'''
        return LSPRecord(id        = 'LSP not configured',
                         url       = '',
                         title     = 'LSP not configured',
                         author    = 'LSP not configured',
                         publisher = 'LSP not configured',
                         year      = 'LSP not configured',
                         edition   = 'LSP not configured',
                         isbn_issn = '')


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

        # Read common configuration variables.
        thumbnails_dir = resolved_path(config('THUMBNAILS_DIR', section = 'dibs'))
        log(f'assuming thumbnails dir is {thumbnails_dir}')

        # Select the appropriate interface type and create the object.
        lsp_type = config('LSP_TYPE').lower()
        if lsp_type == 'folio':
            url           = config('FOLIO_OKAPI_URL',        section = 'folio')
            token         = config('FOLIO_OKAPI_TOKEN',      section = 'folio')
            tenant_id     = config('FOLIO_OKAPI_TENANT_ID',  section = 'folio')
            an_prefix     = config('FOLIO_ACCESSION_PREFIX', section = 'folio')
            page_template = config('EDS_PAGE_TEMPLATE',      section = 'folio')
            log(f'Using FOLIO URL {url} with tenant id {tenant_id}')
            lsp = FolioInterface(url = url,
                                 token = token,
                                 tenant_id = tenant_id,
                                 an_prefix = an_prefix,
                                 page_template = page_template,
                                 thumbnails_dir = thumbnails_dir)
        elif lsp_type == 'tind':
            url = config('TIND_SERVER_URL', section = 'tind')
            log(f'Using TIND URL {url}')
            lsp = TindInterface(url, thumbnails_dir = thumbnails_dir)
        else:
            lsp = UnconfiguredInterface()

        # Store the interface object (to implement the Singleton pattern).
        cls.__lsp_interface__ = lsp
        return lsp


# Internal utilities.
# .............................................................................

def save_thumbnail(dest_file, url = None, isbn = None):
    image = None
    cc_user = config('CC_USER', section = 'contentcafe', default = None)
    cc_password = config('CC_PASSWORD', section = 'contentcafe', default = None)
    cc_login = (cc_user, cc_password) if (cc_user and cc_password) else None

    if isbn:
        url, image = cover_image(isbn, size = 'L', cc_login = cc_login)
        log(f'cover_image returned image at {url}')
    # We were either given a url in the call, or we found one using the isbn.
    elif url:
        (response, error) = net('get', url)
        if not error and response.status_code == 200:
            log(f'got image from {url}')
            image = response.content
    if image:
        log(f'will save cover image in {dest_file}')
        with open(dest_file, 'wb') as file:
            file.write(image)
    else:
        log(f'no cover image found for {url}')


def probable_issn(value):
    return len(value) < 10 and '-' in value


def truncated_title(title):
    modified_title = re.split(':|;|\.', title)[0].strip()
    if len(modified_title) > 60:
        return wrap(modified_title, 60)[0] + ' ...'
    else:
        return modified_title
