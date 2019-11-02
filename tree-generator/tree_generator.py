from __future__ import print_function, division

import maya.cmds as cmds
import random

def create_trunk():
    obj_name, _ = cmds.polyCylinder(h=8, sx=6, sy=5, sc=1)   
    flare, flare_handle = random_flare()
    cmds.select(obj_name, r=True)
    bend, bend_handle = random_bend()
    cmds.move(0, -4, 0, bend_handle, r=True)
    cmds.DeleteAllHistory()
    return obj_name

def create_blob(size=2):
    obj_name, _ = cmds.polyPlatonicSolid(st=1, r=size)
    cmds.polySmooth(mth=1) # Linear smooth
    randomize_faces(move_bias = [2,1,3])
    return obj_name
    
def create_branches(obj_name, num_branches=4, max_iterations=4, length_range=(0.5, 1.5), height_range=(0.2, 1.5)):
    num_faces = cmds.polyEvaluate(obj_name, f=True)
    branch_faces = []
    while len(branch_faces) < num_branches:
        rand_face = random.randint(0, num_faces)
        cmds.select("{}.f[{}]".format(obj_name, rand_face))
        face_verts = format_polyinfo(cmds.polyInfo(fv=True))
        # Only accepting quads and faces above 0 on the Y axis
        if len(face_verts) > 3 and get_position()[1] > 0 and rand_face not in branch_faces:
            branch_faces.append(rand_face)
    branch_ends = []
    for face in branch_faces:
        cmds.select("{}.f[{}]".format(obj_name, face))
        cmds.polyExtrudeFacet()
        cmds.scale(0.7, 0.7, 0.7, cs=True)
        iterations = random.randint(1, max_iterations)
        for i in range(iterations):
            ty = random.uniform(*height_range)
            ltz = random.uniform(*length_range)
            cmds.polyExtrudeFacet(ltz=ltz, ty=ty)
            cmds.scale(0.6, 0.6, 0.6, cs=True)
        branch_ends.append(cmds.ls(selection=True)[0])
    return branch_ends

def create_leaves(dest_obj, dest_faces, size_range=(2,3)):
    for face in dest_faces:
        cmds.select(face, r=True)
        pos = get_position()
        if pos[1] < 2:
            continue
        size = random.uniform(*size_range)
        blob = create_blob(size=size)
        cmds.select(blob, r=True)
        cmds.move(*pos, ws=True)

def grow_trunk(obj_name, length=3):
    num_faces = cmds.polyEvaluate(obj_name, f=True)
    top_faces = []
    for i in range(num_faces):
        cmds.select("{}.f[{}]".format(obj_name, i))
        if cmds.polyEvaluate(tc=True) == 1 and get_position()[1] > 0:
            top_faces.append(i)
    cmds.select(cl=True)
    for id in top_faces:
        cmds.select("{}.f[{}]".format(obj_name, id), add=True)
    cmds.polyExtrudeFacet(ltz=length)
    cmds.scale(0.6, 0.6, 0.6, cs=True)
    return top_faces

def generate_tree():
    trunk = create_trunk()
    branch_ends = create_branches(trunk)
    top_faces = grow_trunk(trunk)
    create_leaves(trunk, branch_ends)
    # Creating a bigger leaf blob for the top of the trunk
    create_leaves(trunk, ["{}.f[{}]".format(trunk, top_faces[0])], size_range=(3,5))

generate_tree()