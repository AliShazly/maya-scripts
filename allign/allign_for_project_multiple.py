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
        area = cmds.polyEvaluate(faces2[0], wfa=True)[0]
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


def weld_all(obj_name, origin_positions_2D, dest_positions_2D, bridge_edges=False, merge_verts=False, merge_threshold=0.3):    

    if not merge_verts and not bridge_edges:
        raise Exception("No weld method chosen")
    
    num_verts = cmds.polyEvaluate(obj_name, v=True)

    origin_positions_2D = [[[round(i, 2) for i in pos] for pos in op] for op in origin_positions_2D]
    dest_positions_2D = [[[round(i, 2) for i in pos] for pos in dp] for dp in dest_positions_2D]

    origin_verts = []
    dest_verts = []
    for i in range(num_verts):
        vert = "{}.vtx[{}]".format(obj_name, i)
        pos = get_position(vert)
        pos = [round(i, 2) for i in pos]
        
        idx = 0  # Cant use enumerate because of zip
        for op, dp in zip(origin_positions_2D, dest_positions_2D):
            if pos in op:
                origin_verts.append((idx, vert))
            elif pos in dp:
                dest_verts.append((idx, vert))
            idx += 1
    
    origin_verts = [j for i, j in sorted(origin_verts, key=lambda x: x[0])]
    dest_verts = [j for i, j in sorted(dest_verts, key=lambda x:x[0])]
    chunk_length = len(dest_positions_2D[0])
    
    ov_split = [origin_verts[i:i + chunk_length] for i in range(0, len(origin_verts), chunk_length)]
    dv_split = [dest_verts[i:i + chunk_length] for i in range(0, len(dest_verts), chunk_length)]
    
    if bridge_edges:
        for o_verts, d_verts in zip(ov_split, dv_split):
            origin_edge_ring = cmds.polyListComponentConversion(o_verts, te=True, internal=True)
            dest_edge_ring = cmds.polyListComponentConversion(d_verts, te=True, internal=True)
            cmds.select(origin_edge_ring, dest_edge_ring)
            cmds.polyBridgeEdge(divisions=0, twist=0, taper=1, curveType=0, smoothingAngle=30, direction=0, sourceDirection=0, targetDirection=0)
        
    elif merge_verts:
        cmds.select(origin_verts, dest_verts)
        cmds.polyMergeVertex(d=merge_threshold)
        
def allign_and_weld_multiple(dest_verts, origin_vert, reference_face_area, local_y_flip=False):
    
    obj_name = origin_vert.split(".")[0]
    vert_id = int("".join([i for i in origin_vert.split(".")[1] if i in string.digits]))
    
    faces = []
    objs = set()
    origin_positions_2D = []
    dest_positions_2D = []
    for dest_vert in dest_verts:    
        new_obj = cmds.duplicate(obj_name)[0]
        new_vert = "{}.vtx[{}]".format(new_obj, vert_id)
        obj1, obj2, op, dp, ftd = allign_and_cache_weld_positions(new_vert, dest_vert, reference_face_area, local_y_flip)
        objs.add(obj1)
        objs.add(obj2)
        origin_positions_2D.append(op)
        dest_positions_2D.append(dp)
        for face in ftd:
            faces.append(face)
    
    cmds.delete(*faces)
    new_obj, _ = cmds.polyUnite(list(objs))
    weld_all(new_obj, origin_positions_2D, dest_positions_2D, bridge_edges=True)


dest_verts = unpack_selection_items(cmds.ls(selection=True))
origin_vert = cmds.ls(selection=True)[0]
reference_face_area = cmds.polyEvaluate(cmds.ls(selection=True)[0], wfa=True)[0]
allign_and_weld_multiple(dest_verts, origin_vert, reference_face_area, local_y_flip=True)
