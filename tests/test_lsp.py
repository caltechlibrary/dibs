from   os.path import join, dirname, abspath
import sys

try:
    thisdir = dirname(abspath(__file__))
    sys.path.append(join(thisdir, '..'))
except Exception:
    sys.path.append('..')

from dibs.lsp import truncated_title, probable_issn


def test_probable_issn():
    assert probable_issn('1573-1332') is True
    assert probable_issn('15731332') is False
    assert probable_issn('978-0-691-20019-4') is False


def test_truncated_title():
    assert truncated_title('Foo: Bar') == 'Foo'
    assert truncated_title('Foo; by Bar') == 'Foo'
    assert truncated_title('Foo. Bar') == 'Foo'
