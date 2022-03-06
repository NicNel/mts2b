import bpy
import tempfile
from ..utils import util

class MTS2WorldProps(bpy.types.PropertyGroup):

    mts2_world_path: bpy.props.PointerProperty(name="mts2_world_path", type=bpy.types.Image,
                                             description="")

    mts2_world_power: bpy.props.FloatProperty(name="mts2_world_power",
                                               description="Power",
                                               min=0.0,
                                               default=1.0)
    mts2_world_rotation : bpy.props.FloatVectorProperty(name="mts2_world_rotation", 
                                                description="rotation",
                                                default=(0.0, 0.0, 0.0),
                                                subtype='EULER', 
                                                size=3)
    mts2_world_show_preview: bpy.props.BoolProperty(name="mts2_world_show_preview", default=False, description="Show thumbnail")
    
def register():
    util.register_class(MTS2WorldProps)
    bpy.types.Scene.mts2WorldProps= bpy.props.PointerProperty(type=MTS2WorldProps)

def unregister():
    del bpy.types.Scene.mts2WorldProps
    util.unregister_class(MTS2WorldProps)
