import maya.cmds as cmds


def fix_selected_transforms():
    """選択されたメッシュのTransformを修正する。"""

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    results = []

    # オブジェクトが選択されていない場合
    if not selected:
        return [{
            "object": None,
            "status": "ERROR",
            "message": "オブジェクトが選択されていません"
        }]

    for obj in selected:
        try:
            # メッシュShapeを取得する
            shapes = cmds.listRelatives(
                obj,
                shapes=True,
                noIntermediate=True,
                fullPath=True
            ) or []

            mesh_shapes = [
                shape
                for shape in shapes
                if cmds.nodeType(shape) == "mesh"
            ]

            # メッシュでないオブジェクトは修正しない
            if not mesh_shapes:
                results.append({
                    "object": obj,
                    "status": "SKIP",
                    "message": "メッシュShapeがありません"
                })
                continue

            # 修正前のシーンを更新
            cmds.refresh(force=True)

            # 修正前の境界を取得
            before_bounds = cmds.exactWorldBoundingBox(obj)

            # Freeze Transformationsを実行する
            cmds.makeIdentity(
                obj,
                apply=True,
                translate=True,
                rotate=True,
                scale=True
            )

            # 修正後のシーンを更新
            cmds.refresh(force=True)

            # 修正後の境界を取得
            after_bounds = cmds.exactWorldBoundingBox(obj)

            # 修正後のTransformを取得する
            translate = cmds.getAttr(obj + ".translate")[0]
            rotate = cmds.getAttr(obj + ".rotate")[0]
            scale = cmds.getAttr(obj + ".scale")[0]

            # 修正後のワールド境界を取得する
            after_bounds = cmds.exactWorldBoundingBox(obj)

            # ワールド境界が変わっていないか調べる
            bounds_unchanged = all(
                abs(before_bounds[i] - after_bounds[i]) < 0.0001
                for i in range(6)
            )

            # Transformの値が初期値になっているか調べる
            transform_reset = (
                all(abs(value) < 0.0001 for value in translate)
                and all(abs(value) < 0.0001 for value in rotate)
                and all(abs(value - 1.0) < 0.0001 for value in scale)
            )

            # 修正結果を記録する
            if bounds_unchanged and transform_reset:
                results.append({
                    "object": obj,
                    "status": "OK",
                    "message": "Transformを修正しました。ワールド境界も維持されています"
                })

            elif not bounds_unchanged:
                results.append({
                    "object": obj,
                    "status": "ERROR",
                    "message": "修正後にワールド境界が変化しました"
                })

            else:
                results.append({
                    "object": obj,
                    "status": "ERROR",
                    "message": "Transformを初期値にできませんでした"
                })

        except Exception as error:
            results.append({
                "object": obj,
                "status": "ERROR",
                "message": str(error)
            })

    return results