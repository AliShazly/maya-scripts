import maya.cmds as cmds
import string
import math

def allign_and_cache_weld_positions(vtx1, vtx2, reference_area=None, local_y_flip=False):
    
    faces1 = unpack_selection_items(cmds.polyListComponentConversion([vtx1], fv=True, tf=True))
    faces2 = unpack_selection_items(cmds.polyListComponentConversion([vtx2], fv=True, tf=True))
    border_verts1 = unpack_selection_items(cmds.polyListComponentConversion(faces1, ff=True, tv=True))
    border_verts2 = unpack_selection_items(cmds.polyListComponentConversion(faces2, ff=True, tv=True))
    border_verts1.remove(vtx1)
    border_verts2.remove(vtx2)
    allign(vtx1, vtx2, local_y_flip)
    obj1 = vtx1.split(".")[0]
    obj2 = vtx2.split(".")[0]
    if reference_area:
        cmds.select(faces2[0])
        face_points = unpack_selection_items(cmds.polyListComponentConversion(tv=True, bo=True))
        face_points = [get_position(i) for i in face_points]
        area = poly_area(face_points)
        area_sqrt1 = math.sqrt(reference_area)
        area_sqrt2 = math.sqrt(area)
        ratio = area_sqrt2 / area_sqrt1
        new_scale = (ratio,)*3
        cmds.select(obj1)
        cmds.scale(*new_scale, r=True)

    bv_cache1 = [get_position(i) for i in border_verts1]
    bv_cache2 = [get_position(i) for i in border_verts2]   
    faces_to_delete = faces1 + faces2
    return obj1, obj2, bv_cache1, bv_cache2, faces_to_delete

def weld_all(obj1, obj2, origin_positions, dest_positions, faces_to_delete):

    cmds.delete(*faces_to_delete)
    obj_name, _ = cmds.polyUnite(obj1, obj2)
    
    num_verts = cmds.polyEvaluate(obj_name, v=True)

    origin_positions = [[round(i, 5) for i in pos] for pos in origin_positions]
    dest_positions = [[round(i, 5) for i in pos] for pos in dest_positions]

    origin_verts = []
    dest_verts = []
    for i in range(num_verts):
        vert = "{}.vtx[{}]".format(obj_name, i)
        pos = get_position(vert)
        pos = [round(i, 5) for i in pos]        
        if pos in origin_positions:
            origin_verts.append(vert)
        elif pos in dest_positions:
            dest_verts.append(vert)
    
    origin_edge_ring = cmds.polyListComponentConversion(origin_verts, te=True, internal=True)
    dest_edge_ring = cmds.polyListComponentConversion(dest_verts, te=True, internal=True)
    cmds.select(origin_edge_ring, dest_edge_ring)
    cmds.polyBridgeEdge(divisions=0, twist=0, taper=1, curveType=0, smoothingAngle=30, direction=0, sourceDirection=0, targetDirection=0)
    
#vtx1 = cmds.ls(selection=True)[0]
#vtx2 = cmds.ls(selection=True)[0]
#reference_face_points = unpack_selection_items(cmds.polyListComponentConversion(cmds.ls(selection=True)[0], tv=True))
#reference_area = poly_area([get_position(i) for i in reference_face_points])
obj1, obj2, op, dp, ftd = allign_and_cache_weld_positions(vtx1, vtx2, reference_area, local_y_flip=True)
#weld_all(obj1, obj2, op, dp, ftd)