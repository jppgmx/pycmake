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
import os

from cmakeutils.typecheck import isdict

class CMakeValType(Enum):
    """
        Determines the type that CMakeValue carries.
    """

    BOOL = 1
    STRING = 2
    FILEPATH = 3

    # Non-official cmake types
    VARDICT = 4

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
            if os.path.isfile(value):
                self.type = CMakeValType.FILEPATH
        elif vtype is bool:
            self.type = CMakeValType.BOOL
        elif isdict(value, str, CMakeValue):
            self.type = CMakeValType.VARDICT
        else:
            raise ValueError('Value not supported -> ' + str(vtype))
        
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, CMakeValue):
            return False
        
        return self.type == __value.type and self.value == self.value
    
    def __ne__(self, __value: object) -> bool:
        return not self == __value
    
    def __hash__(self) -> int:
        return hash((self.type, self.value))

def castbool(boolean: bool):
    return 'ON' if boolean else 'OFF'