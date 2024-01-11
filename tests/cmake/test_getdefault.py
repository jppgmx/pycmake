import cmake

def test_cmakeobj():

    cmake.cminit()
    inst = cmake.cmdefault()
    assert inst is not None
