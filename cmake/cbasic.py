#
#   pycmake CMake Basic types
#
#   Copyright (C) 2023 jppgmx
#   Licensed under MIT License
#

import os
import builtins as btin

from cmakeutils.typecheck import isdict
from enum import Enum
from pathlib import Path

class CMakeValType(Enum):
    BOOL = 1
    STRING = 2

    # Non-official types
    VARDICT = 3

class CMakeValue:
    value = None
    type: CMakeValType

    def __init__(self, value):
        vType = type(value)
        if vType is not str and vType is not bool and not isdict(value, str, CMakeValue):
            raise ValueError('Invalid value type: ' + str(vType))

        self.value = value

        if vType is str:
            self.type = CMakeValType.STRING
        elif vType is bool:
            self.type = CMakeValType.BOOL
        elif isdict(value, str, CMakeValue):
            self.type = CMakeValType.VARDICT
        else:
            raise ValueError('Value not supported -> ' + str(vType))
