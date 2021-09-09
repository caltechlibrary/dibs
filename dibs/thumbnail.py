'''
thumbnail.py: utilities for getting jacket cover thumbnail images

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   commonpy.string_utils import antiformat
from   commonpy.network_utils import net
from   lxml import etree, html
import json

if __debug__:
    from sidetrack import log


# Exported functions.
# .............................................................................

def save_thumbnail(dest_file, url = None, isbn = None):
    if not any([url, isbn]):
        raise ValueError('save_thumbnail() requires either a URL or an ISBN')
    img = None
    if isbn:
        img = thumbnail_for_isbn(isbn)
    # We were either given a url in the call, or we found one using the isbn.
    elif url:
        (response, error) = net('get', url)
        if not error and response.status_code == 200:
            img = response.content
    if img:
        log(f'will save thumbnail image for {isbn} in {dest_file}')
        with open(dest_file, 'wb') as file:
            file.write(img)
    else:
        log(f'no thumbnail found for ISBN {isbn}')


def thumbnail_for_isbn(isbn):
    # None of the services currently can handle ISSN's.
    if probable_issn(isbn):
        log(f"cannot search for thumbnails by ISSN -- giving up")
        return None
    return (thumbnail_from_btol(isbn)
            or thumbnail_from_ol(isbn)
            or thumbnail_from_google(isbn))


def thumbnail_from_btol(isbn):
    '''Given an ISBN, return a URL for an cover image thumbnail.'''
    if not isbn:
        return None
    for size in ['L', 'M', 'S']:
        url = ('https://contentcafe2.btol.com/ContentCafe/jacket.aspx?'
               + f'UserID=ebsco-test&Password=ebsco-test&Return=T&Type={size}'
               + f'&Value={isbn}')
        (response, error) = net('get', url)
        if not error and response.status_code == 200:
            # BTOL responses use Transfer-Encoding: chunked and don't provide
            # a Content-Length header, so there's no way to know the size of
            # the image without downloading all of it.
            # If BTOL doesn't find a value, it returns a small default image.
            if len(response.content) > 2800:
                log(f'succeeded getting thumbnail image URL from btol for {isbn}')
                return response.content
    log('btol did not return a thumbnail URL for {isbn}')
    return None


def thumbnail_from_ol(isbn):
    '''Given an ISBN, return a URL for an cover image thumbnail.'''
    if not isbn:
        return None
    for size in ['L', 'M', 'S']:
        url = f'http://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg'
        (response, error) = net('get', url)
        if not error and response.status_code == 200:
            # If OL doesn't find a value, it returns a 1x1 pixel image.
            if len(response.content) > 810:
                log(f'succeeded getting thumbnail image URL from OL for {isbn}')
                return response.content
    log(f'OL did not return a thumbnail URL for {isbn}')
    return None


def thumbnail_from_google(isbn):
    '''Given an ISBN, return a URL for an cover image thumbnail.'''
    if not isbn:
        return None
    url = f'https://www.googleapis.com/books/v1/volumes?q={isbn}'
    (response, error) = net('get', url)
    if error:
        log(f'got error trying to get thumbnail from Google: {antiformat(error)}')
        return None
    # Google returns JSON, making it easier to get data directly.
    json_dict = json.loads(response.content.decode())
    thumbnail = ''
    if 'items' not in json_dict or 'volumeInfo' not in json_dict['items'][0]:
        log(f'got incomplete result for thumbnail from Google for {isbn}')
        return None
    info = json_dict['items'][0]['volumeInfo']
    if 'imageLinks' in info and 'thumbnail' in info['imageLinks']:
        log(f'succeeded getting thumbnail image URL from Google for {isbn}')
        image_url = info['imageLinks']['thumbnail']
        (google_response, google_error) = net('get', image_url)
        if not google_error:
            return google_response.content
        else:
            return None
    log(f'Google did not return a thumbnail URL for {isbn}')
    return None


# Internal utilities.
# .............................................................................

def probable_issn(value):
    return len(value) < 10 and '-' in value
