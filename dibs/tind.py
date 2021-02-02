'''
tind.py: code for interacting with Caltech.TIND.io
'''

from   collections import namedtuple
from   commonpy.network_utils import net
import json as jsonlib
from   lxml import etree, html


# Constants.
# .............................................................................

# URLs for the TIND API, to be used with HTTP GET calls.
# Note: for the API URLs below, use Python .format() to substitute the
# relevant value into the string. Each string takes only 1 value.

_XML_USING_BARCODE = 'https://caltech.tind.io/search?p=barcode%3A+{}&of=xm'
_XML_USING_TIND_ID = 'https://caltech.tind.io/search?recid={}&of=xm'

# URLs for finding cover image thumbnails.
# Note: for the URLs below, use Python .format() to substitute the
# value of an ISBN number the string. Each string takes only 1 value.

_ISBN_SEARCH_GOOGLE = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'
_ISBN_SEARCH_AMAZON = 'https://www.amazon.com/gp/search/ref=sr_adv_b/?search-alias=stripbooks&unfiltered=1&field-isbn={}&sort=relevanceexprank'


# Class definitions.
# .............................................................................

class TindRecord():
    '''Class to store TIND record data.'''

    def __init__(self, barcode = None, tind_id = None, marc_xml = None):
        '''Create a TIND record.

        Keword arguments "barcode", "tind_id" and "marc_xml" are mutually
        exclusive.

        If either "barcode" or "tind_id" is given, this will look up the
        record using either the barcode or the TIND id in Caltech's TIND
        server and create the record based on data found.

        If "marc_xml" is given instead, this will create the record using
        the given XML string. The XML must have been obtained using the MARC
        XML export feature of TIND.
        '''
        self.barcode   = ''
        self.tind_id   = ''
        self.title     = ''
        self.author    = ''
        self.year      = ''
        self.edition   = ''
        self.call_no   = ''
        self.thumbnail = ''
        self.isbn_list = []

        args = locals().copy()
        del args['self']
        given_keywords = list(keyword for keyword in args if args[keyword])
        if len(given_keywords) == 0:    # No keyword given => return empty rec.
            return
        elif len(given_keywords) == 1:  # Fill out rec based on argument given.
            given = given_keywords[0]
            self._init_from_argument[given](self, args[given])
        else:
            raise ValueError("Can't use more than one: barcode, tind_id or marc_xml")


    def _init_from_xml(self, xml):
        '''Initialize this record given MARC XML as a string.'''
        # Save the XML internally in case it's useful.
        self._xml = xml

        # Parse the XML.
        try:
            tree = etree.fromstring(xml, parser = etree.XMLParser(recover = True))
        except Exception as ex:
            raise ValueError(f'Bad XML')
        if len(tree) == 0:             # Blank record.
            return
        record = tree.find('{http://www.loc.gov/MARC21/slim}record')
        elem_controlfield = '{http://www.loc.gov/MARC21/slim}controlfield'
        elem_datafield = '{http://www.loc.gov/MARC21/slim}datafield'
        elem_subfield = '{http://www.loc.gov/MARC21/slim}subfield'
        subtitle = None
        for element in record.findall(elem_controlfield):
            if element.attrib['tag'] == '001':
                self.tind_id = element.text.strip()
            elif element.attrib['tag'] == '008':
                self.year = element.text[7:11].strip()
                if not self.year.isdigit():
                    self.year = ''
        for element in record.findall(elem_datafield):
            if element.attrib['tag'] == '250':
                self.edition = element.find(elem_subfield).text.strip()
            elif element.attrib['tag'] == '050':
                self.call_no = ''
                for subfield in element.findall(elem_subfield):
                    self.call_no += subfield.text.strip() + ' '
            elif element.attrib['tag'] == '090':
                # If the record has call numbers in both 050 and 090, the 090
                # value will overwrite the 050 one, and that's what we want.
                self.call_no = ''
                for subfield in element.findall(elem_subfield):
                    self.call_no += subfield.text.strip() + ' '
            elif element.attrib['tag'] == '100':
                for subfield in element.findall(elem_subfield):
                    if subfield.attrib['code'] == 'a':
                        self.main_author = subfield.text.strip()
            elif element.attrib['tag'] == '245':
                for subfield in element.findall(elem_subfield):
                    if subfield.attrib['code'] == 'a':
                        text = subfield.text.strip()
                        # The title sometimes contains the author names too.
                        self.title, self.author = parsed_title_and_author(text)
                    elif subfield.attrib['code'] == 'b':
                        subtitle = subfield.text.strip()
                    elif subfield.attrib['code'] == 'c':
                        self.author = subfield.text.strip()
            elif element.attrib['tag'] == '020':
                for subfield in element.findall(elem_subfield):
                    # Value is sometimes of the form "1429224045 (hbk.)"
                    value = subfield.text.split()[0]
                    if value.isdigit():
                        self.isbn_list.append(value)

        # We get author from 245 because in our entries, it's frequently part
        # of the title statement. If it's not, but we got an author from 100
        # use that.  100 only lists first author, but it's better than nothing.
        if self.author:
            if self.author.startswith('by'):
                self.author = self.author[2:].strip()
            elif self.author.startswith('edited by'):
                self.author = self.author[10:].strip()
        elif self.main_author:
            self.author = self.main_author

        # Caltech's TIND database contains some things that are not reading
        # materials per se. The following is an attempt to weed those out.
        if sum([not self.author, not self.year, not self.call_no]) > 1:
            for field in ['title', 'author', 'year', 'call_no', 'edition']:
                setattr(self, field, None)
            return

        # Some cleanup work is better left until after we obtain all values.
        self.author = cleaned(self.author)
        self.title = cleaned(self.title)
        self.edition = cleaned(self.edition)
        self.call_no = cleaned(self.call_no)
        if subtitle:
            # A separate subtitle is not useful for us, so merge it into title.
            if subtitle.find('/') > 0:
                subtitle = subtitle[:-1].strip()
            self.title += ': ' + subtitle

        # Get other items.
        self._get_thumbnail()


    def _init_from_barcode(self, barcode):
        self.barcode = str(barcode)
        (response, error) = net('get', _XML_USING_BARCODE.format(barcode))
        if not error:
            self._init_from_xml(response.content)


    def _init_from_tind_id(self, tind_id):
        self.tind_id = str(tind_id)
        (response, error) = net('get', _XML_USING_TIND_ID.format(tind_id))
        if not error:
            self._init_from_xml(response.content)


    def _get_thumbnail(self):
        '''Look for cover image thumbnails for each ISBN and return first one.'''
        # We can't always find an image, so we try all the ISBNs we have for an item.
        # I find that Amazon's thumbnails are often bigger than Googles, so that's
        # why the order of search is Amazon first.
        for isbn in self.isbn_list:
            self.thumbnail = thumbnail_from_amazon(isbn)
            if self.thumbnail:
                return
            self.thumbnail = thumbnail_from_google(isbn)
            if self.thumbnail:
                return


    # Initialize the dispatcher after defining the methods themselves.
    _init_from_argument = {'barcode' : staticmethod(_init_from_barcode).__func__,
                           'tind_id' : staticmethod(_init_from_tind_id).__func__,
                           'marc_xml': staticmethod(_init_from_xml).__func__}


# Miscellaneous helpers.
# .............................................................................

def cleaned(text):
    '''Mildly clean up the given text string.'''
    if not text:
        return text
    if text and text.endswith('.'):
        text = text[:-1]
    return text.strip()


def parsed_title_and_author(text):
    '''Extract a title and authors (if present) from the given text string.'''
    title = None
    author = None
    if text.find('/') > 0:
        start = text.find('/')
        title = text[:start].strip()
        author = text[start + 3:].strip()
    elif text.find('[by]') > 0:
        start = text.find('[by]')
        title = text[:start].strip()
        author = text[start + 5:].strip()
    elif text.rfind(', by') > 0:
        start = text.rfind(', by')
        title = text[:start].strip()
        author = text[start + 5:].strip()
    else:
        title = text
    if title.endswith(':'):
        title = title[:-1].strip()
    return title, author


def thumbnail_from_amazon(isbn):
    '''Given an ISBN, return a URL for an cover image thumbnail.'''
    (response, error) = net('get', _ISBN_SEARCH_AMAZON.format(isbn))
    if error:
        return None
    # For Amazon, we scrape the results page.
    page = html.fromstring(response.content)
    img_element = page.cssselect('img.s-image')
    if img_element:
        return img_element[0].attrib['src']
    return None


def thumbnail_from_google(isbn):
    '''Given an ISBN, return a URL for an cover image thumbnail.'''
    (response, error) = net('get', _ISBN_SEARCH_GOOGLE.format(isbn))
    if error:
        return None
    # Google returns JSON, making it easier to get data directly.
    json = jsonlib.loads(response.content.decode())
    if 'items' not in json:
        return None
    if 'volumeInfo' not in json['items'][0]:
        return None
    info = json['items'][0]['volumeInfo']
    if 'imageLinks' in info and 'thumbnail' in info['imageLinks']:
        return info['imageLinks']['thumbnail']
    return None
