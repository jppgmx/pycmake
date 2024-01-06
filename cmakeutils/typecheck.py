#
#   pycmake Typecheck utility
#
#   Copyright (c) 2023 jppgmx
#   Licensed under MIT License
#

def isdict(obj: object, key: type, value: type) -> bool:
    if not isinstance(obj, dict):
        return False
    
    if (len(obj) == 0):
        return True
    
    keyTypes = list(set(filter(lambda k: k != None, obj.keys())))
    valueTypes = list(set(filter(lambda v: v != None, obj.values())))

    if len(keyTypes) == 1 and len(valueTypes) == 0:
        if type(keyTypes[0]) == key:
            return True
        else:
            return False
    elif len(keyTypes) == 0 and len(valueTypes) == 1:
        if type(valueTypes[0]) == value:
            return True
        else:
            return False
    elif len(keyTypes) >= 2 and len(valueTypes) >= 2:
        return False
    
    kType = type(keyTypes[0])
    vType = type(valueTypes[0])

    return kType == key and vType == value