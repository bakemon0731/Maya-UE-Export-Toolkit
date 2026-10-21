import maya.cmds as cmds


def get_selected_objects():
    selected = cmds.ls(selection=True, long=True) or []
    return selected


objects = get_selected_objects()

print("取得したデータ:", objects)
print("データ型:", type(objects))
print("取得した個数:", len(objects))