import bpy
from bl_ui.properties_render import RenderButtonsPanel
from bl_ui.properties_world import WorldButtonsPanel
from bl_ui.properties_material import MaterialButtonsPanel
from bl_ui.properties_object import ObjectButtonsPanel
from bl_ui.properties_data_camera import CameraButtonsPanel
from bpy.types import Panel, Menu

class MTS2_RENDER_PT_System(RenderButtonsPanel, Panel):
    COMPAT_ENGINES = {"MTS2"}
    bl_label = "System"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.mts2RProps
        layout.operator("mts2op.start_render", text="Start render")
        layout.operator("mts2op.start_render_anim", text="Start animation render")
        layout.prop(asr_scene_props, "mts2_export_scene_only", text="export scene only")
        layout.prop(asr_scene_props, "mts2_mode", text="Run mode")
        
        #layout.separator()
        #layout.label(text="Mitsuba2 bin folder:")
        layout.prop(asr_scene_props, "mts2_bin_dir", text="mitsuba2 bin")
        #layout.separator()
        #layout.label(text="Project folder:")
        layout.prop(asr_scene_props, "mts2_project_dir", text="project folder")
        #layout.prop(asr_scene_props, "mts2_oidn_dir", text="oidn folder")
        

class MTS2_RENDER_PT_Sensor(RenderButtonsPanel, Panel):
    COMPAT_ENGINES = {"MTS2"}
    bl_label = "Sensor"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.mts2RProps
        layout.label(text="Integrator parameters")
        layout.prop(asr_scene_props, "mts2_integrator", text="Integrator")
        if asr_scene_props.mts2_integrator == "aov":
            layout.prop(asr_scene_props, "mts2_subintegrator", text="subintegrator")
            layout.prop(asr_scene_props, "mts2_denoiser_type", text="denoiser")
            if asr_scene_props.mts2_denoiser_type == "oidn":
                layout.prop(asr_scene_props, "mts2_oidn_dir", text="oidn folder")
        layout.prop(asr_scene_props, "mts2_sampler", text="Sampler")
        layout.prop(asr_scene_props, "mts2_spp", text="spp")
        layout.prop(asr_scene_props, "mts2_max_depth", text="max depth")
        
class MTS2_RENDER_PT_Film(RenderButtonsPanel, Panel):
    COMPAT_ENGINES = {"MTS2"}
    bl_label = "Film"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.mts2RProps
        layout.prop(asr_scene_props, "mts2_component_format", text="component format")
        layout.prop(asr_scene_props, "mts2_pixel_format", text="pixel format")
        layout.prop(asr_scene_props, "mts2_rfilter", text="rfilter")
        
class MTS2_MATERIAL_PT_Slots(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_label = "Material"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and engine == 'MTS2'

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 3
            if (is_sortable):
                rows = 5

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ADD', text="")
            col.operator("object.material_slot_remove", icon='REMOVE', text="")

            col.separator()

            col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        row = layout.row()

        if ob:
            row.template_ID(ob, "active_material", new="material.new")

            if slot:
                icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
                row.prop(slot, "link", icon=icon_link, icon_only=True)

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        elif mat:
            row.template_ID(space, "pin_id")

class PBRTV4_MATERIAL_PT_emissions(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_label = "Material"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and engine == 'PBRTV4'

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data
        
        if ob:
            #print (mat.pbrtv4_emission_color[0])
            layout.prop(mat, "pbrtv4_isEmissive", text="Enable emission")
            
            if mat.pbrtv4_isEmissive == True:
                col = layout.column(align=True)
                col.prop(mat, "pbrtv4_emission_preset", text="Preset")
                if mat.pbrtv4_emission_preset == 'color':
                    col.prop(mat, "pbrtv4_emission_color", text="Color")
                elif mat.pbrtv4_emission_preset == 'blackbody':
                    col.prop(mat, "pbrtv4_emission_temp", text="Temperature")
                col.prop(mat, "pbrtv4_emission_power", text="Power")
        elif mat:
            pass
            #row.template_ID(space, "pin_id")
class MTS2_PT_MATERIAL_Previev(MaterialButtonsPanel, Panel):
    COMPAT_ENGINES = {"MTS2"}
    bl_label = "Preview"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (engine == "MTS2")

    def draw(self, context):
        layout = self.layout
        #image = bpy.ops.image.open(filepath="")
        #preview_mat
        scene_props = context.scene.mts2RProps
        layout.template_preview(context.material, show_buttons=False)
        layout.prop(scene_props, "mts2_prev_fov", text="fov")
        layout.prop(scene_props, "mts2_prev_samples", text="spp")
        
class PBRTV4_PT_OBJECT_prop(ObjectButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_context = "object"
    bl_label = "PBRTV4Settings"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.object and (engine == "PBRTV4")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        layout.prop(obj, "pbrtv4_isPortal", text="Is Portal")
        
class MTS2_WORLD_PT_Common(WorldButtonsPanel, Panel):
    COMPAT_ENGINES = {"MTS2"}
    bl_label = "World Light"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.mts2WorldProps

        col = layout.column(align=True)
        col.prop(asr_scene_props, "mts2_world_show_preview", text="show preview")
        if asr_scene_props.mts2_world_show_preview:
            col.template_ID_preview(asr_scene_props, "mts2_world_path", open="image.open")
        else:
            col.template_ID(asr_scene_props, "mts2_world_path", open="image.open")
        col.prop(asr_scene_props, "mts2_world_power", text="Power")
        col.prop(asr_scene_props, "mts2_world_rotation", text="Rotation")
            
class MTS2_CAMERA_PT_Common(CameraButtonsPanel, Panel):
    COMPAT_ENGINES = {"MTS2"}
    bl_label = "MTS2 Camera"
    #bl_context = "camera"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0
    
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.camera and (engine == 'MTS2')
    def update_object(self, context):
        cam_ob = context.camera
        #cam_d = context.camera.pbrtv4_camera.pbrtv4_camera_focaldistance
        #target_dist = (cam_ob.pbrtv4_camera.pbrtv4_camera_focus_obj.location - cam_ob.location).length
        #cam_d = target_dist
    def draw(self, context):
        layout = self.layout
        cam = context.camera.mts2CamProps
        layout.prop(cam, "mts2_camera_type", text="Camera type")
        if cam.mts2_camera_type == "perspective":
            # layout.prop(cam, "pbrtv4_realistic_camera_file", text="realistic camera file")
            # layout.prop(cam, "pbrtv4_realistic_camera_apperture", text="realistic camera apperture type")
            # layout.prop_search(cam, "pbrtv4_camera_focus_obj", bpy.data, "objects",  text="target object")
            # layout.prop(cam, "pbrtv4_camera_lensradius", text="F value (lens radius=(1/F))")
            # if not cam.pbrtv4_camera_focus_obj:
                # layout.prop(cam, "pbrtv4_camera_focaldistance", text="camera focal distance")
            pass
        elif cam.mts2_camera_type == "thinlens":
            layout.prop_search(cam, "mts2_cam_focus_obj", bpy.data, "objects",  text="target object")
            layout.prop(cam, "mts2_aperture_radius", text="f-value")
            layout.prop(cam, "mts2_focus_distance", text="focus distance")
            
            # if cam.pbrtv4_camera_use_dof:
                # layout.prop_search(cam, "pbrtv4_camera_focus_obj", bpy.data, "objects",  text="target object")
                # layout.prop(cam, "pbrtv4_camera_lensradius", text="F value (lens radius=(1/F))")
                # if not cam.pbrtv4_camera_focus_obj:
                    # layout.prop(cam, "pbrtv4_camera_focaldistance", text="camera focal distance")
            #pass    

def register():
    bpy.utils.register_class(MTS2_RENDER_PT_System)
    bpy.utils.register_class(MTS2_RENDER_PT_Sensor)
    bpy.utils.register_class(MTS2_RENDER_PT_Film)
    bpy.utils.register_class(MTS2_CAMERA_PT_Common)
    bpy.utils.register_class(MTS2_WORLD_PT_Common)
    bpy.utils.register_class(MTS2_MATERIAL_PT_Slots)
    bpy.utils.register_class(MTS2_PT_MATERIAL_Previev)
    
def unregister():
    bpy.utils.unregister_class(MTS2_RENDER_PT_System)
    bpy.utils.unregister_class(MTS2_RENDER_PT_Sensor)
    bpy.utils.unregister_class(MTS2_RENDER_PT_Film)
    bpy.utils.unregister_class(MTS2_CAMERA_PT_Common)
    bpy.utils.unregister_class(MTS2_WORLD_PT_Common)
    bpy.utils.unregister_class(MTS2_MATERIAL_PT_Slots)
    bpy.utils.unregister_class(MTS2_PT_MATERIAL_Previev)