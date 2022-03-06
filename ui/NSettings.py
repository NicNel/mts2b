import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils

from nodeitems_utils import (
    NodeCategory,
    NodeItem,
    NodeItemCustom,
)
from ..utils import util

class MTS2NodeTree(bpy.types.NodeTree):
    """ This operator is only visible when pbrt4 is the selected render engine"""
    bl_idname = 'MTS2NodeTree'
    bl_label = "MTS2 Node Tree"
    bl_icon = 'MATERIAL'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MTS2'

class MTS2NodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        #Do not add the MTS2 shader category if MTS2 is not selected as renderer
        engine = context.scene.render.engine
        if engine != 'MTS2':
            return False
        else:
            b = False
            if context.space_data.tree_type == 'ShaderNodeTree': b = True
            return b

# all categories in a list
node_categories = [
    # identifier, label, items list
    #MyNodeCategory("SOMENODES", "PBRT", items=[
    MTS2NodeCategory("MTS2_SHADER", "MTS2 Shaders", items=[
        NodeItem("mts2Diffuse"),
        NodeItem("mts2DiffTrans"),
        NodeItem("mts2Plastic"),
        NodeItem("mts2Dielectric"),
        NodeItem("mts2Conductor"),
        NodeItem("mts2Blend"),
        NodeItem("mts2Twosided"),
        NodeItem("mts2Bumpmap"),
        NodeItem("mts2Normalmap"),
        NodeItem("mts2Mask"),
        NodeItem("mts2Null")
        ]),
    MTS2NodeCategory("MTS2_MEDIUM", "MTS2 Mediums", items=[
        #NodeItem("pbrtv4CloudVolume")
        ]),
    MTS2NodeCategory("MTS2_TEXTURES", "MTS2 Textures", items=[
        NodeItem("mts2Bitmap"),
        NodeItem("mts2CheckerText"),
        NodeItem("mts2MixText"),
        NodeItem("mts2Fresnel"),
        NodeItem("mts2ScaleText")
        ]),
    MTS2NodeCategory("MTS2_UTILS", "MTS2 Utils", items=[
        NodeItem("mts2Transform"),
        NodeItem("mts2AreaEmitter")
        ]),
    ]

class MTS2TreeNode:
    bl_icon = 'MATERIAL'
    bl_idname = 'mts2Node'
    
    isMts2TreeNode = True
    
    def setId(self, name, id):
        #matName::nodeType::nodeTreeUniqueId
        #self.name ="{}::{}::{}".format(name, self.bl_idname, id)
        self.label ="{}::{}::{}".format(name, self.bl_idname, id)
    
    def getId(self):
        tmp = self.label.split("::")
        id = tmp[-1]
        return int(id)
    
    #List - already exported nodes Data - nodes data to write
    def Backprop(self, List, Data, Tag = None):
        if self.label not in List:
            List.append(self.label)
            return self.to_dict(List, Data) #self.to_string(List, Data)
        else:
            return self
            
    def to_dict(self, List, data):
        return self
    def to_string(self, List, data):
        return self
    
    @classmethod
    def poll(cls, ntree):
        b = False
        # Make your node appear in different node trees by adding their bl_idname type here.
        if ntree.bl_idname == 'ShaderNodeTree': b = True
        return b
        
    #prev version
    def constructTName(self, matName, tName):
        return "{}::{}::{}".format(matName, "Texture", tName)
    def constructMName(self, matName, tName):
        return "{}::{}::{}".format(matName, "Material", tName)
    
class mts2Null(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Null'
    bl_label = 'null'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
        
    def to_dict(self, list, data):
        name = self.label
        
        bsdf_dict = {}
        bsdf_dict["type"] = "null"
        bsdf_dict["id"] = name
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Diffuse(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Diffuse'
    bl_label = 'diffuse'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        diffuse_reflectance = self.inputs.new('NodeSocketColor', "Color Texture")
        diffuse_reflectance.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
        
    def to_dict(self, list, data):
        name = self.label
        
        color = self.inputs[0]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "diffuse"
        bsdf_dict["id"] = name
        bsdf_dict["rgb"] = []
        bsdf_dict["ref"] = []
         
        #reflectance
        if not(color.is_linked):
            c = color.default_value
            bsdf_dict["rgb"].append({"name":"reflectance", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = color.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"id":text_id, "name":"reflectance"})
        
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2DiffTrans(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2DiffTrans'
    bl_label = 'transmitter'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        diffuse_transmittance = self.inputs.new('NodeSocketColor', "Color Texture")
        diffuse_transmittance.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
        
    def to_dict(self, list, data):
        name = self.label
        
        color = self.inputs[0]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "difftrans"
        bsdf_dict["id"] = name
        bsdf_dict["rgb"] = []
        bsdf_dict["ref"] = []
         
        #transmittance
        if not(color.is_linked):
            c = color.default_value
            bsdf_dict["rgb"].append({"name":"transmittance", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = color.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"id":text_id, "name":"transmittance"})
        
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Plastic(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Plastic'
    bl_label = 'plastic'
    bl_icon = 'MATERIAL'

    Nonlinear: bpy.props.BoolProperty(default=False)
    Sample_visible: bpy.props.BoolProperty(default=True)
    
    Int_ior_preset: bpy.props.EnumProperty(name="IorPreset",
                                              description="",
                                              items=util.IorPreset, default = "polypropylene")
    Int_ior : bpy.props.FloatProperty(default=1.49, min=1.0, max=999.0)
    Ext_ior_preset: bpy.props.EnumProperty(name="IorPreset",
                                              description="",
                                              items=util.IorPreset)
    Ext_ior : bpy.props.FloatProperty(default=1.00028, min=1.0, max=999.0)
    Distribution: bpy.props.EnumProperty(name="Distribution",
                                              description="Distribution",
                                              items=[
                                              ("beckmann", "beckmann", "beckmann"),
                                              ("ggx", "ggx", "ggx")
                                              ],
                                              default='beckmann')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        diffuse_reflectance = self.inputs.new('NodeSocketColor', "Color Texture")
        diffuse_reflectance.default_value = [0.8, 0.8, 0.8, 1.0]
        
        specular_reflectance = self.inputs.new('NodeSocketColor', "Specular Texture")
        specular_reflectance.default_value = [1.0, 1.0, 1.0, 1.0]
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "Roughness Texture")
        RoughnessTexture_node.default_value = 0.0
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Sample_visible",text = 'sample visible')
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "Int_ior_preset",text = 'Int_ior preset')
        if self.Int_ior_preset == "value":
            layout.prop(self, "Int_ior",text = 'int_ior')
        layout.prop(self, "Ext_ior_preset",text = 'Ext_ior preset')
        if self.Ext_ior_preset == "value":
            layout.prop(self, "Ext_ior",text = 'ext_ior')
        layout.prop(self, "Distribution",text = 'Distribution type')
        
        layout.prop(self, "Nonlinear",text = 'nonlinear')
        
    def draw_label(self):
        return self.bl_label
        
    def to_dict(self, list, data):
        name = self.label
        
        color = self.inputs[0]
        spec = self.inputs[1]
        rough = self.inputs[2]
        
        isRough = False if not(rough.is_linked) and rough.default_value == 0 else True
        
        bsdf_dict = {}
        bsdf_dict["type"] = "roughplastic" if isRough else "plastic"
        bsdf_dict["id"] = name
        bsdf_dict["float"] = []
        bsdf_dict["string"] = []
        bsdf_dict["rgb"] = []
        bsdf_dict["boolean"] = []
        bsdf_dict["ref"] = []
         
        bsdf_dict["boolean"].append({"name":"nonlinear", "value":self.Nonlinear})
        #export ior
        if self.Int_ior_preset == "value":
            bsdf_dict["float"].append({"name":"int_ior", "value":self.Int_ior})
        else:
            bsdf_dict["string"].append({"name":"int_ior", "value":self.Int_ior_preset})
        if self.Ext_ior_preset == "value":
            bsdf_dict["float"].append({"name":"ext_ior", "value":self.Ext_ior})
        else:
            bsdf_dict["string"].append({"name":"ext_ior", "value":self.Ext_ior_preset})
        #export colors
        #reflectance
        if not(color.is_linked):
            c = color.default_value
            bsdf_dict["rgb"].append({"name":"diffuse_reflectance", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = color.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"id":text_id, "name":"diffuse_reflectance"})
        #specular
        if not(spec.is_linked):
            c = spec.default_value
            bsdf_dict["rgb"].append({"name":"specular_reflectance", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = spec.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"id":text_id, "name":"specular_reflectance"})
        #export roughness
        if isRough:
            if not(rough.is_linked):
                c = rough.default_value
                bsdf_dict["float"].append({"name":"alpha", "value":c})
            else:
                node_link = roughness.links[0]
                curNode =  node_link.from_node
                nd = curNode.Backprop(list, data)
                #res+='  "texture roughness" ["{}"]\n'.format(nd.label)
            bsdf_dict["boolean"].append({"name":"sample_visible", "value":self.Sample_visible})
            
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Dielectric(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Dielectric'
    bl_label = 'dielectric'
    bl_icon = 'MATERIAL'

    Sample_visible: bpy.props.BoolProperty(default=True)
    
    Int_ior_preset: bpy.props.EnumProperty(name="IorPreset",
                                              description="",
                                              items=util.IorPreset, default = "polypropylene")
    Int_ior : bpy.props.FloatProperty(default=1.49, min=1.0, max=999.0)
    Ext_ior_preset: bpy.props.EnumProperty(name="IorPreset",
                                              description="",
                                              items=util.IorPreset)
    Ext_ior : bpy.props.FloatProperty(default=1.00028, min=1.0, max=999.0)
    Distribution: bpy.props.EnumProperty(name="Distribution",
                                              description="Distribution",
                                              items=[
                                              ("beckmann", "beckmann", "beckmann"),
                                              ("ggx", "ggx", "ggx")
                                              ],
                                              default='beckmann')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "Roughness Texture")
        RoughnessTexture_node.default_value = 0.0
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Sample_visible",text = 'sample visible')
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "Int_ior_preset",text = 'Int_ior preset')
        if self.Int_ior_preset == "value":
            layout.prop(self, "Int_ior",text = 'int_ior')
        layout.prop(self, "Ext_ior_preset",text = 'Ext_ior preset')
        if self.Ext_ior_preset == "value":
            layout.prop(self, "Ext_ior",text = 'ext_ior')
        layout.prop(self, "Distribution",text = 'Distribution type')
        
    def draw_label(self):
        return self.bl_label
        
    def to_dict(self, list, data):
        name = self.label
        
        rough = self.inputs[0]
        
        isRough = False if not(rough.is_linked) and rough.default_value == 0 else True
        
        bsdf_dict = {}
        bsdf_dict["type"] = "roughdielectric" if isRough else "dielectric"
        bsdf_dict["id"] = name
        bsdf_dict["float"] = []
        bsdf_dict["string"] = []
        bsdf_dict["rgb"] = []
        bsdf_dict["boolean"] = []
        bsdf_dict["ref"] = []
         
        #export ior
        if self.Int_ior_preset == "value":
            bsdf_dict["float"].append({"name":"int_ior", "value":self.Int_ior})
        else:
            bsdf_dict["string"].append({"name":"int_ior", "value":self.Int_ior_preset})
        if self.Ext_ior_preset == "value":
            bsdf_dict["float"].append({"name":"ext_ior", "value":self.Ext_ior})
        else:
            bsdf_dict["string"].append({"name":"ext_ior", "value":self.Ext_ior_preset})
        #export colors
        #export roughness
        if isRough:
            if not(rough.is_linked):
                c = rough.default_value
                bsdf_dict["float"].append({"name":"alpha", "value":c})
            else:
                node_link = rough.links[0]
                curNode =  node_link.from_node
                nd = curNode.Backprop(list, data)
                text_id = nd.label
                bsdf_dict["ref"].append({"id":text_id, "name":"alpha"})
            bsdf_dict["boolean"].append({"name":"sample_visible", "value":self.Sample_visible})
            
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Conductor(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Conductor'
    bl_label = 'conductor'
    bl_icon = 'MATERIAL'

    Sample_visible: bpy.props.BoolProperty(default=True)
    
    Material_preset: bpy.props.EnumProperty(name="Material_preset",
                                              description="",
                                              items=util.MaterialPreset)
    
    Distribution: bpy.props.EnumProperty(name="Distribution",
                                              description="Distribution",
                                              items=[
                                              ("beckmann", "beckmann", "beckmann"),
                                              ("ggx", "ggx", "ggx")
                                              ],
                                              default='beckmann')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "Roughness Texture")
        RoughnessTexture_node.default_value = 0.0
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Sample_visible",text = 'sample visible')
        layout.prop(self, "Material_preset",text = 'Material preset')
        layout.prop(self, "Distribution",text = 'Distribution type')
        
    def draw_label(self):
        return self.bl_label
        
    def to_dict(self, list, data):
        name = self.label
        
        rough = self.inputs[0]
        
        isRough = False if not(rough.is_linked) and rough.default_value == 0 else True
        
        bsdf_dict = {}
        bsdf_dict["type"] = "roughconductor" if isRough else "conductor"
        bsdf_dict["id"] = name
        bsdf_dict["float"] = []
        bsdf_dict["string"] = []
        bsdf_dict["rgb"] = []
        bsdf_dict["boolean"] = []
        bsdf_dict["ref"] = []
         
        #export ior
        bsdf_dict["string"].append({"name":"material", "value":self.Material_preset})
        
        #export roughness
        if isRough:
            if not(rough.is_linked):
                c = rough.default_value
                bsdf_dict["float"].append({"name":"alpha", "value":c})
            else:
                node_link = rough.links[0]
                curNode =  node_link.from_node
                nd = curNode.Backprop(list, data)
                text_id = nd.label
                bsdf_dict["ref"].append({"id":text_id, "name":"alpha"})
            bsdf_dict["boolean"].append({"name":"sample_visible", "value":self.Sample_visible})
            
        data["bsdf"].append(bsdf_dict)
        return self
                    
class mts2Blend(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Blend'
    bl_label = 'blendbsdf'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        MixAmount_node = self.inputs.new('NodeSocketFloat', "Mix amount")
        MixAmount_node.default_value = 0.5
        Mat1_node = self.inputs.new('NodeSocketShader', "Mat1")
        Mat2_node = self.inputs.new('NodeSocketShader', "Mat2")
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        amount = self.inputs[0]
        mat1 = self.inputs[1]
        mat2 = self.inputs[2]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "blendbsdf"
        bsdf_dict["id"] = name
        bsdf_dict["rgb"] = []
        bsdf_dict["ref"] = []
        bsdf_dict["float"] = []
        bsdf_dict["bsdf"] = []
         
        #reflectance
        if not(amount.is_linked):
            c = amount.default_value
            bsdf_dict["float"].append({"name":"weight", "value":c})
        else:
            node_link = amount.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"id":text_id, "name":"weight"})
            
        #mat1
        if not(mat1.is_linked):
            mat1FinalName = "None"
        else:
            node_link = mat1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat1FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat1FinalName})
        #mat2
        if not(mat2.is_linked):
            mat2FinalName = "None"
        else:
            node_link = mat2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat2FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat2FinalName})
        
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Twosided(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Twosided'
    bl_label = 'twosided'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        Mat1_node = self.inputs.new('NodeSocketShader', "Mat1")
        Mat2_node = self.inputs.new('NodeSocketShader', "Mat2")
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        mat1 = self.inputs[0]
        mat2 = self.inputs[1]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "twosided"
        bsdf_dict["id"] = name
        bsdf_dict["ref"] = []
         
        #mat1
        if not(mat1.is_linked):
            mat1FinalName = "None"
        else:
            node_link = mat1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat1FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat1FinalName})
        #mat2
        if not(mat2.is_linked):
            mat2FinalName = "None"
        else:
            node_link = mat2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat2FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat2FinalName})
        
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Bumpmap(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Bumpmap'
    bl_label = 'bumpmap'
    bl_icon = 'MATERIAL'
    
    Scale : bpy.props.FloatProperty(default=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        Mat1_node = self.inputs.new('NodeSocketShader', "bsdf")
        diffuse_reflectance = self.inputs.new('NodeSocketColor', "texture")
        diffuse_reflectance.hide_value = True
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Scale",text = 'scale')
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        mat = self.inputs[0]
        text = self.inputs[1]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "bumpmap"
        bsdf_dict["id"] = name
        bsdf_dict["float"] = []
        bsdf_dict["bsdf"] = []
        bsdf_dict["ref"] = []
        
        bsdf_dict["float"].append({"name":"scale", "value":self.Scale})
         
        #text
        if not(text.is_linked):
            pass
        else:
            node_link = text.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"id":text_id})
            
        #mat
        if not(mat.is_linked):
            mat1FinalName = "None"
        else:
            node_link = mat.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat1FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat1FinalName})
        
        data["bsdf"].append(bsdf_dict)
        return self

class mts2Normalmap(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Normalmap'
    bl_label = 'normalmap'
    bl_icon = 'MATERIAL'
    
    Scale : bpy.props.FloatProperty(default=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        Mat1_node = self.inputs.new('NodeSocketShader', "bsdf")
        diffuse_reflectance = self.inputs.new('NodeSocketColor', "texture")
        diffuse_reflectance.hide_value = True
        
    def draw_buttons(self, context, layout):
        #pass
        layout.prop(self, "Scale",text = 'scale')
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        mat = self.inputs[0]
        text = self.inputs[1]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "normalmap"
        bsdf_dict["id"] = name
        bsdf_dict["float"] = []
        bsdf_dict["bsdf"] = []
        bsdf_dict["ref"] = []
        
        bsdf_dict["float"].append({"name":"scale", "value":self.Scale})
         
        #text
        if not(text.is_linked):
            pass
        else:
            node_link = text.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"name":"normalmap","id":text_id})
            
        #mat
        if not(mat.is_linked):
            mat1FinalName = "None"
        else:
            node_link = mat.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat1FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat1FinalName})
        
        data["bsdf"].append(bsdf_dict)
        return self
        
class mts2Mask(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Mask'
    bl_label = 'mask'
    bl_icon = 'MATERIAL'
    
    #Scale : bpy.props.FloatProperty(default=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        Mat1_node = self.inputs.new('NodeSocketShader', "bsdf")
        diffuse_reflectance = self.inputs.new('NodeSocketColor', "texture")
        diffuse_reflectance.hide_value = True
        
    def draw_buttons(self, context, layout):
        pass
        #layout.prop(self, "Scale",text = 'scale')
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        mat = self.inputs[0]
        text = self.inputs[1]
        
        bsdf_dict = {}
        bsdf_dict["type"] = "mask"
        bsdf_dict["id"] = name
        bsdf_dict["float"] = []
        bsdf_dict["bsdf"] = []
        bsdf_dict["ref"] = []
        
        #bsdf_dict["float"].append({"name":"scale", "value":self.Scale})
         
        #text
        if not(text.is_linked):
            pass
        else:
            node_link = text.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            bsdf_dict["ref"].append({"name":"opacity","id":text_id})
            
        #mat
        if not(mat.is_linked):
            mat1FinalName = "None"
        else:
            node_link = mat.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat1FinalName = nd.label
            bsdf_dict["ref"].append({"id":mat1FinalName})
        
        data["bsdf"].append(bsdf_dict)
        return self
          
class mts2Bitmap(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Bitmap'
    bl_label = 'bitmap'
    bl_icon = 'TEXTURE'
    
    def update_image(self, context):
        pass
    def update_type(self, context):
        #util.ShowMessageBox("This is a message", "This is a custom title", 'ERROR')
        if not self.Raw:
            self.outputs[0].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
    
    image: bpy.props.PointerProperty(name="Image", type=bpy.types.Image, update=update_image)
    
    show_thumbnail: bpy.props.BoolProperty(name="", default=True, description="Show thumbnail")
    Raw: bpy.props.BoolProperty(name="", default=False, description="Is Raw", update=update_type)
    FilterType: bpy.props.EnumProperty(name="FilterType",
                                          description="Texture filter type",
                                          items=[('bilinear', "bilinear", "bilinear filter"),
                                                 ('nearest', "nearest", "nearest filter")],
                                          default='bilinear')
    WrapMode: bpy.props.EnumProperty(name="WrapMode",
                                          description="Wrap Mode",
                                          items=[('repeat', "repeat", "repeat"),
                                                 ('mirror', "mirror", "mirror"),
                                                 ('clamp', "clamp", "clamp")],
                                          default='repeat')

    def init(self, context):
        self.outputs.new('NodeSocketColor', "bitmap")
        Mapping_node = self.inputs.new('NodeSocketVector', "Mapping")
        Mapping_node.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "show_thumbnail", text = 'Show preview')
        
        if self.show_thumbnail:
            layout.template_ID_preview(self, "image", open="image.open")
        else:
            layout.template_ID(self, "image", open="image.open")
        
        layout.prop(self, "Raw", text = 'Is Raw')
        layout.prop(self, "FilterType", text = 'Filter type')
        layout.prop(self, "WrapMode", text = 'Wrap mode')
        
    def draw_label(self):
        return self.bl_label
    
    def scaleNormalMap(self, scale):
        baseTexture = util.switchpath(util.realpath(self.image.filepath))
        baseName = util.getFileName(baseTexture)
        baseName = util.replaceExtension(baseName, "png")
        textureFolder =os.path.join(bpy.context.scene.pbrtv4.pbrt_project_dir, "textures")
        converted_file = os.path.join(textureFolder, baseName)
        converted_file = util.switchpath(converted_file)
        itoolExecPath = util.switchpath(bpy.context.scene.pbrtv4.pbrt_bin_dir)+'/'+'imgtool.exe'
        cmd = [ itoolExecPath, "scalenormalmap", baseTexture, "--scale", str(scale), "--outfile", converted_file]
        #print(cmd)
        util.runCmd(cmd)
        return converted_file
    
    def getFileName(self):
        if self.isNormal:
            name = self.scaleNormalMap(self.ScaleValue)
            return util.switchpath(name)
        else:
            util.switchpath(util.realpath(curNode.image.filepath))
    
    def to_dict(self, list, data):
        name = self.label
        
        uv = self.inputs[0]
        
        text_dict = {}
        text_dict["type"] = "bitmap"
        text_dict["id"] = name
        
        text_dict["float"] = []
        text_dict["string"] = []
        text_dict["rgb"] = []
        text_dict["boolean"] = []
        
        path = util.switchpath(util.realpath(self.image.filepath))
        text_dict["string"].append({"name":"filename", "value":path})
        text_dict["string"].append({"name":"filter_type", "value":self.FilterType})
        text_dict["string"].append({"name":"wrap_mode", "value":self.WrapMode})
        text_dict["boolean"].append({"name":"raw", "value":self.Raw})
        
        uv = self.inputs[0]
        if uv.is_linked:
            node_link = uv.links[0]
            curNode =  node_link.from_node
            uv=curNode.to_dict(list, data)
            text_dict["transform"] = uv
        
        data["texture"].append(text_dict)
        return self

class mts2ScaleText(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2ScaleText'
    bl_label = 'scale'
    bl_icon = 'TEXTURE'
    
    Scale : bpy.props.FloatProperty(default=1)
   
    def init(self, context):
        self.outputs.new('NodeSocketColor', "scale")
        text = self.inputs.new('NodeSocketColor', "Texture")
        text.default_value = [0.8, 0.8, 0.8, 1.0]

    def draw_buttons(self, context, layout):
        layout.prop(self, "Scale",text = 'scale')
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        text = self.inputs[0]
        
        text_dict = {}
        text_dict["type"] = "scale"
        text_dict["id"] = name
        
        text_dict["float"] = []
        text_dict["ref"] = []
        text_dict["rgb"] = []
        
        text_dict["float"].append({"name":"scale", "value":self.Scale})
        
        #transmittance
        if not(text.is_linked):
            c = text.default_value
            text_dict["rgb"].append({"name":"texture", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"texture"})
        
        data["texture"].append(text_dict)
        return self
        
class mts2MixText(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2MixText'
    bl_label = 'mix'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.outputs.new('NodeSocketColor', "Mix")
        
        MixAmount_node = self.inputs.new('NodeSocketFloat', "Mix amount")
        MixAmount_node.default_value = 0.5
        text1_node = self.inputs.new('NodeSocketColor', "color0")
        text1_node.default_value = [0.8, 0.8, 0.8, 1.0]
        text2_node = self.inputs.new('NodeSocketColor', "color1")
        text2_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        amount = self.inputs[0]
        text1 = self.inputs[1]
        text2 = self.inputs[2]
        
        text_dict = {}
        text_dict["type"] = "mix"
        text_dict["id"] = name
        text_dict["rgb"] = []
        text_dict["ref"] = []
        text_dict["float"] = []
         
        #reflectance
        if not(amount.is_linked):
            c = amount.default_value
            text_dict["float"].append({"name":"weight", "value":c})
        else:
            node_link = amount.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"weight"})
            
        #color0
        if not(text1.is_linked):
            c = text1.default_value
            text_dict["rgb"].append({"name":"color0", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"color0"})
        #color1
        if not(text2.is_linked):
            c = text2.default_value
            text_dict["rgb"].append({"name":"color1", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"color1"})
        
        data["texture"].append(text_dict)
        return self

class mts2Fresnel(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Fresnel'
    bl_label = 'fresnel'
    bl_icon = 'TEXTURE'
    
    IOR : bpy.props.FloatProperty(default=1.5)

    def init(self, context):
        self.outputs.new('NodeSocketColor', "fresnel")
        
        text1_node = self.inputs.new('NodeSocketColor', "color0")
        text1_node.default_value = [0.0, 0.0, 0.0, 1.0]
        text2_node = self.inputs.new('NodeSocketColor', "color1")
        text2_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "IOR",text = 'ior')
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        text1 = self.inputs[0]
        text2 = self.inputs[1]
        
        text_dict = {}
        text_dict["type"] = "fresnel"
        text_dict["id"] = name
        text_dict["rgb"] = []
        text_dict["ref"] = []
        text_dict["float"] = []
        
        text_dict["float"].append({"name":"ior", "value":self.IOR})
        
        #color0
        if not(text1.is_linked):
            c = text1.default_value
            text_dict["rgb"].append({"name":"color0", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"color0"})
        #color1
        if not(text2.is_linked):
            c = text2.default_value
            text_dict["rgb"].append({"name":"color1", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"color1"})
        
        data["texture"].append(text_dict)
        return self        

class mts2CheckerText(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2CheckerText'
    bl_label = 'checkerboard'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.outputs.new('NodeSocketColor', "checkerboard")
        text1_node = self.inputs.new('NodeSocketColor', "color0")
        text1_node.default_value = [0.8, 0.8, 0.8, 1.0]
        text2_node = self.inputs.new('NodeSocketColor', "color1")
        text2_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        Mapping_node = self.inputs.new('NodeSocketVector', "transform")
        Mapping_node.hide_value = True
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        text1 = self.inputs[0]
        text2 = self.inputs[1]
        uv = self.inputs[2]
        
        text_dict = {}
        text_dict["type"] = "checkerboard"
        text_dict["id"] = name
        text_dict["rgb"] = []
        text_dict["ref"] = []
        text_dict["float"] = []
        
        #color0
        if not(text1.is_linked):
            c = text1.default_value
            text_dict["rgb"].append({"name":"color0", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"color0"})
        #color1
        if not(text2.is_linked):
            c = text2.default_value
            text_dict["rgb"].append({"name":"color1", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            text_dict["ref"].append({"id":text_id, "name":"color1"})
        #uv transform
        if uv.is_linked:
            node_link = uv.links[0]
            curNode =  node_link.from_node
            uv=curNode.to_dict(list, data)
            text_dict["transform"] = uv
            
        data["texture"].append(text_dict)
        return self

class mts2Transform(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2Transform'
    bl_label = 'transform'
    bl_icon = 'TEXTURE'
    
    UValue : bpy.props.FloatProperty(default=1.0)
    VValue : bpy.props.FloatProperty(default=1.0)
    UDelta : bpy.props.FloatProperty(default=0.0)
    VDelta : bpy.props.FloatProperty(default=0.0)
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', "transform")

    def draw_buttons(self, context, layout):
        layout.prop(self, "UValue",text = 'U')
        layout.prop(self, "VValue",text = 'V')
        layout.separator()
        layout.prop(self, "UDelta",text = 'UD')
        layout.prop(self, "VDelta",text = 'VD')
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        uv_dict = {}
        uv_dict["name"] = "to_uv"
        uv_dict["scale"] = {"x":self.UValue, "y":self.VValue}
        return uv_dict
        
class mts2AreaEmitter(Node, MTS2TreeNode):
    '''A custom node'''
    bl_idname = 'mts2AreaEmitter'
    bl_label = 'area_emitter'
    bl_icon = 'MATERIAL'
    isMts2AreaEmitter = True

    def init(self, context):
        self.outputs.new('NodeSocketShader', "Output")
        Mat1_node = self.inputs.new('NodeSocketShader', "bsdf")
        
        diffuse_reflectance = self.inputs.new('NodeSocketColor', "Color Texture")
        diffuse_reflectance.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    def to_dict(self, list, data):
        name = self.label
        
        mat = self.inputs[0]
        
        #mat
        if not(mat.is_linked):
            mat1FinalName = "None"
        else:
            node_link = mat.links[0]
            curNode =  node_link.from_node
            curNode.label = name
            curNode.Backprop(list, data)
            #mat1FinalName = nd.label
            #bsdf_dict["ref"].append({"id":mat1FinalName})
        
        #data["bsdf"].append(bsdf_dict)
        return self
    
    def em_to_dict(self, list, data, id):
        #name = self.label
        text = self.inputs[1]
        
        em_dict = {}
        em_dict["rgb"] = []
        em_dict["spectrum"] = []
        em_dict["ref"] = []
        #radiance
        if not(text.is_linked):
            c = text.default_value
            #em_dict["rgb"].append({"name":"radiance", "value":""c})
            em_dict["rgb"].append({"name":"radiance", "value":"{}, {}, {}".format(c[0],c[1],c[2])})
        else:
            node_link = text.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            text_id = nd.label
            em_dict["ref"].append({"id":text_id, "name":"radiance"})
        
        return em_dict
        
def register():
    bpy.utils.register_class(mts2Plastic)
    bpy.utils.register_class(mts2Diffuse)
    bpy.utils.register_class(mts2DiffTrans)
    bpy.utils.register_class(mts2Dielectric)
    bpy.utils.register_class(mts2Conductor)
    bpy.utils.register_class(mts2Blend)
    bpy.utils.register_class(mts2Twosided)
    bpy.utils.register_class(mts2Bumpmap)
    bpy.utils.register_class(mts2Normalmap)
    bpy.utils.register_class(mts2Mask)
    bpy.utils.register_class(mts2Null)
    bpy.utils.register_class(mts2Bitmap)
    bpy.utils.register_class(mts2MixText)
    bpy.utils.register_class(mts2CheckerText)
    bpy.utils.register_class(mts2ScaleText)
    bpy.utils.register_class(mts2Transform)
    bpy.utils.register_class(mts2AreaEmitter)
    bpy.utils.register_class(mts2Fresnel)
    
    nodeitems_utils.register_node_categories("MTS2_NODES", node_categories)

def unregister():
    bpy.utils.unregister_class(mts2Plastic)
    bpy.utils.unregister_class(mts2Diffuse)
    bpy.utils.unregister_class(mts2Dielectric)
    bpy.utils.unregister_class(mts2Conductor)
    bpy.utils.unregister_class(mts2DiffTrans)
    bpy.utils.unregister_class(mts2Blend)
    bpy.utils.unregister_class(mts2Twosided)
    bpy.utils.unregister_class(mts2Bumpmap)
    bpy.utils.unregister_class(mts2Normalmap)
    bpy.utils.unregister_class(mts2Mask)
    bpy.utils.unregister_class(mts2Null)
    bpy.utils.unregister_class(mts2Bitmap)
    bpy.utils.unregister_class(mts2MixText)
    bpy.utils.unregister_class(mts2CheckerText)
    bpy.utils.unregister_class(mts2ScaleText)
    bpy.utils.unregister_class(mts2Transform)
    bpy.utils.unregister_class(mts2AreaEmitter)
    bpy.utils.unregister_class(mts2Fresnel)
    nodeitems_utils.unregister_node_categories("MTS2_NODES")