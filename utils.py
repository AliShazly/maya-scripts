from __future__ import division

import string
import re
import math
import maya.cmds as cmds

class Component:
    """Basic struct for maya components"""
    def __init__(self, name, x, y, z):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        if self.name:
            return "{}: (x: {}, y: {}, z: {})".format(self.name, self.x, selfa.y, self.z)
        return "(x: {}, y: {}, z: {})".format(self.x, self.y, self.z)

    @property
    def id(self):
        return "".join(re.findall(r"\[(\d+)\]", self.name))


def format_polyinfo(polyinfo_output, flt=True):
    """Formats string output from cmds.polyInfo to usable data"""
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


def get_position(obj_name=None, object_space=False, rounding=0):
    """Returns the position of a specified object"""
    if obj_name is not None:
        cmds.select(obj_name, r=True)
    if object_space:
        pos = cmds.xform(obj_name, q=True, translation=True, os=True)
    else:
        pos = cmds.xform(obj_name, q=True, translation=True, worldSpace=True)
    if len(pos) > 3:
        # Splitting into sublists and averaging to find the center
        pos = [pos[i:i + 3] for i in range(0, len(pos), 3)]
        l = len(pos)
        pos_x = sum(pt[0] for pt in pos) / l
        pos_y = sum(pt[1] for pt in pos) / l
        pos_z = sum(pt[2] for pt in pos) / l
        pos = [pos_x, pos_y, pos_z]
    if rounding:
        return [round(i, rounding) for i in pos]
    return pos


def unpack_selection_items(selection_items):
    """Unpacks slice notation into seperate items
    
    ["pPlane1.vtx[50:52]"] -> ["pPlane1.vtx[50]", "pPlane1.vtx[51]", "pPlane1.vtx[52]"]
    """
    unformatted = []
    for selection_item in selection_items:
        if ":" not in selection_item:
            unformatted.append(selection_item)
            continue
        name, type_ = selection_item.split(".")
        type_ = filter(lambda x: x in string.ascii_letters, type_)
        nums = selection_item.split('[', 1)[1].split(']')[0]
        num1, num2, = [int(i) for i in nums.split(":")]
        unformatted.append(["{}.{}[{}]".format(name, type_, i) for i in range(num1, num2 + 1)])
    formatted = []
    for i in unformatted:
        if type(i) != list:
            formatted.append(i)
        else:
            for j in i:
                formatted.append(j)
    return formatted

def cube_at_point(pos):
    """Spawns a cube with the origin at a specified point"""
    o, n = cmds.polyCube()
    cmds.select(o)
    cmds.move(*pos, a=True, ws=True)

def distance_between(pos1, pos2):
    """Returns distance between two points"""
    difference = [i - j for i, j in zip(pos1, pos2)]
    power = [i ** 2 for i in difference]
    squared_dist = sum(power)
    return math.sqrt(squared_dist)
