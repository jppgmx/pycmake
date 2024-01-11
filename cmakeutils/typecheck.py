"""
   pycmake Typecheck utility

   Copyright (c) 2023 jppgmx
   Licensed under MIT License

   Adds some type checks
"""

def isdict(obj: object, key: type, value: type) -> bool:
    """
        Check if object is a dict with specified type values.
    """

    if not isinstance(obj, dict):
        return False

    if len(obj) == 0:
        return True

    keytypes = list(set(filter(lambda k: k is not None, obj.keys())))
    valuetypes = list(set(filter(lambda v: v is not None, obj.values())))

    if len(keytypes) == 1 and len(valuetypes) == 0:
        if isinstance(keytypes[0], key):
            return True
        else:
            return False
    elif len(keytypes) == 0 and len(valuetypes) == 1:
        if isinstance(valuetypes[0], value):
            return True
        else:
            return False
    elif len(keytypes) >= 2 and len(valuetypes) >= 2:
        return False

    ktype = type(keytypes[0])
    vtype = type(valuetypes[0])

    return ktype == key and vtype == value
