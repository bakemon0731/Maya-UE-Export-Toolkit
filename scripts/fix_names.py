import maya.cmds as cmds


# =========================================
# 01. 設定
# =========================================

REQUIRED_PREFIX = "SM_"


# =========================================
# 02. メッシュ判定
# =========================================

def has_mesh_shape(obj):

    shapes = cmds.listRelatives(
        obj,
        shapes=True,
        noIntermediate=True,
        fullPath=True
    ) or []

    return any(
        cmds.nodeType(shape) == "mesh"
        for shape in shapes
    )


# =========================================
# 03. 命名規則の自動修正
# =========================================

def fix_selected_names():

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    results = []

    if not selected:

        return [{
            "object": "不明",
            "status": "ERROR",
            "message": "オブジェクトが選択されていません。",
            "details": []
        }]

    for obj in selected:

        object_name = obj.split("|")[-1]

        try:

            # メッシュShapeの存在確認
            if not has_mesh_shape(obj):

                results.append({
                    "object": object_name,
                    "status": "SKIP",
                    "message": "メッシュShapeがありません。",
                    "details": []
                })

                continue

            # すでに命名規則を満たしている場合
            if object_name.startswith(REQUIRED_PREFIX):

                results.append({
                    "object": obj,
                    "status": "OK",
                    "message": "すでに命名規則を満たしています。",
                    "details": []
                })

                continue

            # 修正後の名前を作成
            new_name = REQUIRED_PREFIX + object_name

            # オブジェクト名を変更
            renamed_object = cmds.rename(
                obj,
                new_name
            )

            # 変更後のフルパスを取得
            renamed_paths = cmds.ls(
                renamed_object,
                long=True,
                type="transform"
            ) or []

            if not renamed_paths:

                raise RuntimeError(
                    "変更後のオブジェクトを取得できませんでした。"
                )

            renamed_path = renamed_paths[0]

            actual_name = renamed_path.split("|")[-1]

            results.append({
                "object": renamed_path,
                "status": "OK",
                "message": "命名規則を自動修正しました。",
                "details": [
                    {
                        "変更前": object_name,
                        "変更後": actual_name,
                        "変更前パス": obj,
                        "変更後パス": renamed_path
                    }
                ]
            })

        except Exception as error:

            results.append({
                "object": object_name,
                "status": "ERROR",
                "message": "命名規則の修正に失敗しました。",
                "details": [
                    str(error)
                ]
            })

    return results