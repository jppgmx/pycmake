import cmake
import cmake.options as ops
import os

def test_cmakeobj():
    
    cmake.cminit(ops.CMakeInitOptions(enableLogging=True))
    assert cmake.CMakeDefault != None