bl_info = {
    "name": "MITSUBA2_Exporter",
    "author": "nel",
    "version": (0, 0),
    "blender": (2, 80, 0),
    "category": "Render",
    "location": "Info header, render engine menu",
    "description": "Mitsuba2 for Blender",
    "warning": "",
}

import sys
import os

currDir = os.path.abspath(os.path.dirname(__file__))
#sys.path.append(currDir)

from .mitsuba2 import registerMTS2, unregisterMTS2

def register():
    from . import props
    props.register()
    print("Addon current directory", currDir)
    registerMTS2()

def unregister():
    from . import props
    props.unregister()
    unregisterMTS2()
