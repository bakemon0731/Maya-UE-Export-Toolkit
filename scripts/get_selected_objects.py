import maya.cmds as cmds


def validate_selected_meshes():
    selected = cmds.ls(selection=True, long=True) or []

    if not selected:
        print("オブジェクトを選択してください")
        return

    for obj in selected:
        shapes = cmds.listRelatives(
            obj,
            shapes=True,
            noIntermediate=True,
            fullPath=True
        ) or []

        if not shapes:
            print("Shapeが見つかりません:", obj)
            continue

        for shape in shapes:
            shape_type = cmds.nodeType(shape)

            print("オブジェクト:", obj)
            print("Shape:", shape)
            print("ノードの種類:", shape_type)

            if shape_type == "mesh":
                print("ポリゴンメッシュです")
            else:
                print("ポリゴンメッシュではありません")


validate_selected_meshes()