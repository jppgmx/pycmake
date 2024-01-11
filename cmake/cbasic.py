"""
    pycmake cbasic module
    --------------------

    Copyright (C) 2023 jppgmx
    Licensed under MIT License

    It contains a class that encapsulates the data and its types, 
    which are String and Bool, in addition to VarDict, which is a type to encapsulate a dictionary.


"""
import dataclasses

from enum import Enum
from cmakeutils.typecheck import isdict


class CMakeValType(Enum):
    """
        Determines the type that CMakeValue carries.
    """

    BOOL = 1
    STRING = 2

    # Non-official cmake types
    VARDICT = 3

@dataclasses.dataclass
class CMakeValue:

    """
        Encapsulates a value.
    """
    value = None
    type: CMakeValType

    def __init__(self, value):
        vtype = type(value)
        if vtype is not str and vtype is not bool and not isdict(value, str, CMakeValue):
            raise ValueError('Invalid value type: ' + str(vtype))

        self.value = value

        if vtype is str:
            self.type = CMakeValType.STRING
        elif vtype is bool:
            self.type = CMakeValType.BOOL
        elif isdict(value, str, CMakeValue):
            self.type = CMakeValType.VARDICT
        else:
            raise ValueError('Value not supported -> ' + str(vtype))
