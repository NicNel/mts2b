import bpy
import os
import math
import threading
import time
import numpy as np

from .utils.dict2xml import dict2xml
from .utils.util import createFolder, runCmd, matrixtostr, vectortostr, switchpath, realpath, calcFovRAD, Lerp, InvLerp

from .export.geometry import GeometryExporter
from .preview.prepare import preparePreview

# Render engine ================================================================================
class MTS2enderEngine(bpy.types.RenderEngine):
    bl_idname = "MTS2" # internal name
    bl_label = "MTS2 Renderer" # Visible name
    bl_use_preview = True
    bl_use_material = True
    bl_use_shading_nodes = False
    bl_use_shading_nodes_custom = False
    bl_use_texture_preview = True
    bl_use_texture = True
    is_busy = False
    bl_use_eevee_viewport = True
    #bl_use_shading_nodes_custom = True
    
    def render(self, depsgraph):
        if self.is_preview:
            self.PreviewRender(depsgraph)
        else:
            self.FinalRender(depsgraph)
    
    def LoadRenderResult(self, file, sx, sy):
        result = self.begin_result(0, 0, sx, sy)
        layer = result.layers[0]
        layer.load_from_file(file)
        self.end_result(result)
        
    def PreviewRender(self, depsgraph):
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        size_x = int(scene.render.resolution_x * scale)
        size_y = int(scene.render.resolution_y * scale)
        
        if max(size_x,  size_y) >= 96:
            print("Start preview render")
            p = self.getProps()
            preparePreview(p["previewFolder"])
            
            bsdfs = 'bsdfs.xml'
            geometry = "geometry.xml"
            bsdfs_base = 'bsdfs_base.xml'
            geometry_base = 'geometry_base.xml'
            settings_base = 'settings_base.xml'
            
            scene_dict = {"version":"2.0.0"}
            scene_dict["default"] = [
                {"name":"resXPar", "value":size_x},
                {"name":"resYPar", "value":size_y},
                {"name":"fovPar", "value":p["mts2_prev_fov"]},
                {"name":"sppPar", "value":p["mts2_prev_samples"]}
            ]
            scene_dict["include"] = [
                {"filename":bsdfs},
                {"filename":geometry},
                {"filename":bsdfs_base},
                {"filename":geometry_base},
                {"filename":settings_base}
            ]
            data = dict2xml(scene_dict, 'scene')
            
            #test write file
            with open(p["previewSceneFile"], 'w') as f:
                f.write(data)
                f.close()
            
            #export bsdf
            matData = {}
            mat_name = "preview_mat"
            mat = bpy.context.view_layer.objects.active.active_material
            
            mat_dict = GeometryExporter.export_mat_get(mat, mat_name)
            xml_data = dict2xml(mat_dict["data"], "scene", "")
            with open(bsdfs, 'w') as f:
                f.write(xml_data)
                f.close()
                
            #export main object geometry
            transform = "1.000000 0.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 0.000000 1.000000 1.000000 0.000000 0.000000 0.000000 1.000000"
            g = {"version":"2.0.0"}
            g["shape"] = []
            if len(mat_dict["emitter"])>0:
                par = mat_dict["emitter"][mat_name]
                em_dict = {}
                em_dict["type"] = "area"
                em_dict.update(par)
                g["shape"].append(GeometryExporter.exportShape("", "geometry\outer_sphere-preview_mat.ply", 0, transform, mat_name, em_dict))
            else:
                g["shape"].append(GeometryExporter.exportShape("", "geometry\outer_sphere-preview_mat.ply", 0, transform, mat_name))
            g_data = dict2xml(g, "scene", "")
            with open(geometry, 'w') as f:
                f.write(g_data)
                f.close()
                
            p["size_x"] = size_x
            p["size_y"] = size_y
            self.RunPreviewRender(depsgraph, p)
        
    def FinalRender(self, depsgraph):
        props = self.getProps()
        if not props["scene_only"]:
            self.exportObjects(depsgraph, props)
        self.exportScene(props)
        self.exportSettings(depsgraph, props)
        self.RunRender(depsgraph, props)
    
    def getProps(self):
        p = {}
        #props
        p["project_dir"] = bpy.context.scene.mts2RProps.mts2_project_dir
        p["bin_dir"] = bpy.context.scene.mts2RProps.mts2_bin_dir
        p["spp"] = bpy.context.scene.mts2RProps.mts2_spp
        p["max_depth"] = bpy.context.scene.mts2RProps.mts2_max_depth
        p["integrator"] = bpy.context.scene.mts2RProps.mts2_integrator
        p["subintegrator"] = bpy.context.scene.mts2RProps.mts2_subintegrator
        
        p["scene_only"] = bpy.context.scene.mts2RProps.mts2_export_scene_only
        p["sampler"] = bpy.context.scene.mts2RProps.mts2_sampler
        p["component_format"] = bpy.context.scene.mts2RProps.mts2_component_format
        p["pixel_format"] = bpy.context.scene.mts2RProps.mts2_pixel_format
        p["mts2_rfilter"] = bpy.context.scene.mts2RProps.mts2_rfilter
        
        p["mts2_prev_samples"] = bpy.context.scene.mts2RProps.mts2_prev_samples
        p["mts2_prev_fov"] = bpy.context.scene.mts2RProps.mts2_prev_fov
        
        p["world_rotation"] = bpy.context.scene.mts2WorldProps.mts2_world_rotation
        
        p["geometryFolder"] = os.path.join(p["project_dir"], "geometry")
        p["texturesFolder"] = os.path.join(p["project_dir"], "textures")
        p["previewFolder"] = os.path.join(p["project_dir"], "preview")
        p["geometryFolder"] = createFolder(p["geometryFolder"])
        p["texturesFolder"] = createFolder(p["texturesFolder"])
        p['compute_mode'] = 'CPU'
        p['run_mode'] = bpy.context.scene.mts2RProps.mts2_mode
        
        p['denoiser'] = bpy.context.scene.mts2RProps.mts2_denoiser_type
        p['oidn'] = bpy.context.scene.mts2RProps.mts2_oidn_dir
        
        
        #files
        p["sceneFile"] = os.path.join(p["project_dir"], 'scene.xml')
        p["previewSceneFile"] = os.path.join(p["previewFolder"], 'scene.xml')
        p["settingsFile"] = os.path.join(p["project_dir"], 'settings.xml')
        p["geometryFile"] = os.path.join(p["project_dir"], 'geometry.xml')
        p["bsdfsFile"] = os.path.join(p["project_dir"], 'bsdfs.xml')
        p['rendered_file'] = os.path.join(p["project_dir"], 'scene.exr')
        p['denoised_file'] = os.path.join(p["project_dir"], 'denoised.exr')
        p['rendered_preview_file'] = os.path.join(p["previewFolder"], 'scene.exr')
        
        p["mts2BinFile"] = os.path.join(p["bin_dir"], 'mitsuba.exe')
        p["mts2ImgtoolFile"] = os.path.join(p["bin_dir"], 'imgtool.exe')
        
        return p
        
    def exportObjects(self, depsgraph, p):
        geometry_exporter = GeometryExporter()
        linked_as_instance = True
        data = geometry_exporter.ExportSceneGeometry(depsgraph, p["geometryFolder"], self, linked_as_instance)
        #test write file
        with open(p["geometryFile"], 'w') as f:
            f.write(data[0])
            f.close()
        with open(p["bsdfsFile"], 'w') as f:
            f.write(data[1])
            f.close()
         
    def exportIntegrator(self, p):
        integrator_dict = {}
        integrator_dict["type"] = p["integrator"]
        if p["integrator"] == "aov":
            integrator_dict["string"] = {"name":"aovs", "value":"zDepth:depth, Sh_Normal:sh_normal, Albedo:albedo"}
            integrator_dict["integrator"] = {"type":p["subintegrator"], "name":"Beauty", "integer":{"name":"max_depth", "value":p["max_depth"]}}
        else:
            if not p["integrator"] == "direct":
                integrator_dict["integer"] = []
                integrator_dict["integer"].append({"name":"max_depth", "value":p["max_depth"]})
        #data = dict2xml(integrator_dict, 'integrator', "")
        return integrator_dict
        
    def exportSampler(self, p):
        sampler_dict = {}
        sampler_dict["type"] = p["sampler"]
        sampler_dict["integer"] = []
        sampler_dict["integer"].append({"name":"sample_count", "value":p["spp"]})
        #data = dict2xml(sampler_dict, 'integrator', "")
        return sampler_dict
    
    def exportEnv(self, p):
        if bpy.context.scene.mts2WorldProps.mts2_world_path:
            filePath = bpy.context.scene.mts2WorldProps.mts2_world_path.filepath
            file = switchpath(realpath(filePath))
            scale = bpy.context.scene.mts2WorldProps.mts2_world_power
            r = p["world_rotation"]
            
            env_dict = {}
            env_dict["type"] = "envmap"
            env_dict["id"] = "emitter-envmap"
            
            env_dict["string"] = {"name":"filename", "value":file}
            env_dict["float"] = {"name":"scale", "value":scale}
            
            transform = {"name":"to_world"}
            transform["rotate"]=[{"x":"1", "angle":180.0 / math.pi*r[0]}]
            transform["rotate"].append({"y":"1", "angle":180.0 / math.pi*r[1]})
            transform["rotate"].append({"z":"1", "angle":180.0 / math.pi*r[2]})
            env_dict["transform"] = transform
            #data = dict2xml(env_dict, 'integrator', "")
            return env_dict
        return None
        
    def exportFilm(self, depsgraph, p):
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        sx = int(scene.render.resolution_x * scale)
        sy = int(scene.render.resolution_y * scale)
        render = scene.render
        use_border = render.use_border
        film_dict = {}
        film_dict["type"] = "hdrfilm"
        film_dict["integer"] = []
        film_dict["string"] = []
        film_dict["integer"].append({"name":"width", "value":sx})
        film_dict["integer"].append({"name":"height", "value":sy})
        film_dict["rfilter"] = {"type":p["mts2_rfilter"]}
        film_dict["string"].append({"name":"pixel_format", "value":p["pixel_format"]})
        film_dict["string"].append({"name":"component_format", "value":p["component_format"]})
        #data = dict2xml(film_dict, 'integrator', "")
        
        p["size_x"] = sx
        p["size_y"] = sy
        
        if use_border:
            min_x = int(Lerp(0, sx, render.border_min_x))
            min_y = int(Lerp(0, sy, render.border_min_y))
            max_x = int(Lerp(0, sx, render.border_max_x))
            max_y = int(Lerp(0, sy, render.border_max_y))
            film_dict["integer"].append({"name":"crop_offset_x", "value":min_x})
            film_dict["integer"].append({"name":"crop_offset_y", "value":sy - max_y})
            film_dict["integer"].append({"name":"crop_width", "value":max_x - min_x})
            film_dict["integer"].append({"name":"crop_height", "value":max_y - min_y})
        return film_dict
    
    def exportSensor(self, depsgraph, p):
        scene = depsgraph.scene
        cam_ob = scene.camera
        
        cameramatrix = cam_ob.matrix_world.copy()
        matrixTransposed = cameramatrix.transposed()
        up_point = matrixTransposed[1]

        from_point=cam_ob.matrix_world.col[3]
        at_point=cam_ob.matrix_world.col[2]
        at_point=at_point * -1
        at_point=at_point + from_point
        
        fov = calcFovRAD(scene.render.resolution_x, scene.render.resolution_y, cam_ob.data.angle)
        cam_type = cam_ob.data.mts2CamProps.mts2_camera_type
        radius = cam_ob.data.mts2CamProps.mts2_aperture_radius
        focus_obj = cam_ob.data.mts2CamProps.mts2_cam_focus_obj
        
        sensor_dict = {}
        sensor_dict["type"] = cam_type
        sensor_dict["string"] = []
        sensor_dict["string"].append({"name":"fov_axis", "value":"smaller"})
        
        sensor_dict["float"] = []
        sensor_dict["float"].append({"name":"near_clip", "value":cam_ob.data.clip_start})
        sensor_dict["float"].append({"name":"far_clip", "value":cam_ob.data.clip_end})
        sensor_dict["float"].append({"name":"fov", "value":fov})
        
        shiftX = cam_ob.data.shift_x
        shiftY = cam_ob.data.shift_y
        sensor_dict["float"].append({"name":"principal_point_offset_x", "value":shiftX})
        sensor_dict["float"].append({"name":"principal_point_offset_y", "value":-shiftY})
        
        if cam_type == "thinlens":
            target_dist = -1
            if focus_obj:
                target_dist = (focus_obj.location - cam_ob.location).length
                print("CAMERA DISTANCE >>>", target_dist)
            if target_dist>0:
                cam_ob.data.mts2CamProps.mts2_focus_distance = target_dist
            else:
                target_dist = cam_ob.data.mts2CamProps.mts2_focus_distance
            #https://photo.stackexchange.com/questions/79605/how-do-i-correctly-convert-from-aperture-diameter-into-f-stops
            f_value = radius
            sensor_size = ((cam_ob.data.lens / f_value)/1000.0)#/2.0 #diameter or radius?
            print("aperture_radius: ", sensor_size)
            sensor_dict["float"].append({"name":"aperture_radius", "value":sensor_size})
            sensor_dict["float"].append({"name":"focus_distance", "value":target_dist})
        
        matrix = {"origin":vectortostr(from_point), "target":vectortostr(at_point), "up":vectortostr(up_point)}
        transform = {"name":"to_world", "lookat" : matrix}
        sensor_dict["transform"] = transform
        
        sensor_dict["sampler"] = self.exportSampler(p)
        sensor_dict["film"] = self.exportFilm(depsgraph, p)
        
        return sensor_dict
    
    def exportSettings(self, depsgraph, p):
        scene_dict = {"version":"2.0.0"}
        scene_dict["integrator"] = self.exportIntegrator(p)
        scene_dict["sensor"] = self.exportSensor(depsgraph, p)
        scene_dict["emitter"] = self.exportEnv(p)
        
        data = dict2xml(scene_dict, 'scene')
        
        #test write file
        with open(p["settingsFile"], 'w') as f:
            f.write(data)
            f.close()
        
    def exportScene(self, p):
        scene_dict = {"version":"2.0.0"}
        scene_dict["include"] = [
            {"filename":p["settingsFile"]},
            {"filename":p["bsdfsFile"]},
            {"filename":p["geometryFile"]}
        ]
        data = dict2xml(scene_dict, 'scene')
        
        #test write file
        with open(p["sceneFile"], 'w') as f:
            f.write(data)
            f.close()
    
    def RunRender(self, depsgraph, p):
        # Compute pbrt executable path
        mts2BinFile = p["mts2BinFile"]
        sceneFile = p["sceneFile"]
        #start render
        if p['compute_mode'] == 'CPU':
            cmd = [ mts2BinFile, '-m', p['run_mode'], sceneFile ]
        else:
            cmd = [ mts2BinFile, '-m', p['run_mode'], sceneFile ]
        runCmd(cmd)
        
        if p["integrator"] == "aov":
            if p['denoiser'] == "optix":
                denoisedFile = p['denoised_file']
                self.denoiseOptix(p)
            else:
                ext = "pfm"
                aov = p['rendered_file']
                self.SplitGbuffer(p, aov, ext)
                beauty = switchpath(p["project_dir"])+'/'+'{}.{}'.format("pass_0",ext)
                albedo = switchpath(p["project_dir"])+'/'+'{}.{}'.format("pass_1",ext)
                normal = switchpath(p["project_dir"])+'/'+'{}.{}'.format("pass_2",ext)
                self.denoiseOIDN(p, beauty, albedo, normal, p['denoised_file'])
            self.loadResult(p['denoised_file'], p)
        else:
            self.loadResult(p['rendered_file'], p)
    
    def RunPreviewRender(self, depsgraph, p):
        # Compute pbrt executable path
        mts2BinFile = p["mts2BinFile"]
        sceneFile = p["previewSceneFile"]
        #start render
        if p['compute_mode'] == 'CPU':
            cmd = [ mts2BinFile, '-m', 'scalar_spectral', sceneFile ]
        else:
            cmd = [ mts2BinFile, '-m', 'scalar_spectral', sceneFile ]
        runCmd(cmd)
        #result = self.get_result()
        #result.layers[0].load_from_file(p['rendered_preview_file'])
        self.LoadRenderResult(p['rendered_preview_file'], p["size_x"], p["size_y"])
        
    def denoiseOptix(self, p):
        imgtoolPath = p["mts2ImgtoolFile"]
        aov = p['rendered_file']
        result = p['denoised_file']
        cmd = [ imgtoolPath, "denoise-optix2", aov, "-outfile", result]
        runCmd(cmd)
        
    def SplitGbuffer(self, p, file, ext):
        imgtoolPath = p["mts2ImgtoolFile"]
        cmd = [ imgtoolPath, "split-gbuffer2", file, "--ext", ext]
        #cmd = [ itoolExecPath, "split-gbuffer", file, "--outpath", folder]
        runCmd(cmd)
        
    def denoiseOIDN(self, p, beauty, albedo, normal, result):
        imgtoolPath = p["mts2ImgtoolFile"]
        denoisedPfm = switchpath(p["project_dir"])+'/'+'{}.pfm'.format("denoised")
        denoiserExecPath = switchpath(p['oidn'])+'/'+'oidnDenoise.exe'
        cmd = [ denoiserExecPath, "-hdr", beauty, "-alb", albedo, "-nrm", normal, "-o", denoisedPfm]
        runCmd(cmd)
        cmd = [ imgtoolPath, "convert", denoisedPfm, "--outfile", result]
        runCmd(cmd)
    
    def loadResult(self, file, p):
        outImagePath = file
        #result = self.get_result()
        #result.layers[0].load_from_file(outImagePath)
        self.LoadRenderResult(outImagePath, p["size_x"], p["size_y"])