import maya.cmds as cmds


def fix_selected_history():
    """選択されたメッシュのポリゴンモデリング履歴を削除する。"""

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
            # メッシュShapeを取得
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

            # メッシュ以外はスキップ
            if not mesh_shapes:
                results.append({
                    "object": obj,
                    "status": "SKIP",
                    "message": "メッシュShapeがありません"
                })
                continue

            # Construction Historyを取得
            history = cmds.listHistory(
                obj,
                pruneDagObjects=True
            ) or []

            # 既に履歴がない場合
            if not history:
                results.append({
                    "object": obj,
                    "status": "OK",
                    "message": "Construction Historyはありません"
                })
                continue

            # 履歴ノードの種類を調べる
            history_types = {
                node: cmds.nodeType(node)
                for node in history
            }

            # poly系以外の履歴があれば、自動削除しない
            unsupported_nodes = [
                node
                for node, node_type in history_types.items()
                if not node_type.startswith("poly")
            ]

            if unsupported_nodes:
                results.append({
                    "object": obj,
                    "status": "SKIP",
                    "message": (
                        "ポリゴンモデリング以外の履歴があるため、"
                        "自動削除を見送りました"
                    ),
                    "details": [
                        {
                            "node": node,
                            "type": history_types[node]
                        }
                        for node in unsupported_nodes
                    ]
                })
                continue

            # 削除前の形状情報を記録
            before_bounds = cmds.exactWorldBoundingBox(obj)

            before_vertices = cmds.polyEvaluate(
                obj,
                vertex=True
            )

            before_faces = cmds.polyEvaluate(
                obj,
                face=True
            )

            # Construction Historyを削除
            cmds.delete(
                obj,
                constructionHistory=True
            )

            # 削除後の形状情報を取得
            after_history = cmds.listHistory(
                obj,
                pruneDagObjects=True
            ) or []

            after_bounds = cmds.exactWorldBoundingBox(obj)

            after_vertices = cmds.polyEvaluate(
                obj,
                vertex=True
            )

            after_faces = cmds.polyEvaluate(
                obj,
                face=True
            )

            # ワールド境界の差を比較
            differences = [
                abs(before_bounds[i] - after_bounds[i])
                for i in range(6)
            ]

            bounds_unchanged = all(
                difference < 0.0001
                for difference in differences
            )

            # 頂点数と面数が維持されているか確認
            geometry_unchanged = (
                before_vertices == after_vertices
                and before_faces == after_faces
            )

            # 履歴がなくなり、形状も維持されていれば成功
            if (
                not after_history
                and bounds_unchanged
                and geometry_unchanged
            ):
                results.append({
                    "object": obj,
                    "status": "OK",
                    "message": (
                        "Construction Historyを削除しました。"
                        "ワールド境界・頂点数・面数は維持されています"
                    )
                })

            else:
                results.append({
                    "object": obj,
                    "status": "ERROR",
                    "message": (
                        "削除後の履歴または形状が"
                        "期待どおりではありません"
                    ),
                    "details": {
                        "remaining_history": after_history,
                        "bounds_unchanged": bounds_unchanged,
                        "vertices_unchanged": (
                            before_vertices == after_vertices
                        ),
                        "faces_unchanged": (
                            before_faces == after_faces
                        )
                    }
                })

        except Exception as error:
            results.append({
                "object": obj,
                "status": "ERROR",
                "message": str(error)
            })

    return results