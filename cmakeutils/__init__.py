__package__ = 'cmakeutils'

from . import platcheck as platfrom2
from . import typecheck

if platfrom2.isWindows():
    from . import win32