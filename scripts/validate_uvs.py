import maya.cmds as cmds


# 検証処理を担当する関数
def validate_uvs(obj):
    name = obj.split("|")[-1]

    shapes = cmds.listRelatives(
        obj,
        shapes=True,
        noIntermediate=True,
        fullPath=True,
        type="mesh"
    ) or []

    if not shapes:
        print(name, "-> Meshが見つかりません")
        return

    for shape in shapes:
        uv_sets = cmds.polyUVSet(shape,query=True,allUVSets=True) or []

        if not uv_sets:
            print(name, "-> UVセットなし")
            continue

        # 最初のUVセットを検証する
        uv_set = uv_sets[0]

        uv_count = cmds.polyEvaluate(shape,uvcoord=True,uvSetName=uv_set) or 0

        print("オブジェクト:", name)
        print("UVセット:", uv_set)
        print("UV座標数:", uv_count)

        if uv_count > 0:
            print(name, "-> UV座標あり")
        else:
            print(name, "-> UV座標なし")


def validate_selected_uvs():
    selected = cmds.ls(selection=True,long=True,type="transform") or []

    if not selected:
        print("オブジェクトを選択してください")
        return

    for obj in selected:
        validate_uvs(obj)


validate_selected_uvs()