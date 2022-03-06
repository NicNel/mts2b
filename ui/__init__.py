from . import RSettings
from . import NSettings

def register():
    RSettings.register()
    NSettings.register()

def unregister():
    RSettings.unregister()
    NSettings.unregister()
