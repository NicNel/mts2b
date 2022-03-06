import bpy
import tempfile
from ..utils import util

class MTS2CameraProps(bpy.types.PropertyGroup):
    mts2_camera_type: bpy.props.EnumProperty(
        name="mts2_camera_type",
        description="camera type",
        items=[
            ("perspective", "perspective", "perspective camera"),
            ("thinlens", "thinlens", "thinlens camera")
            ],
            default="perspective"
    )
    mts2_cam_focus_obj: bpy.props.PointerProperty(name="mts2_cam_focus_obj", type=bpy.types.Object)
    mts2_aperture_radius: bpy.props.FloatProperty(name="mts2_aperture_radius",
                                               description="aperture_radius",
                                               min=0.0,
                                               default=5.6)
    mts2_focus_distance: bpy.props.FloatProperty(name="mts2_focus_distance",
                                               description="focus distance",
                                               min=0.0,
                                               default=1.0)
    

def register():
    util.register_class(MTS2CameraProps)
    bpy.types.Camera.mts2CamProps = bpy.props.PointerProperty(type=MTS2CameraProps)

def unregister():
    del bpy.types.Camera.mts2CamProps
    util.unregister_class(MTS2CameraProps)
