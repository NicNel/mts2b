from . import renderProp
from . import worldProp
from . import cameraProp
#from . import lightProp

def register():
    renderProp.register()
    worldProp.register()
    cameraProp.register()
    #lightProp.register()

def unregister():
    renderProp.unregister()
    worldProp.unregister()
    cameraProp.unregister()
    #lightProp.unregister()
