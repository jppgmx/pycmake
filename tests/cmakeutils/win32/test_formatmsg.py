import cmakeutils.win32.kernel32 as krnl
import cmakeutils.win32.winconstants as wc

def test_formatmsg():
    expected = 'Hello World in Python using FormatMessage!'
    toFormat = '%1 %2 in Py%3 using %4Message%!'
    args = [
        'Hello',
        'World',
        'thon',
        'Format'
    ]

    formatedString = krnl.FormatMessage(
        krnl.FormatSource.FS_STRING,
        srcInput=toFormat,
        args=args
        )
    
    assert (expected.lower()) == (formatedString.lower())