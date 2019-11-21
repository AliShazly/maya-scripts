import maya.cmds as cmds
import random

def random_bend(thresh=20):
    curvature, rotation = random.uniform(-thresh,thresh), random.uniform(0,360)
    bend, bend_handle = cmds.nonLinear(type="bend", curvature=curvature, highBound=5)
    cmds.rotate(0, rotation, 0, bend_handle, fo=True, os=True, r=True)
    return bend, bend_handle

def random_flare(curve_range=(-0.5, 0)):
    curve_value = random.uniform(*curve_range)
    f_v = [random.uniform(0.6, 1.6) for i in range(2)]
    return cmds.nonLinear(type="flare",
        curve=curve_value,
        startFlareX=f_v[0],
        endFlareX=f_v[1])

def randomize_faces(obj_name=None, move_thresh=0.1, rotate_thresh=1, move_bias=None, rotate_bias=None, component_space=False):
    
    if obj_name is None:
        obj_name = cmds.ls(selection=True)[0]
    
    # Loop through all faces and randomly manipulate
    num_faces = cmds.polyEvaluate(obj_name, f=True)
    for num in range(num_faces):
        cmds.select("{}.f[{}]".format(obj_name, num))
        normal = format_polyinfo(cmds.polyInfo(fn=True))
        if normal[1] not in (-1, 1): # Not manipulating straight faces
           rotate_coords = [random.uniform(-rotate_thresh, rotate_thresh) for i in range(3)]
           move_coords = [random.uniform(-move_thresh, move_thresh) for i in range(3)]
           if rotate_bias:
               rotate_coords = [c * b for c, b in zip(rotate_coords, rotate_bias)]
           if move_bias:
               move_coords = [c * b for c, b in zip(move_coords, move_bias)]
           if component_space:
               cmds.rotate(*rotate_coords, r=True, cs=True)
               cmds.move(*move_coords, r=True, cs=True)
           else:
               cmds.rotate(*rotate_coords, r=True)
               cmds.move(*move_coords, r=True)

    # Harden edges
    cmds.select(obj_name, r=True)
    cmds.polySoftEdge(angle=0)
