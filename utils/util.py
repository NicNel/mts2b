import bpy
import os
import math
import pathlib
from pathlib import Path
import subprocess

def register_class(cls):
    try:
        #logger.debug("[appleseed] Registering class {0}...".format(cls))
        bpy.utils.register_class(cls)
    except Exception as e:
        print ("ERROR: Failed to register class {0}: {1}".format(cls, e))
        #logger.error("[appleseed] ERROR: Failed to register class {0}: {1}".format(cls, e))

def unregister_class(cls):
    try:
        #logger.debug("[appleseed] Unregistering class {0}...".format(cls))
        bpy.utils.unregister_class(cls)
    except Exception as e:
        print ("ERROR: Failed to unregister class {0}: {1}".format(cls, e))
        #logger.error("[appleseed] ERROR: Failed to unregister class {0}: {1}".format(cls, e))

def realpath(path):
    """Resolve a relative Blender path to a real filesystem path"""
    if path.startswith('//'):
        path = bpy.path.abspath(path)
    else:
        path = os.path.realpath(path)
    path = path.replace('\\', '/')
    path = os.path.realpath(path)
    return path
    
def switchpath(path):
    """Resolve a relative Blender path to a real filesystem path"""
    p = pathlib.PureWindowsPath(path)
    return p.as_posix()

def getFileName(file):
    #base = os.path.basename(file)
    #name = os.path.splitext(base)
    #return name[0]
    return Path(file).stem
    
def createFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder
    
def Lerp(a, b, t):
    return a-(a*t)+(b*t)

def InvLerp(a, b, t):
    return (t-a)/(b-a)
    
def matrixtostr(matrix):
    return ' %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f '%(matrix[0][0],matrix[0][1],matrix[0][2],matrix[0][3],matrix[1][0],matrix[1][1],matrix[1][2],matrix[1][3],matrix[2][0],matrix[2][1],matrix[2][2],matrix[2][3],matrix[3][0],matrix[3][1],matrix[3][2],matrix[3][3])

def vectortostr(vec):
    return '%f, %f, %f'%(vec[0],vec[1],vec[2])

def calcFovRAD(resx, resy, angle):
        if resx>=resy:
            ratio = resy / resx
        else:
            ratio = resx / resy
        angle_rad = angle
        fov = 2.0 * math.atan ( ratio * math.tan( angle_rad / 2.0 )) * 180.0 / math.pi 
        return fov
        
def calcFovDEG(resx, resy, angle):
    if resx>=resy:
        ratio = resy / resx
    else:
        ratio = resx / resy
    angle_deg = angle * 180.0 / math.pi 
    fov = 2.0 * math.atan ( ratio * math.tan( angle_deg / 2.0 ))* 180.0 / math.pi 
    return fov
    
def runCmd(cmd, stdout=None, cwd=None, env=None):
    stdoutInfo = ""
    if stdout is not None:
        stdoutInfo = " > {}".format(stdout.name)
    print(">>> {}{}".format(cmd, stdoutInfo))
    subprocess.call(cmd, shell=False, stdout=stdout, cwd=cwd, env=env)
    
IorPreset = [
                                              ("air", "air", "air"),
                                              ("vacuum", "vacuum", "vacuum"),
                                              ("bromine", "bromine", "bromine"),
                                              ("helium", "helium", "helium"),
                                              ("water ice", "water ice", "water ice"),
                                              ("hydrogen", "hydrogen", "hydrogen"),
                                              ("fused quartz", "fused quartz", "fused quartz"),
                                              ("pyrex", "pyrex", "pyrex"),
                                              ("carbon dioxide", "carbon dioxide", "carbon dioxide"),
                                              ("acrylic glass", "acrylic glass", "acrylic glass"),
                                              ("water", "water", "water"),
                                              ("polypropylene", "polypropylene", "polypropylene"),
                                              ("acetone", "acetone", "acetone"),
                                              ("bk7", "bk7", "bk7"),
                                              ("ethanol", "ethanol", "ethanol"),
                                              ("sodium chloride", "sodium chloride", "sodium chloride"),
                                              ("carbon tetrachloride", "carbon tetrachloride", "carbon tetrachloride"),
                                              ("amber", "amber", "amber"),
                                              ("glycerol", "glycerol", "glycerol"),
                                              ("pet", "pet", "pet"),
                                              ("benzene", "benzene", "benzene"),
                                              ("diamond", "diamond", "diamond"),
                                              ("silicone oil", "silicone oil", "silicone oil"),
                                              ("value", "value", "value")
                                              ]
MaterialPreset = [
                                              ("a-C", "a-C", "a-C"),
                                              ("Ag", "Ag", "Ag"),
                                              ("Al", "Al", "Al"),
                                              ("AlAs", "AlAs", "AlAs"),
                                              ("AlAs_palik", "AlAs_palik", "AlAs_palik"),
                                              ("AlSb", "AlSb", "AlSb"),
                                              ("AlSb_palik", "AlSb_palik", "AlSb_palik"),
                                              ("Au", "Au", "Au"),
                                              ("Be", "Be", "Be"),
                                              ("Be_palik", "Be_palik", "Be_palik"),
                                              ("Cr", "Cr", "Cr"),
                                              ("CsI", "CsI", "CsI"),
                                              ("CsI_palik", "CsI_palik", "CsI_palik"),
                                              ("Cu", "Cu", "Cu"),
                                              ("Cu_palik", "Cu_palik", "Cu_palik"),
                                              ("Cu2O", "Cu2O", "Cu2O"),
                                              ("Cu2O_palik", "Cu2O_palik", "Cu2O_palik"),
                                              ("CuO", "CuO", "CuO"),
                                              ("CuO_palik", "CuO_palik", "CuO_palik"),
                                              ("d-C", "d-C", "d-C"),
                                              ("d-C_palik", "d-C_palik", "d-C_palik"),
                                              ("Hg", "Hg", "Hg"),
                                              ("Hg_palik", "Hg_palik", "Hg_palik"),
                                              ("HgTe", "HgTe", "HgTe"),
                                              ("HgTe_palik", "HgTe_palik", "HgTe_palik"),
                                              ("Ir", "Ir", "Ir"),
                                              ("Ir_palik", "Ir_palik", "Ir_palik"),
                                              ("K", "K", "K"),
                                              ("K_palik", "K_palik", "K_palik"),
                                              ("Li", "Li", "Li"),
                                              ("Li_palik", "Li_palik", "Li_palik"),
                                              ("MgO", "MgO", "MgO"),
                                              ("MgO_palik", "MgO_palik", "MgO_palik"),
                                              ("Mo", "Mo", "Mo"),
                                              ("Mo_palik", "Mo_palik", "Mo_palik"),
                                              ("Na_palik", "Na_palik", "Na_palik"),
                                              ("Nb", "Nb", "Nb"),
                                              ("Nb_palik", "Nb_palik", "Nb_palik"),
                                              ("Ni_palik", "Ni_palik", "Nickel"),
                                              ("Rh", "Rh", "Rh"),
                                              ("Rh_palik", "Rh_palik", "Rh_palik"),
                                              ("Se", "Se", "Se"),
                                              ("Se_palik", "Se_palik", "Se_palik"),
                                              ("SiC", "SiC", "SiC"),
                                              ("SiC_palik", "SiC_palik", "SiC_palik"),
                                              ("SnTe", "SnTe", "SnTe"),
                                              ("SnTe_palik", "SnTe_palik", "SnTe_palik"),
                                              ("Ta", "Ta", "Ta"),
                                              ("Ta_palik", "Ta_palik", "Ta_palik"),
                                              ("Te", "Te", "Te"),
                                              ("Te_palik", "Te_palik", "Te_palik"),
                                              ("ThF4", "ThF4", "ThF4"),
                                              ("ThF4_palik", "ThF4_palik", "ThF4_palik"),
                                              ("TiC", "TiC", "TiC"),
                                              ("TiC_palik", "TiC_palik", "TiC_palik"),
                                              ("TiN", "TiN", "TiN"),
                                              ("TiN_palik", "TiN_palik", "TiN_palik"),
                                              ("TiO2", "TiO2", "TiO2"),
                                              ("TiO2_palik", "TiO2_palik", "TiO2_palik"),
                                              ("VC", "VC", "VC"),
                                              ("VC_palik", "VC_palik", "VC_palik"),
                                              ("V_palik", "V_palik", "Vanadium"),
                                              ("VN", "VN", "VN"),
                                              ("VN_palik", "VN_palik", "Vanadium nitride"),
                                              ("W", "W", "Tungsten"),
                                              ("none", "none", "mirror")
                                              ]