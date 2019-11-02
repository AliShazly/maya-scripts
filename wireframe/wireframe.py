import maya.cmds as cmds  

def wireframe(obj_name, offset, thickness):
    cmds.select(obj_name + ".f[0:]")
    cmds.setAttr(cmds.polyExtrudeFacet(keepFacesTogether=False)[0] + ".offset", offset)
    cmds.delete()
    cmds.select("{}.f[0:]".format(obj_name))
    cmds.polyExtrudeFacet(thickness=thickness)