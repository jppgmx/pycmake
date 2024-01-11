import cmakeutils.win32.kernel32 as krnl

def test_formatmsg():
    expected = 'Hello World in Python using FormatMessage!'
    toformat = '%1 %2 in Py%3 using %4Message%!'
    args = [
        'Hello',
        'World',
        'thon',
        'Format'
    ]

    formatedstring = krnl.FormatMessage(
        krnl.FormatSource.FS_STRING,
        srcinput=toformat,
        args=args
        )

    assert (expected.lower()) == (formatedstring.lower())
