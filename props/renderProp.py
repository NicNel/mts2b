import bpy
import tempfile
from ..utils import util

class MTS2RenderProps(bpy.types.PropertyGroup):
    mts2_project_dir: bpy.props.StringProperty(name="mts2_project_dir",
                                             description="",
                                             default=util.switchpath(tempfile.gettempdir())+'/',
                                             subtype='DIR_PATH')
    mts2_bin_dir: bpy.props.StringProperty(name="mts2_bin_dir",
                                             description="",
                                             default=util.switchpath(tempfile.gettempdir())+'/',
                                             subtype='DIR_PATH')
    mts2_oidn_dir: bpy.props.StringProperty(name="mts2_oidn_dir",
                                             description="",
                                             default=util.switchpath(tempfile.gettempdir())+'/',
                                             subtype='DIR_PATH')
    mts2_denoiser_type: bpy.props.EnumProperty(
        name="mts2_denoiser_type",
        description="type",
        items=[
            ("optix", "Optix", "Optix denoiser"),
            ("oidn", "Oidn External", "Oidn External denoiser")],
            default = "optix"
    )
    mts2_integrator: bpy.props.EnumProperty(name="mts2_integrator",
                                          description="mts2_integrator",
                                          items=[("direct", "direct", "direct Integrator"),
                                                 ("path", "path", "path Integrator"),
                                                 ("aov", "aov", "Arbitrary Output Variables Integrator"),
                                                 ("stokes", "stokes", "stokes Integrator"),
                                                 ("moment", "moment", "moment Integrator"),
                                                 ("volpathmis", "volpathmis", "volpathmis Integrator"),
                                                 ("volpath", "volpath", "volpath Integrator")],
                                          default='path')
    mts2_subintegrator: bpy.props.EnumProperty(name="mts2_subintegrator",
                                          description="mts2_subintegrator",
                                          items=[("direct", "direct", "direct Integrator"),
                                                 ("path", "path", "path Integrator"),
                                                 ("volpathmis", "volpathmis", "volpathmis Integrator"),
                                                 ("volpath", "volpath", "volpath Integrator")],
                                          default='path')
                                          
    mts2_mode: bpy.props.EnumProperty(name="mts2_mode",
                                          description="mts2_mode",
                                          items=[("scalar_rgb", "scalar_rgb", "scalar_rgb Integrator"),
                                                 ("scalar_spectral", "scalar_spectral", "scalar_spectral Integrator"),
                                                 ("packet_spectral", "packet_spectral", "packet_spectral Integrator")],
                                          default='scalar_spectral')
                                      
    mts2_export_scene_only: bpy.props.BoolProperty(name="mts2_export_scene_only",
                                                    description="",
                                                    default=False)
    mts2_spp: bpy.props.IntProperty(
        name="mts2_spp",
        description="Number of samples spp",
        default=24,
        min=1
    )
    mts2_max_depth: bpy.props.IntProperty(
        name="mts2_max_depth",
        default=-1,
        min=-1
    )
    mts2_sampler: bpy.props.EnumProperty(
        name="mts2_sampler",
        description="Sampler",
        items=[
            ("independent", "independent", "independent Sampler"),
            ("stratified", "stratified", "stratified Sampler"),
            ("multijitter", "multijitter", "multijitter Sampler"),
            ("orthogonal", "orthogonal", "orthogonal Sampler"),
            ("ldsampler", "ldsampler", "ldsampler Sampler")],
            default = "independent"
    )
    mts2_component_format: bpy.props.EnumProperty(
        name="mts2_component_format",
        description="component format",
        items=[
            ("float16", "float16", "float16"),
            ("float32", "float32", "float32"),
            ("uint32", "uint32", "uint32")],
            default = "float32"
    )
    mts2_pixel_format: bpy.props.EnumProperty(
        name="mts2_pixel_format",
        description="pixel_format",
        items=[
            ("luminance", "luminance", "luminance"),
            ("luminance_alpha", "luminance_alpha", "luminance_alpha"),
            ("rgb", "rgb", "rgb"),
            ("rgba", "rgba", "rgba"),
            ("xyz", "xyz", "xyz"),
            ("xyza", "xyza", "xyza")],
            default = "rgb"
    )
    mts2_rfilter: bpy.props.EnumProperty(
        name="mts2_rfilter",
        description="reconstruction filter",
        items=[
            ("box", "box", "box"),
            ("tent", "tent", "tent"),
            ("gaussian", "gaussian", "gaussian"),
            ("mitchell", "mitchell", "mitchell"),
            ("catmullrom", "catmullrom", "catmullrom"),
            ("lanczos", "lanczos", "lanczos")],
            default = "box"
    )
    mts2_prev_fov: bpy.props.FloatProperty(name="mts2_prev_fov",
                                               description="Preview camera fov",
                                               min=1,
                                               default=18)
    mts2_prev_samples: bpy.props.IntProperty(
        name="mts2_prev_samples",
        default=24,
        min=0
    )

class runRenderOperator(bpy.types.Operator):
    bl_idname = 'mts2op.start_render'
    bl_label = 'start render'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
        #bpy.ops.mesh.primitive_cube_add()
        #bpy.context.scene.render.RunTestOperator()
        return {"FINISHED"}
        
class runRenderAnimOperator(bpy.types.Operator):
    bl_idname = 'mts2op.start_render_anim'
    bl_label = 'start render animation'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
        return {"FINISHED"}
  
def register():
    bpy.utils.register_class(runRenderOperator)
    bpy.utils.register_class(runRenderAnimOperator)
    util.register_class(MTS2RenderProps)
    bpy.types.Scene.mts2RProps = bpy.props.PointerProperty(type=MTS2RenderProps)

def unregister():
    bpy.utils.unregister_class(runRenderOperator)
    bpy.utils.unregister_class(runRenderAnimOperator)
    
    del bpy.types.Scene.mts2RProps
    util.unregister_class(MTS2RenderProps)
