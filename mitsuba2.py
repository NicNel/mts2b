import bpy

import os
import tempfile
import subprocess
import math
import time
import shutil
import json

from .engine import MTS2enderEngine
from .ui.RSettings import MTS2_RENDER_PT_System, MTS2_RENDER_PT_Sensor, MTS2_RENDER_PT_Film

# RenderEngines also need to tell UI Panels that they are compatible with.
# We recommend to enable all panels marked as BLENDER_RENDER, and then
# exclude any panels that are replaced by custom panels registered by the
# render engine, or that are not supported.
def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
    }
    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels
	
def registerMTS2():
    bpy.utils.register_class(MTS2enderEngine)
    from . import ui
    ui.register()
    for panel in get_panels():
        panel.COMPAT_ENGINES.add('MTS2')
    print("Mitsuba2 registered")
def unregisterMTS2():
    bpy.utils.unregister_class(MTS2enderEngine)
    from . import ui
    ui.unregister()
    for panel in get_panels():
        if 'MTS2' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('MTS2')
    print("Mitsuba2 unregistered")
