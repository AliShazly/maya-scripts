from __future__ import division
import maya.cmds as cmds

def get_uv_position(obj_name, coord):
    cmds.select("{}.map[0:]".format(obj_name))
    uv_positions = cmds.polyEditUV(q=True)
    it = iter(uv_positions)

    lowest_dist = 1
    uv_idx = 0
    for idx, pos in enumerate(zip(it, it)):
        dist = distance_between(pos, coord)
        if dist < lowest_dist:
            lowest_dist = dist
            uv_idx = idx

    return get_position("{}.map[{}]".format(obj_name, uv_idx))

def place_light(pos, aim=(0,0,0)):
    light = cmds.shadingNode("VRayLightRectShape", asLight=True)
    loc = cmds.spaceLocator(p=aim)
    cmds.setAttr("{}.translateZ".format(light), 1)
    cmds.aimConstraint(loc, light, maintainOffset=True)
    x, y, z = pos
    cmds.move(x, y, z, light, a=True)
    cmds.scale(1, -1, 1, light, r=True)
    return light

def resize_light(light, bbox_points):
    light_shape = cmds.listRelatives(light)[0]
    tl, tr, br, bl = bbox_points
    u_size = max(distance_between(tl, tr), distance_between(bl, br)) / 2
    v_size = max(distance_between(tl, bl), distance_between(tr, br)) / 2
    cmds.setAttr("{}.uSize".format(light_shape), u_size)
    cmds.setAttr("{}.vSize".format(light_shape), v_size)
    
mid = (0.5869140625, 0.6484375)
bbox = [(0.4580078125, 0.783203125), (0.716796875, 0.783203125), (0.716796875, 0.51171875), (0.4580078125, 0.51171875)]
bbox_world = [get_uv_position("pSphere1", i) for i in bbox]

pos = get_uv_position("pSphere1", mid)
light = place_light(pos)
resize_light(light, bbox_world)