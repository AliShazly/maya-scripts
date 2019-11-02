from __future__ import print_function, division

import maya.cmds as cmds
import re

# from utils import *

class Component:
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

# https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def lines_intersect(pt1, pt2, pt3, pt4):
    
    # Returns true if points are in counter clockwise order
    def ccw(pt1, pt2, pt3):
        return (pt3.z - pt1.z) * (pt2.x - pt1.x) > (pt2.z - pt1.z) * (pt3.x - pt1.x)
    
    return ccw(pt1, pt3, pt4) != ccw(pt2, pt3, pt4) and ccw(pt1, pt2, pt3) != ccw(pt1, pt2, pt4)

def cut_at_y(obj_name, y_val):
    cmds.polyCut(obj_name, pc=[-999, y_val, 999], ro=[90, -90, 0])
    edge_num = cmds.polyEvaluate(obj_name, e=True)
    return "{}.e[{}]".format(obj_name, edge_num)

# Add Better curve accuracy around hard corners
def edge_loop_to_curve(edge_name, delete_edges=False):
    cmds.select(edge_name)
    cmds.pickWalk(edge_name, type="edgeloop", d="right")
    curve_name, shape_name = cmds.polyToCurve(form=2, degree=3)
    cvs = cmds.getAttr("{}.spans".format(curve_name))
    curve_points = []
    for cv_id in range(cvs):
        cv_name = "{}.cv[{}]".format(curve_name, cv_id)
        pos = get_position(cv_name)
        curve_points.append(Component(cv_name, *pos))

    if delete_edges:
        cmds.select(edge_name)
        cmds.pickWalk(edge_name, type="edgeloop", d="right")
        cmds.polyDelEdge(cv=True)
        
    cmds.select(curve_name)
    cmds.Delete()
    return curve_points

# Curve points list must be even length, also it has to be a list of components.
def point_in_curve(pt1, curve_points, max_x=999):
    pt2 = Component(None, max_x, pt1.y, pt1.z)
    intersections = 0
    for idx, pt in enumerate(curve_points):
        pt3 = pt
        try:
            pt4 = curve_points[idx + 1]
        except IndexError:
            pt4 = curve_points[0]
        if lines_intersect(pt1, pt2, pt3, pt4):
            intersections += 1
    if intersections % 2 == 0:
        return False
    return True

def get_intersection(ground, obj):
    intersection_points = []
    edge_name = cut_at_y(obj, 0)
    curve_points = edge_loop_to_curve(edge_name, delete_edges=True)
    for face_id in range(cmds.polyEvaluate(ground, f=True)):
        face_name = "{}.f[{}]".format(ground, face_id)
        pos = get_position(face_name)
        face = Component(face_name, *pos)
        if point_in_curve(face, curve_points):
            intersection_points.append(face.name)
    return intersection_points
    
intersection_points = get_intersection("pPlane1", "pCube1")
cmds.select(*intersection_points)