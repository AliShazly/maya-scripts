from __future__ import division

import json
import maya.cmds as cmds
import mtoa.utils as mutils


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


def place_light(pos, bbox_points, aim=(0,0,0)):
    light = mutils.createLocator("aiAreaLight", asLight=True)[1]
    loc = cmds.spaceLocator(p=aim)
    cmds.setAttr("{}.translateZ".format(light), 1)
    cmds.aimConstraint(loc, light, maintainOffset=True)

    x, y, z = pos
    cmds.move(x, y, z, light, a=True)
    
    tl, tr, br, bl = bbox_points
    u_size = max(distance_between(tl, tr), distance_between(bl, br)) / 2
    v_size = max(distance_between(tl, bl), distance_between(tr, br)) / 2
    cmds.scale(u_size, v_size, 1, light, r=True)
   
    return light


def resize_light(light, bbox_points, midpoint):
    tl, tr, br, bl = bbox_points
    u_size = max(distance_between(tl, tr), distance_between(bl, br)) / 2
    v_size = max(distance_between(tl, bl), distance_between(tr, br)) / 2
    cmds.select(light)
    cmds.scale(u_size, v_size, 1, light, r=True)


def main(data_path, radius=700, divisions=100, intensity=15, exposure=11.5):
    with open(data_path, "r") as f:
        data = json.load(f)
    
    sphere_name, _ = cmds.polySphere(radius=radius, sx=divisions, sy=divisions)
    # Flipping UVs and rotating to match default arnold dome light position
    cmds.select("{}.map[0:]".format(sphere_name))
    cmds.polyFlipUV(usePivot=True, pivotU=0.5, pivotV=0.5)
    cmds.setAttr("{}.rotateY".format(sphere_name), 86.4)

    for i in range(data["num_lights"]):
        bbox_points = data[str(i)]["bbox_points"]
        mid_point = data[str(i)]["mid_point"]
        tex_path = data[str(i)]["rect_tex"]
        
        bbox_world = [get_uv_position(sphere_name, i) for i in bbox_points]
        mid_pos = get_uv_position(sphere_name, mid_point)
        light = place_light(mid_pos, bbox_world)
        
        file_node = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr("{}.fileTextureName".format(file_node), tex_path, type="string")

        light_shape = cmds.listRelatives(light)[0]        
        cmds.connectAttr("{}.outColor".format(file_node), "{}.color".format(light_shape))
        
        cmds.setAttr("{}.intensity".format(light_shape), intensity)
        cmds.setAttr("{}.exposure".format(light_shape), exposure)        
        
    
    hdr_path = data["hdr"]
    light_dome = mutils.createLocator("aiSkyDomeLight", asLight=True)[1]
    light_dome_shape = cmds.listRelatives(light_dome)[0]
    hdr_file_node = cmds.shadingNode("file", asTexture=True)
    cmds.setAttr("{}.fileTextureName".format(hdr_file_node), hdr_path, type="string")
    cmds.connectAttr("{}.outColor".format(hdr_file_node), "{}.color".format(light_dome_shape))
        
    cmds.delete(sphere_name)
    
        
data_path = "D:\\personalProjects\\maya-scripts\\extract-hdri\\"
filename = "extract-hdri.json"
main(data_path + filename)