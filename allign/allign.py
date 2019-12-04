import maya.cmds as cmds
import string
import math

def allign(vtx1, vtx2, local_y_flip=False):
    """Alligns the normal of vtx1 to the normal of vtx2

    Args:
        vtx1 (str): name of the source vertex
        vtx2 (str): name of the destination vertex
        local_y_flip (bool): whether to flip source object along it's Y axis once alligned

    Returns:
        None
    """

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


def allign_and_cache_weld_positions(vtx1, vtx2, reference_area=None, local_y_flip=False):
    """Alligns the normal of vtx1 to the normal of vtx2 and stores information needed to weld the two objects

    Args:
        vtx1 (str): name of the source vertex
        vtx2 (str): name of the destination vertex
        reference_area (float): reference face area from the source object for relative resizing
        local_y_flip (bool): whether to flip source object along it's Y axis once alligned

    Returns:
        obj1 (str): name of the source object
        obj2 (str): name of the destination object
        bv_cache1 (float[]): list of border vertex positions on the source object
        bv_cache2 (float[]): list of border vertex positions on the destination object
        faces_to_delete (str[]): list of border faces to delete before merging objects
    """

    # Getting the faces around the source and destination vertices
    faces1 = unpack_selection_items(cmds.polyListComponentConversion([vtx1], fv=True, tf=True))
    faces2 = unpack_selection_items(cmds.polyListComponentConversion([vtx2], fv=True, tf=True))

    # Getting the border vertices to weld the two objects together
    border_verts1 = unpack_selection_items(cmds.polyListComponentConversion(faces1, ff=True, tv=True))
    border_verts2 = unpack_selection_items(cmds.polyListComponentConversion(faces2, ff=True, tv=True))
    border_verts1.remove(vtx1)
    border_verts2.remove(vtx2)

    allign(vtx1, vtx2, local_y_flip)

    # Getting the object names of the source and destination vertices
    obj1 = vtx1.split(".")[0]
    obj2 = vtx2.split(".")[0]

    # Resizing the source object relative to the reference area if it is given
    if reference_area:
        face = faces2[0]
        area = cmds.polyEvaluate(face, wfa=True)[0]
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


def weld_all(obj_name, source_positions_2D, dest_positions_2D, maintain_source_shape=False):
    """Welds all the source verticies to the destination verticies by bridging or merging

    Args:
        obj_name (str): name of the object to weld
        source_positions_2D (float[][]): positions of source vertecies
        dest_positions_2D (float[][]): positions of destination vertecies
        maintain_source_shape (bool): maintain the shape of the source object by leaving a bridge between the two borders

    Returns:
        None
    """

    cmds.select(cl=True)

    num_verts = cmds.polyEvaluate(obj_name, v=True)

    # Script encounters float comparison errors if I don't round all of the positions
    source_positions_2D = [[[round(i, 2) for i in pos] for pos in sp] for sp in source_positions_2D]
    dest_positions_2D = [[[round(i, 2) for i in pos] for pos in dp] for dp in dest_positions_2D]

    # Looping through all the vertices of the object to find the verts that match the stored positions
    source_verts = []
    dest_verts = []
    for i in range(num_verts):
        vert = "{}.vtx[{}]".format(obj_name, i)
        pos = get_position(vert)
        pos = [round(i, 2) for i in pos]

        idx = 0
        for sp, dp in zip(source_positions_2D, dest_positions_2D):
            if pos in sp:
                source_verts.append((idx, vert))
            elif pos in dp:
                dest_verts.append((idx, vert))
            idx += 1

    # Splitting the vertices into chunks based on the vert count of the border edges
    source_verts = [j for i, j in sorted(source_verts, key=lambda x: x[0])]
    dest_verts = [j for i, j in sorted(dest_verts, key=lambda x: x[0])]
    chunk_length = len(dest_positions_2D[0])
    sv_split = [source_verts[i:i + chunk_length] for i in range(0, len(source_verts), chunk_length)]
    dv_split = [dest_verts[i:i + chunk_length] for i in range(0, len(dest_verts), chunk_length)]

    # Bridging each pair of border edges together
    edges_to_delete = []
    for s_verts, d_verts in zip(sv_split, dv_split):
        source_edge_ring = cmds.polyListComponentConversion(s_verts, te=True, internal=True)
        dest_edge_ring = cmds.polyListComponentConversion(d_verts, te=True, internal=True)
        cmds.select(source_edge_ring, dest_edge_ring)
        try:
            cmds.polyBridgeEdge(divisions=0, twist=0, taper=1, curveType=0, smoothingAngle=30, direction=0, sourceDirection=0, targetDirection=0)
            edges_to_delete.append(source_edge_ring)
        except RuntimeError:
            raise Exception("Precision too low, lower current working units to mm")

    if not maintain_source_shape:
        # Deleting the leftover edge loop from bridge
        cmds.select(cl=True)
        for edge_loop in edges_to_delete:
            cmds.select(edge_loop, add=True)
        cmds.polyDelEdge(cv=True)

def allign_and_weld_multiple(source_vert, dest_verts, reference_face_area, local_y_flip=False, maintain_source_shape=False):
    """Alligns and welds multiple copies of the same source object to specified destinations

    Args:
        source_vert (str): source vertex to allign and weld along destination verts
        dest_verts (str[]): list of vertices to be used as destinations
        reference_face_area (float): reference face area for relative resizing
        local_y_flip (bool): whether to flip source object along it's Y axis once alligned
        maintain_source_shape (bool): maintain the shape of the source object by leaving a bridge between the two borders

    Returns:
        None
    """

    obj_name = source_vert.split(".")[0]
    vert_id = int("".join([i for i in source_vert.split(".")[1] if i in string.digits]))

    # Alligning all the copies to the destinations
    faces = []
    objs = set()
    source_positions_2D = []
    dest_positions_2D = []
    for dest_vert in dest_verts:
        new_obj = cmds.duplicate(obj_name)[0]
        new_vert = "{}.vtx[{}]".format(new_obj, vert_id)
        obj1, obj2, sp, dp, ftd = allign_and_cache_weld_positions(new_vert, dest_vert, reference_face_area, local_y_flip)
        objs.add(obj1)
        objs.add(obj2)
        source_positions_2D.append(sp)
        dest_positions_2D.append(dp)
        for face in ftd:
            faces.append(face)

    # Merging and welding copies to destination object
    cmds.delete(*faces)
    new_obj, _ = cmds.polyUnite(list(objs))
    weld_all(new_obj, source_positions_2D, dest_positions_2D)

# Select all destination verts and run this line
dest_verts = unpack_selection_items(cmds.ls(selection=True))
# Select source vertex and run this line
source_vert = cmds.ls(selection=True)[0]
# Select one face on the bottom of the source object and run this line
reference_face_area = cmds.polyEvaluate(cmds.ls(selection=True)[0], wfa=True)[0]
# Run this line to execute
allign_and_weld_multiple(source_vert, dest_verts, reference_face_area, local_y_flip=True)
