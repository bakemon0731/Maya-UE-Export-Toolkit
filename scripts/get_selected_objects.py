import maya.cmds as cmds
import re

def validate_name(name):
    pattern = r"^SM_[A-Za-z0-9]+$"
    return bool(re.match(pattern,name))


def validate_selected_meshes():
    selected = cmds.ls(selection=True, long=True) or []

    if not selected:
        print("オブジェクトを選択してください")
        return

    for obj in selected:
        name = obj.split("|")[-1]

        if validate_name(name):
            print(name,"-> 命名規則OK")
        else:
            print(name, "-> 命名規則NG")



validate_selected_meshes()