def test_probable_issn():
    from dibs.lsp import probable_issn

    assert probable_issn('1573-1332') is True
    assert probable_issn('15731332') is False
    assert probable_issn('978-0-691-20019-4') is False


def test_truncated_title():
    from dibs.lsp import truncated_title

    assert truncated_title('Foo: Bar') == 'Foo'
    assert truncated_title('Foo; by Bar') == 'Foo'
    assert truncated_title('Foo. Bar') == 'Foo'


def test_names():
    from dibs.lsp import TindInterface, FolioInterface

    interface = TindInterface()
    assert interface.name == 'TIND'

    interface = FolioInterface()
    assert interface.name == 'FOLIO'
