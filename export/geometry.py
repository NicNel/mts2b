from .mesh_ply import write_ply_mesh
import os
import bpy
import copy

from ..utils import util
from ..utils.dict2xml import dict2xml
import mathutils
import numpy as np

class GeometryExporter:
    """
    Encapsulates mesh export methods, and keeps track of exported objects.
    This is necessary in order to export meshes with multiple materials.
    """
    need_update=False
    
    def __init__(self):
        self.exported_meshes = {} # dict containing entries like mesh_name : [exported materials]
        self.exported_materials = set() # exported materials
        self.materialData = {}
        self.areaEmitterData = {}
        self.objectData = {}
        self.instancedData = []
        self.lightsData = []
        
        self.linkedData = []
        self.linkedName = []
    
    @staticmethod
    def exportShape(id, file, idx, t_m, mat_id, emitter = None, isString = False):
        shape_dict = {}
        shape_dict["type"] = "ply"
        #shape_dict["id"] = id
        
        shape_dict["string"] = {"name":"filename", "value":file}
        #shape_dict["integer"] = {"name":"shape_index", "value":idx}
        
        matrix = {"value":t_m}
        transform = {"name":"to_world", "matrix" : matrix}
        shape_dict["transform"] = transform
        
        if not emitter is None:
            shape_dict["emitter"] = emitter
        
        shape_dict["ref"] = {"name":"bsdf", "id" : mat_id}
        if isString:
            data = dict2xml(shape_dict, "shape", "")
            return data
        return shape_dict
    
    def exportInstance(self, refid, t_m, isString = False):
        shape_dict = {}
        shape_dict["type"] = "instance"
        #shape_dict["id"] = id
        
        shape_dict["ref"] = {"id":refid}
        
        if not t_m is None:
            matrix = {"value":t_m}
            transform = {"name":"to_world", "matrix" : matrix}
            shape_dict["transform"] = transform
        
        if isString:
            data = dict2xml(shape_dict, "shape", "")
            return data
        return shape_dict
    
    @staticmethod
    def addDefaultMat(data, id):
        bsdf_dict = {}
        bsdf_dict["type"] = "diffuse"
        bsdf_dict["id"] = id
        bsdf_dict["rgb"] = {"name":"reflectance", "value":"0.8, 0.0, 0.0"}
        data['bsdf'].append(bsdf_dict)
        
    @staticmethod
    def export_mat_get(mat, export_name):
        outInfo = {}
        emData = {}
        matData = {"version":"2.0.0"}
        matData["bsdf"] = []
        matData["texture"] = []
        matData["emitter"] = []
        
        outInfo["mat_name"]=export_name
        OutputNode = mat.node_tree.nodes.get('Material Output')
        
        input = OutputNode.inputs[0] #shader input
        if input.is_linked:
            node_link = input.links[0]
            curNode =  node_link.from_node
            
            ID = 0
            #OutputNode = None
            ExportedNodes = []
            for node in mat.node_tree.nodes:
                if hasattr(node, 'isMts2TreeNode'):
                    node.setId(mat.name, ID)
                    ID+=1
            if hasattr(curNode, 'isMts2TreeNode'):
                #set material name instead of generated
                if hasattr(curNode, 'isMts2AreaEmitter'):
                    curNode.label = export_name
                    curNode.to_dict(ExportedNodes, matData)
                    emData[export_name] = curNode.em_to_dict(ExportedNodes, matData, "area_em_"+export_name)
                else:
                    curNode.label = export_name
                    curNode.Backprop(ExportedNodes, matData)
            else:
                print("error: ", mat.name, " not valid mts2 bsdf")
                GeometryExporter.addDefaultMat(matData, export_name)
        else:
            print("error: ", mat.name, " not valid mts2 bsdf")
            GeometryExporter.addDefaultMat(matData, export_name)
        return {"info":outInfo, "data":matData, "emitter":emData}
        
    def export_mat(self, object_instance, matid, customData = None, customExported = None):
        outInfo = {}
        matData = customData if not customData is None else self.materialData
        exported_lst = customExported if not customExported is None else self.exported_materials
        
        mat = object_instance.object.material_slots[matid].material
        #print ('Exporting material: ', mat.name)
        outInfo["mat_name"]=mat.name
        OutputNode = mat.node_tree.nodes.get('Material Output')
        #export medium
        volume_input = OutputNode.inputs[1] #shader volume
        
        if volume_input.is_linked:
            volume_node_link = volume_input.links[0]
            volume =  volume_node_link.from_node
            #volume.label = export_name+"_volume"
            medium_id ="{}::{}".format(object_instance.object.name, matid)
            volume.setId(mat.name, medium_id)
            #volume.label = "{}::{}".format(volume.label, object_instance.object.name) #export medium for each part
            #volume.Backprop(outInfo, self.materialData)
        #export material nodetree
        #check for emission
        input = OutputNode.inputs[0] #shader input
        if input.is_linked:
            node_link = input.links[0]
            curNode =  node_link.from_node
            if not mat.name in exported_lst:
                ID = 0
                #OutputNode = None
                ExportedNodes = []
                for node in mat.node_tree.nodes:
                    if hasattr(node, 'isMts2TreeNode'):
                        node.setId(mat.name, ID)
                        ID+=1
                #input = OutputNode.inputs[0] #shader input
                #node_link = input.links[0]
                #curNode =  node_link.from_node
                if hasattr(curNode, 'isMts2TreeNode'):
                    #set material name instead of generated
                    if hasattr(curNode, 'isMts2AreaEmitter'):
                        curNode.label = mat.name
                        curNode.to_dict(ExportedNodes, matData)
                        self.areaEmitterData[mat.name] = curNode.em_to_dict(ExportedNodes, matData, "area_em_"+mat.name)
                    else:
                        curNode.label = mat.name
                        curNode.Backprop(ExportedNodes, matData)
                else:
                    #not bpbrt material
                    #add default instead
                    print("error: ", mat.name, " not valid mts2 bsdf")
                    GeometryExporter.addDefaultMat(matData, mat.name)
                #exported_lst.add(mat.name)
                exported_lst.add(mat.name)
            else:
                pass
                #print(mat.name, " already exported")
        else:
            print("error: ", mat.name, " not valid mts2 bsdf")
            GeometryExporter.addDefaultMat(matData, mat.name)
        return outInfo
                        
    def save_mesh(self, b_mesh, matrix_world, b_name, file_path, mat_nr, info, mat_info):
        b_mesh.calc_normals()
        b_mesh.calc_loop_triangles() # Compute the triangle tesselation
        if mat_nr == -1:
            name = b_name
            mat_nr=0 # Default value for blender
        else:
            name = "%s-%s" %(b_name, b_mesh.materials[mat_nr].name)
        loop_tri_count = len(b_mesh.loop_triangles)
        if loop_tri_count == 0:
            print("Mesh: {} has no faces. Skipping.".format(name), 'WARN')
            return

		# collect faces by mat index
        ffaces_mats = {}
        mesh_faces = b_mesh.loop_triangles
        cnt =0
        ffaces_mats=[]
        for f in mesh_faces:
            mi = f.material_index
			#create container with mat index
            #if mi not in ffaces_mats.keys():
                #ffaces_mats[mi] = []
			#export only material part / need to be optimized
            if mi == mat_nr:
                ffaces_mats.append(f)
                cnt=cnt+1
        #material_indices = ffaces_mats.keys()
        if cnt > 0: # Only save complete meshes
            #add only parts with data
            #mtInfo = MatInfo.CreateInfo(b_mesh.materials[mat_nr].name, b_mesh.materials[mat_nr].pbrtv4_isEmissive, b_mesh.materials[mat_nr].pbrtv4_emission_color, b_mesh.materials[mat_nr].pbrtv4_emission_power, b_mesh.materials[mat_nr].pbrtv4_emission_preset, b_mesh.materials[mat_nr].pbrtv4_emission_temp)
            #info.addPart(name, mtInfo)
            if mat_info["mat_name"] in self.areaEmitterData:
                    em_dict = {}
                    em_dict["type"] = "area"
                    #em_dict["id"] = id
                    par = self.areaEmitterData[mat_info["mat_name"]]
                    em_dict.update(par)
                    info["shapes"].append(GeometryExporter.exportShape(name, file_path, mat_nr, info["transform"], b_mesh.materials[mat_nr].name, em_dict))
            else:
                info["shapes"].append(GeometryExporter.exportShape(name, file_path, mat_nr, info["transform"], b_mesh.materials[mat_nr].name))
            #info["shapes"].append(self.exportShape(name, file_path, mat_nr, info["transform"], "default_bsdf"))
            write_ply_mesh(file_path, b_name, b_mesh, ffaces_mats)
            return True
        else:
            print("Material ", b_mesh.materials[mat_nr].name, " has no mesh data assigned! Skipped...")
        return False

    def export_object_mat(self, object_instance, mat_nr, info, folder):
        #object export
        b_object = object_instance.object
        if b_object.is_instancer and not b_object.show_instancer_for_render:
            return#don't export hidden mesh
        if mat_nr == -1:
            name = b_object.name_full
        else:
            name = "%s-%s" %(b_object.name_full, b_object.data.materials[mat_nr].name)
        abs_path = os.path.join(folder, "%s.ply" % name)
        if not object_instance.is_instance:
            #save the mesh once, if it's not an instance, or if it's an instance and the original object was not exported
            b_mesh = b_object.to_mesh()
            mat_info = self.export_mat(object_instance, mat_nr)
            if self.save_mesh(b_mesh, b_object.matrix_world, b_object.name_full, abs_path, mat_nr, info, mat_info) and mat_nr >= 0:
                #if len(mat_info)>0:
                #    info.materials[-1].mediumName = mat_info[0]
                #export_material(export_ctx, b_object.data.materials[mat_nr])
                #print(abs_path,"exported")
                pass
            else:
                pass
            b_object.to_mesh_clear()

    def export_object(self, object_instance, folder):
        objectInfo = {}
        objectInfo["transform"] = util.matrixtostr(object_instance.matrix_world)
        objectInfo["shapes"] = []
        mat_count = len(object_instance.object.data.materials)
        valid_mats=0
        #export if mats exist
        for mat_nr in range(mat_count):
            if object_instance.object.data.materials[mat_nr] is not None:
                valid_mats += 1
                self.export_object_mat(object_instance, mat_nr, objectInfo, folder)
        #export with default mat
        if valid_mats == 0: #no material, or no valid material
            self.export_object_mat(object_instance, -1, objectInfo, folder)
        #objectInfo.to_String()
        #print(objectInfo.Transform)
        #print(objectInfo.to_DictStr('geometry/'))
        #group = {}
        #group["type"] = "shapegroup"
        #group["id"] = "id"+object_instance.object.data.name
        #group["shape"] = []
        #group["shape"].extend(objectInfo["shapes"])
        #objectInfo["group"] = group
        
        return objectInfo
   
    def ExportSceneGeometry(self, depsgraph, geometryFolder, engine, linked_as_instance = True):
        self.linkedData = []
        self.objectData={}
        self.areaEmitterData={}
        self.groups = set()
        
        b_scene = depsgraph.scene
        
        self.materialData = {"version":"2.0.0"}
        self.materialData["bsdf"] = []
        self.materialData["texture"] = []
        self.materialData["emitter"] = []
         
        d = {"version":"2.0.0"}
        d["shape"] = []
        #t = "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1"
        #d["shape"].append(self.exportShape("id1", "file1.ply", 1, t))
        
        #main export loop
        #update_progress(progress)
        total_cnt = len(depsgraph.object_instances)
        counter = 0
        for object_instance in depsgraph.object_instances:
            counter = counter + 1
            engine.update_progress(counter/total_cnt)
            evaluated_obj = object_instance.object
            object_type = evaluated_obj.type
            #type: enum in [‘MESH’, ‘CURVE’, ‘SURFACE’, ‘META’, ‘FONT’, ‘ARMATURE’, ‘LATTICE’, ‘EMPTY’, ‘GPENCIL’, ‘CAMERA’, ‘LIGHT’, ‘SPEAKER’, ‘LIGHT_PROBE’], default ‘EMPTY’, (readonly)
            if evaluated_obj.hide_render:
                print ("Object: {} is hidden for render. Ignoring it.".format(evaluated_obj.name), 'INFO')
                continue#ignore it since we don't want it rendered (TODO: hide_viewport)
            
            if object_instance.is_instance:
                Transform = util.matrixtostr(object_instance.matrix_world)
                #instance_data = self.add_instance(evaluated_obj.name, Transform)
                #instStr+=instance_data
                data_name = evaluated_obj.data.name
                self.groups.add(data_name)
                refid = "group"+data_name
                self.objectData[data_name+"_instance"+str(counter)] = self.exportInstance(refid, Transform)
                #print("instance object", data_name)
            
            elif object_type in {'MESH', 'FONT', 'SURFACE', 'META', 'CURVE'}:
                #check if object has linked mesh data:
                #evaluated_obj.data.name //for linked data check
                data_name = evaluated_obj.data.name
                if linked_as_instance and data_name in self.linkedData:
                    #export as instance:
                    obj_data_id = self.linkedData.index(data_name)
                    obj_data_name = self.linkedName[obj_data_id]
                    Transform = util.matrixtostr(object_instance.matrix_world)
                    self.groups.add(data_name)
                    
                    refid = "group"+data_name
                    self.objectData[evaluated_obj.name+"_instance"] = self.exportInstance(refid, Transform)
                    
                    print("Export Linked As Instance Object")
                else:
                    #add data to linked info
                    if linked_as_instance:
                        self.linkedData.append(data_name)
                        self.linkedName.append(evaluated_obj.name)
                    info = self.export_object(object_instance, geometryFolder)
                    #d["shape"].extend(info["shapes"]) #add object parts to scene objects
                    #d["shape"].append(info["group"])
                    #print("export regular object")
                    self.objectData[data_name] = info["shapes"]
                    
                    #if info.notEmpty():
                    #    infoLst[evaluated_obj.name] = info.to_InstanceDictStr('geometry/')
                    #    GeometryLst.append(info.to_DictStr('geometry/'))
                            
            elif object_type == 'LIGHT':
                if evaluated_obj.data.type == 'SUN':
                    #self.lightsData.append(export_distant_light(evaluated_obj))
                    print("SUN OBJECT", evaluated_obj.data.type)
                elif evaluated_obj.data.type == 'POINT':
                    #self.lightsData.append(export_point_light(evaluated_obj))
                    print("POINT LIGHT OBJECT", evaluated_obj.data.type)
                elif evaluated_obj.data.type == 'SPOT':
                    #self.lightsData.append(export_spot_light(evaluated_obj))
                    print("SPOT LIGHT OBJECT", evaluated_obj.data.type)
                else:
                    print("LIGHT OBJECT", evaluated_obj.data.type)
            elif object_type == 'CAMERA':
                print ("export object: ", evaluated_obj.name, " skip camera")
            else:
                print ("Object: %s of type '%s' is not supported!" % (evaluated_obj.name_full, object_type), 'WARN')
        
        for name in self.groups:
            print("Linked data:",name)
            shapes = self.objectData[name]
            transform = shapes[0].get("transform").get("matrix").get("value")
            for dic in shapes:
                dic.pop('transform')
            refid = "group"+name
            group = {}
            group["type"] = "shapegroup"
            group["id"] = refid
            group["shape"] = shapes
            self.objectData[name] = group
            #create instance itself
            self.objectData[name+"_instance_base"] = self.exportInstance(refid, transform)
        
        d["shape"].extend(list(self.objectData.values()))
        print("Generate xml data...")
        #shapes = np.array_split(d["shape"], 2)
        chunk_size = 100000 #prevent recursion slowdown on big data
        data = '<scene version="2.0.0">\n'
        for i in range(0, len(d["shape"]), chunk_size):
            print("convert chunk: ", str(i))
            chunk_scene = {"version":"2.0.0"}
            chunk_scene["shape"] = d["shape"][i:i + chunk_size]
            data_str = dict2xml(chunk_scene["shape"], "shape", "")
            data+=data_str
            #print(data_str)
        data += "</scene>\n"
        #data = dict2xml(d, "scene", "")
        #self.materialData["emitter"].extend(list(self.areaEmitterData.values()))
        mat_data = dict2xml(self.materialData, "scene", "")
        return data, mat_data
