import maya.cmds as cmds
import math

def allign(vtx1, vtx2, local_y_flip=False):
    
    assert "vtx" in vtx1 and "vtx" in vtx2
    
    # Matching rotation of face normal
    obj_name = vtx1.split(".")[0]
    vec1 = cmds.polyNormalPerVertex(vtx1, query=True, xyz=True)[:3]
    vec2 = cmds.polyNormalPerVertex(vtx2, query=True, xyz=True)[:3]
    rotation_matrix = get_rotation_matrix(vec1, vec2)
    euler_radians = rotation_matrix_to_euler(rotation_matrix)    
    r_x, r_y, r_z = [math.degrees(i) for i in euler_radians]
    cmds.rotate(r_x, r_y, r_z, [obj_name])
    
    if local_y_flip:
        cmds.scale(1, -1, 1, [obj_name], os=True, r=True)
    
    # Matching face position
    v1_x, v1_y, v1_z = get_position(vtx1)
    v2_x, v2_y, v2_z = get_position(vtx2)
    cmds.move(v1_x, v1_y, v1_z, "{}.scalePivot".format(obj_name), "{}.rotatePivot".format(obj_name), rpr=True)
    cmds.move(v2_x, v2_y, v2_z, [obj_name], rpr=True, ws=True)

