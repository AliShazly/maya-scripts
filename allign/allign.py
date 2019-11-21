import maya.cmds as cmds
import math

def allign(face1, face2, local_y_flip=False):
    
    # Matching rotation of face normal
    obj_name = face1.split(".")[0]
    vec1 = format_polyinfo(cmds.polyInfo(face1, fn=True))
    vec2 = format_polyinfo(cmds.polyInfo(face2, fn=True))
    rotation_matrix = get_rotation_matrix(vec1, vec2)
    euler_radians = rotation_matrix_to_euler(rotation_matrix)    
    r_x, r_y, r_z = [math.degrees(i) for i in euler_radians]
    cmds.rotate(r_x, r_y, r_z, [obj_name])
    
    if local_y_flip:
        cmds.scale(1, -1, 1, [obj_name], os=True, r=True)
    
    # Matching face position
    f1_x, f1_y, f1_z = get_position(face1)
    f2_x, f2_y, f2_z = get_position(face2)
    cmds.move(f1_x, f1_y, f1_z, "{}.scalePivot".format(obj_name), "{}.rotatePivot".format(obj_name), rpr=True)
    cmds.move(f2_x, f2_y, f2_z, [obj_name], rpr=True, ws=True)
    
# Select first face
face1 = cmds.ls(selection=True)[0]
# Select target face
face2 = cmds.ls(selection=True)[0]
# Move
allign(face1, face2, local_y_flip=False)