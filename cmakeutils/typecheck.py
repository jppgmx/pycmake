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

    keytypes = list(
            {type(k) for k in filter(lambda k: k is not None, obj.keys())}
        )
    valuetypes = list(
            {type(v) for v in filter(lambda v: v is not None, obj.values())}
        )

    if len(keytypes) == 1 and len(valuetypes) == 0:
        return keytypes[0] == key
    if len(keytypes) == 0 and len(valuetypes) == 1:
        return valuetypes[0] == value
    if len(keytypes) >= 2 and len(valuetypes) >= 2:
        return False

    ktype = keytypes[0]
    vtype = valuetypes[0]

    return ktype == key and vtype == value
