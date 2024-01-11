from cmakeutils.win32.kernel32 import SetSearchPathMode, SearchPath, SearchMode

def test_searchpath():
    tofind = 'cmd'
    ext = '.exe'

    SetSearchPathMode(SearchMode.SAFE_ENABLE)
    result = SearchPath(tofind, ext)

    assert (result[0].lower()) == ('C:\\Windows\\system32\\cmd.exe'.lower())
