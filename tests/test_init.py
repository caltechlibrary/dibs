def test_version():
    """Test version import."""
    from dibs import __version__
    assert __version__


def test_print_version(capsys):
    from dibs import print_version
    print_version()
    captured = capsys.readouterr()
    assert 'URL' in captured.out
