from __future__ import print_function, division

import maya.cmds as cmds
import string

def line_intersection(a1, a2, b1, b2):
    line1 = (a1, a2)
    line2 = (b1, b2)
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def straighten_edges(move_axis, other_axis, max_y=999):
    idx2, idx1 = move_axis, other_axis
    edge1, edge2 = unpack_selection_items(cmds.ls(selection=True))
    edge1_pos = get_position(edge1, object_space=True)
    edge2_pos = get_position(edge2, object_space=True)
    a1 = (edge1_pos[idx1], edge1_pos[idx2])
    a2 = (edge2_pos[idx1], edge2_pos[idx2])

    # Getting all verts inbetween the two edges
    obj_name = edge1.split(".")[0]
    edge1_id = int("".join([i for i in edge1.split(".")[1] if i in string.digits]))
    edge2_id = int("".join([i for i in edge2.split(".")[1] if i in string.digits]))
    cmds.polySelect(obj_name, erp=[edge1_id, edge2_id], r=True)
    edges = unpack_selection_items(cmds.ls(selection=True))
    verts_packed = cmds.polyListComponentConversion(edges, fe=True, tv=True)
    verts = unpack_selection_items(verts_packed)

    for vert in verts:
        pos = get_position(vert, object_space=True)
        b1 = (pos[idx1], pos[idx2])
        b2 = (pos[idx1], max_y)
        _, y = line_intersection(a1, a2, b1, b2)
        cmds.select(vert)
        if idx2 == 0:
            cmds.move(y, x=True, os=True)
        elif idx2 == 1:
            cmds.move(y, y=True, os=True)
        elif idx2 == 2:
            cmds.move(y, z=True, os=True)  

def straighten_multiple_edges(edge_loop_1, edge_loop_2, move_axis, other_axis):
    # This is so stupid but it works
    all_axis = [0,1,2]
    all_axis.remove(move_axis)
    all_axis.remove(other_axis)
    sort_axis = all_axis[0]
    edge_loop_1 = sorted(edge_loop_1, key=lambda x: get_position(x, object_space=True)[sort_axis])
    edge_loop_2 = sorted(edge_loop_2, key=lambda x: get_position(x, object_space=True)[sort_axis])
    for edge1, edge2 in zip(edge_loop_1, edge_loop_2):
        cmds.select(edge1, edge2, r=True)
        straighten_edges(move_axis, other_axis)
        
x = 0
y = 1
z = 2
# run this on the first edge loop
el1 = unpack_selection_items(cmds.ls(selection=True))
# run this on the second edge loop
el2 = unpack_selection_items(cmds.ls(selection=True))
# run this to execute
straighten_multiple_edges(el1, el2, move_axis=y, other_axis=x)