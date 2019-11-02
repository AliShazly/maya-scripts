from __future__ import division

import maya.cmds as cmds
import string

def format_polyinfo(polyinfo_output, flt=True):
    out = []
    for s in polyinfo_output:
        ascii_filtered = "".join([i for i in s if i not in string.ascii_letters])
        formatted = ascii_filtered.split(":")[1].split(" ")
        empty_strings_filtered = filter(None, formatted)
        newline_filtered = [i for i in empty_strings_filtered if i != u"\n"]
        converted = [float(i) if flt else int(i) for i in newline_filtered]
        out.append(converted)
    if len(out) > 1:
        return out
    return out[0]


def get_position(obj_name=None):
    if obj_name is not None:
        cmds.select(obj_name, r=True)
    pos = cmds.xform(obj_name, q=True, translation=True, worldSpace=True)
    if len(pos) > 3:
        # Splitting into sublists and averaging to find the center
        pos = [pos[i:i + 3] for i in range(0, len(pos), 3)]
        l = len(pos)
        pos_x = sum(pt[0] for pt in pos) / l
        pos_y = sum(pt[1] for pt in pos) / l
        pos_z = sum(pt[2] for pt in pos) / l
        pos = [pos_x, pos_y, pos_z]        
    return [round(i, 5) for i in pos]


def clear():
    cmds.select(all=True)
    cmds.Delete()