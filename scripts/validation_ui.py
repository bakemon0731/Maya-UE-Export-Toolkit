from pydoc import text
import sys
import importlib
import maya.cmds as cmds


# 検証スクリプトが保存されているフォルダ
SCRIPT_DIR = r"E:\Maya-UE-Export-Toolkit\scripts"

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


# 命名規則チェックを読み込む
import validate_names
importlib.reload(validate_names)
import validate_transforms
importlib.reload(validate_transforms)
import validate_history
importlib.reload(validate_history)
import validate_ngons
importlib.reload(validate_ngons)
import validate_uvs
importlib.reload(validate_uvs)


# ウィンドウの名前
WINDOW_NAME = "MayaUEValidationWindow"


def run_name_check(*args):
    """命名規則を検証して、結果をGUIに表示する。"""

    #names検証機能を呼び出し
    results = validate_names.validate_selected_names()

    # GUIに表示する文章を用意する
    lines = []

    if not results:
        lines.append("検証結果がありません。")
        lines.append("オブジェクトを選択してください。")

    else:
        lines.append("===== 命名規則チェック結果 =====")
        lines.append("")

        for result in results:
            lines.append(
                "オブジェクト: " + result["object"]
            )
            lines.append(
                "結果: " + result["status"]
            )
            lines.append(
                "詳細: " + result["message"]
            )
            lines.append("")

        # NG件数を集計する
        ng_count = sum(
            1
            for result in results
            if result["status"] == "NG"
        )

        lines.append("検証対象数: " + str(len(results)))
        lines.append("NG件数: " + str(ng_count))

    # 文章を1つにまとめる
    output_text = "\n".join(lines)

    # GUIの表示欄を更新する
    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )

def run_transform_check(*args):
    """Transformを検証して、結果をGUIに表示する。"""

    #Transform検証機能を呼び出し
    results = validate_transforms.validate_selected_transforms()

    lines = []

    if not results:
        lines.append("検証結果がありません。")
        lines.append("")

    else:
        lines.append("===== Transformチェック結果 =====")
        lines.append("")

        for result in results:
            lines.append(
                "オブジェクト: " + result["object"]
            )
            lines.append(
                "結果: " + result["status"]
            )
            lines.append(
                "詳細: " + result["message"]
            )

            if result["details"]:
                lines.append(
                    "対象属性: " + ", ".join(result["details"])
                )

            lines.append("")

        ng_count = sum(
            1
            for result in results
            if result["status"] == "NG"
        )

        lines.append("検証対象数: " + str(len(results)))
        lines.append("NG件数: " + str(ng_count))

    output_text = "\n".join(lines)

    cmds.scrollField(OUTPUT_FIELD,edit=True,text=output_text)

def run_history_check(*args):
    """Construction Historyを検証して、結果をGUIに表示する。"""

    results = validate_history.validate_selected_history()

    lines = []

    if not results:
        lines.append("検証結果がありません。")
        lines.append("オブジェクトを選択してください。")

    else:
        lines.append("===== Construction Historyチェック結果 =====")
        lines.append("")

        for result in results:
            lines.append(
                "オブジェクト: " + result["object"]
            )
            lines.append(
                "結果: " + result["status"]
            )
            lines.append(
                "詳細: " + result["message"]
            )

            if result["details"]:
                lines.append(
                    "履歴ノード: " + ", ".join(result["details"])
                )

            lines.append("")

        ng_count = sum(
            1
            for result in results
            if result["status"] == "NG"
        )

        lines.append("検証対象数: " + str(len(results)))
        lines.append("NG件数: " + str(ng_count))

    output_text = "\n".join(lines)

    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )

def run_ngon_check(*args):
    """N-gonを検証して、結果をGUIに表示する。"""

    results = validate_ngons.validate_selected_ngons()

    lines = []

    if not results:
        lines.append("検証結果がありません。")
        lines.append("オブジェクトを選択してください。")

    else:
        lines.append("===== N-gonチェック結果 =====")
        lines.append("")

        for result in results:
            lines.append(
                "オブジェクト: " + result["object"]
            )
            lines.append(
                "結果: " + result["status"]
            )
            lines.append(
                "詳細: " + result["message"]
            )

              # N-gonが見つかった場合、面ごとの情報を表示する
            if result["details"]:
                lines.append("N-gonの詳細:")

                for face_data in result["details"]:
                    lines.append(
                        "  Shape: " + face_data["shape"]
                    )
                    lines.append(
                        "  面番号: " + str(face_data["face_index"])
                    )
                    lines.append(
                        "  頂点数: " + str(face_data["vertex_count"])
                    )

            lines.append("")

        ng_count = sum(
            1
            for result in results
            if result["status"] == "NG"
        )

        lines.append("検証対象数: " + str(len(results)))
        lines.append("NG件数: " + str(ng_count))
    
    output_text = "\n".join(lines)

    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )
                
def run_uv_check(*args):
    """UVを検証して、結果をGUIに表示する。"""

    results = validate_uvs.validate_selected_uvs()

    lines = []

    if not results:
        lines.append("検証結果がありません。")
        lines.append("オブジェクトを選択してください。")

    else:
        lines.append("===== UVチェック結果 =====")
        lines.append("")

        for result in results:
            lines.append(
                "オブジェクト: " + result["object"]
            )
            lines.append(
                "結果: " + result["status"]
            )
            lines.append(
                "詳細: " + result["message"]
            )

            # UVセットごとの情報を表示する
            if result["details"]:
                lines.append("UVの詳細:")

                for uv_data in result["details"]:
                    lines.append(
                        "  Shape: " + uv_data["shape"]
                    )
                    lines.append(
                        "  UVセット: " + str(uv_data["uv_set"])
                    )
                    lines.append(
                        "  UV座標数: " + str(uv_data["uv_count"])
                    )

            lines.append("")

        ng_count = sum(
            1
            for result in results
            if result["status"] == "NG"
        )

        lines.append("検証対象数: " + str(len(results)))
        lines.append("NG件数: " + str(ng_count))

    output_text = "\n".join(lines)

    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )


def run_all_checks(*args):
    """5つの検証を実行し、結果をGUIにまとめて表示する。"""

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    if not selected:
        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text="オブジェクトを選択してください。"
        )
        return

    # 検証名と実行する関数をまとめる
    checks = [
        ("命名規則", validate_names.validate_selected_names),
        ("Transform", validate_transforms.validate_selected_transforms),
        ("Construction History", validate_history.validate_selected_history),
        ("N-gon", validate_ngons.validate_selected_ngons),
        ("UV", validate_uvs.validate_selected_uvs),
    ]

    # すべての検証結果を集めるリスト
    all_results = []

    # 例外が発生した検証の情報を保存するリスト
    errors = []

    # 5つの検証を順番に実行する
    for label, check_function in checks:
        try:
            results = check_function() or []
            all_results.extend(results)

        except Exception as error:
            errors.append({
                "check": label,
                "type": type(error).__name__,
                "message": str(error)
            })

    # GUIに表示する文章を作成する
    lines = []
    lines.append("===== 全項目チェック結果 =====")
    lines.append("")

    # 各検証結果を表示する
    for result in all_results:
        lines.append("オブジェクト: " + result.get("object", "不明"))
        lines.append("検証項目: " + result.get("check", "不明"))
        lines.append("結果: " + result.get("status", "不明"))
        lines.append("説明: " + result.get("message", ""))

        details = result.get("details", [])

        if details:
            lines.append("追加情報:")

            for detail in details:
                if isinstance(detail, dict):
                    for key, value in detail.items():
                        lines.append(
                            " " + str(key) + ": " + str(value)
                        )
                else:
                    lines.append(" " + str(detail))
        
        lines.append("")

    # OKとNGの検証結果を集計する
    ok_count = sum(
        1 for result in all_results
        if result.get("status") == "OK"
    )

    ng_count = sum(
        1 for result in all_results
        if result.get("status") == "NG"
    )

    # 最後に集計結果を表示する
    lines.append("===== 実行サマリー =====")
    lines.append("検証対象オブジェクト数: " + str(len(selected)))
    lines.append("取得した検証結果数: " + str(len(all_results)))
    lines.append("検証OK件数: " + str(ok_count))
    lines.append("検証NG件数: " + str(ng_count))
    lines.append("例外が発生した数: " + str(len(errors)))

    # エラーがあれば、その内容も表示する
    if errors:
        lines.append("")
        lines.append("===== エラー詳細 =====")

        for error in errors:
            lines.append("検証項目: " + error["check"])
            lines.append("エラーの種類: " + error["type"])
            lines.append("エラーの詳細: " + error["message"])
            lines.append("")

    output_text = "\n".join(lines)

    # GUIの表示欄を更新する
    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )

    return all_results

def validate_and_export(*args):
    """検証を実行し、すべてOKの場合だけFBXを書き出す。"""

    # 5種類の検証を実行
    results = run_all_checks()

    # 検証結果がない場合は中止
    if not results:
        message = "検証結果がありません。選択状態を確認してください。"
        print(message)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=message
        )

        return {
            "status": "ERROR",
            "message": message
        }

    # OK以外の結果を抽出
    failed_results = [
        result
        for result in results
        if result.get("status") != "OK"
    ]

    # NGやERRORがあれば書き出さない
    if failed_results:
        output_lines = [
            "検証NGがあるため、FBX書き出しを中止します"
        ]

        for result in failed_results:
            output_lines.append(
                "対象: {} | 検証: {} | 状態: {} | 内容: {}".format(
                    result.get("object"),
                    result.get("check"),
                    result.get("status"),
                    result.get("message")
                )
            )

        output_text = "\n".join(output_lines)

        print(output_text)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=output_text
        )

        return{
            "status": "NG",
            "message": "検証NGがあるため、書き出しを中止しました",
            "failed_results": failed_results
        }

    #すべてOKの場合だけFBX書き出しを実行
    try:
        import importlib
        import export_fbx

        importlib.reload(export_fbx)

        export_result = export_fbx.export_selected_fbx()

        # 書き出し結果をUIに表示
        status = export_result.get("status")

        if status == "OK":
            output_lines = [
                "すべての検証に合格しました",
                "FBX書き出しが完了しました",
                "保存先: {}".format(
                    export_result.get("file_path")
                )
            ]

        elif status == "CANCELLED":
            output_lines = [
                "検証はすべてOKです",
                "FBX書き出しはキャンセルされました"
            ]

        else:
            output_lines = [
                "検証はすべてOKです",
                "FBX書き出しに失敗しました",
                "エラー: {}".format(
                    export_result.get("message","詳細不明")
                )
            ]

        output_text = "\n".join(output_lines)

        print(output_text)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=output_text
        )

        return export_result

    #書き出し中のtryが失敗した場合実行
    except Exception as error:
        message = "統合処理でエラーが発生しました: {}".format(error)

        print(message)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=message
        )

        return {
            "status": "ERROR",
            "message": str(error)
        }

def fix_transforms_and_revalidate(*args):
    """Transformを自動修正し、5種類の検証を再実行する。"""

    # 選択中のオブジェクトを取得する
    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    # オブジェクトが選択されていなければ終了
    if not selected:
        message = (
            "オブジェクトが選択されていません。"
            "Transform自動修正を中止しました。"
        )

        print(message)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=message
        )

        error_result = {
            "object": None,
            "check": "選択状態",
            "status": "ERROR",
            "message": message
        }

        return {
            "fix_results": [error_result],
            "validation_results": [],
            "failed_results": [error_result]
        }

    # Transform自動修正の確認ダイアログ
    selected_names = [
        obj.split("|")[-1]
        for obj in selected
    ]

    object_list = "\n".join(
        "- " + name
        for name in selected_names
    )

    # 修正対象とスキップ対象を分類する
    fix_candidates = []
    skipped_objects = []

    for obj in selected:
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

        object_name = obj.split("|")[-1]

        #メッシュShapeがあるかどうか
        if mesh_shapes:
            fix_candidates.append(object_name)
        else:
            skipped_objects.append(object_name)

    # 修正対象の一覧
    if fix_candidates:
        fix_list = "\n".join(
            "- " + name
            for name in fix_candidates
        )
    else:
        fix_list = "なし"

    # スキップ対象の一覧
    if skipped_objects:
        skipped_list = "\n".join(
            "- " + name
            for name in skipped_objects
        )
    else:
        skipped_list = "なし"


   # 確認ダイアログに表示する文章
    message = (
        "Transform自動修正の対象を確認してください。\n\n"
        "【修正対象（メッシュ）】\n"
        + fix_list
        + "\n\n【スキップ対象（メッシュShapeなし）】\n"
        + skipped_list
        + "\n\nTranslate・Rotate・Scaleを基準値に戻します。\n"
        "処理を続行しますか？"
    )

    answer = cmds.confirmDialog(
        title="Transform自動修正の確認",
        message=message,
        button=["実行する", "キャンセル"],
        defaultButton="キャンセル",
        cancelButton="キャンセル",
        dismissString="キャンセル",
        icon="warning"
    )

    # キャンセル時は修正処理へ進まない
    if answer != "実行する":
        message = "Transform自動修正をキャンセルしました。"

        print(message)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=message
        )

        return {
            "status": "CANCELLED",
            "message": message,
            "fix_results": [],
            "validation_results": [],
            "failed_results": [],
            "skipped_results": []
        }

    import importlib
    import fix_transforms

    # 自動修正モジュールを読み込み直す
    importlib.reload(fix_transforms)

    # Transformを自動修正する
    fix_results = fix_transforms.fix_selected_transforms()

    # 修正結果を表示する
    output_lines = ["=== Transform自動修正の結果 ==="]

    for result in fix_results:
        output_lines.append(
            "対象: {} | 状態: {} | 内容: {}".format(
                result.get("object"),
                result.get("status"),
                result.get("message")
            )
        )
    
        # 自動修正に失敗した結果を抽出する
    fix_errors = [
        result
        for result in fix_results
        if result.get("status") == "ERROR"
    ]

    # ERRORがあれば、再検証を実行せずに終了する
    if fix_errors:
        output_lines.append("")
        output_lines.append(
            "自動修正に失敗したため、再検証を中止しました。"
        )

        for result in fix_errors:
            output_lines.append(
                "対象: {} | エラー: {}".format(
                    result.get("object"),
                    result.get("message")
                )
            )

        output_text = "\n".join(output_lines)

        print(output_text)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=output_text
        )

        return {
            "fix_results": fix_results,
            "validation_results": [],
            "failed_results": fix_errors
        }

    # 自動修正に成功した結果を抽出する
    fix_successes = [
        result
        for result in fix_results
        if result.get("status") == "OK"
    ]

    # 修正対象外としてスキップされた結果を抽出する
    fix_skips = [
        result
        for result in fix_results
        if result.get("status") == "SKIP"
    ]

    # 修正に成功したメッシュが1つもない場合
    if not fix_successes:
        output_lines.append("")
        output_lines.append(
            "自動修正できるメッシュがないため、再検証を中止しました。"
        )

        output_text = "\n".join(output_lines)

        print(output_text)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=output_text
        )

        return {
            "fix_results": fix_results,
            "validation_results": [],
            "failed_results": []
        }

    # 自動修正に成功したオブジェクトだけを再検証する
    successful_objects = [
        result.get("object")
        for result in fix_successes
        if result.get("object")
    ]

    # 再検証の前に、対象をメッシュだけに絞る
    cmds.select(successful_objects, replace=True)

    try:
        validation_results = run_all_checks()

    finally:
        # 処理後に、元の選択状態へ戻す
        if selected:
            cmds.select(selected, replace=True)

        else:
            cmds.select(clear=True)


    # 検証結果を集計する
    failed_results = [
        result
        for result in validation_results
        if result.get("status") != "OK"
    ]

    # 検証結果の要約を作成する
    output_lines.append("")
    output_lines.append("=== 修正後の再検証結果 ===")
    output_lines.append(
        "検証件数: {}".format(len(validation_results))
    )
    output_lines.append(
        "要確認件数: {}".format(len(failed_results))
    )

    # 結果の詳細を追加する
    for result in validation_results:
        output_lines.append(
            "対象: {} | 検証: {} | 状態: {} | 内容: {}".format(
                result.get("object"),
                result.get("check"),
                result.get("status"),
                result.get("message")
            )
        )

    output_text = "\n".join(output_lines)

    print(output_text)

    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )

    # 呼び出し元でも結果を利用できるようにする
    return {
        "fix_results": fix_results,
        "validation_results": validation_results,
        "failed_results": failed_results
    }
          
def fix_history_and_revalidate(*args):
    """Construction Historyを修正し、修正後に再検証する。"""

    import importlib
    import fix_history
    
    importlib.reload(fix_history)

    # 元の選択状態を保存
    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    # 未選択の場合は終了
    if not selected:
        message = "オブジェクトが選択されていません。処理を中止しました。"

        print(message)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=message
        )

        return {
            "fix_results": [],
            "validation_results": [],
            "failed_results": [{
                "status": "ERROR",
                "message": message
            }]
        }

    # 選択対象の名前を取り出す
    selected_names = [
        obj.split("|")[-1]
        for obj in selected
    ]

    # 複数の選択オブジェクトを一覧確認
    object_list = "\n".join(
         "- " + name
         for name in selected_names
    )

    # メッシュとメッシュ以外を分類する
    history_candidates = []
    skipped_objects = []

    for obj in selected:
        shapes = cmds.listRelatives(
            obj,
            shapes=True,
            noIntermediate=True,
            fullPath=True
        ) or []

        mesh_shapes = [
            shapes
            for shape in shapes
            if cmds.nodeType(shape) == "mesh"
        ]

        object_name = obj.split("|")[-1]

        if not mesh_shapes:
            skipped_objects.append(
                (object_name,"メッシュShapeがありません")
            )
            continue

        # Construction Historyを調べる
        history = cmds.listHistory(
            obj,
            pruneDagObjects=True
        ) or []

        if not history:
            skipped_objects.append(
                (object_name,"Construction Historyがありません")
            )
            continue

        # 履歴ノードの種類を調べる
        history_types = {
            node: cmds.nodeType(node)
            for node in history
        }

        unsupported_nodes = [
            node
            for node, node_type in history_types.items()
            if node_type not in fix_history.ALLOWED_HISTORY_TYPES
        ]

        if unsupported_nodes:
            node_details = ",".join(
                "{} ({})".format(
                    node,
                    history_types[node]
                )
                for node in unsupported_nodes
            )

            skipped_objects.append(
                (
                    object_name,
                    "対応対象外の履歴:" + node_details
                )
            )
        else:
            history_candidates.append(object_name)

    # 削除対象の一覧
    if history_candidates:
        history_list = "\n".join(
            "- " + name
            for name in history_candidates
        )
    else:
        history_list = "なし"

    # スキップ対象と理由の一覧
    if skipped_objects:
        skipped_list = "\n".join(
            "- {}：{}".format(name, reason)
            for name, reason in skipped_objects
        )
    else:
        skipped_list = "なし"

    # 確認ダイアログに表示する文章
    message = (
        "Construction Historyの処理対象を確認してください。\n\n"
        "【削除対象】\n"
        + history_list
        + "\n\n【スキップ対象】\n"
        + skipped_list
        + "\n\n削除対象のメッシュからConstruction Historyを削除します。\n"
        "削除後は、モデリング操作の履歴を編集できなくなります。\n"
        "続行しますか？"
    )

    # Construction History削除の確認ダイアログ
    answer = cmds.confirmDialog(
        title="Construction Historyの削除確認",
        message=message,
        button=["実行する","キャンセル"],
        defaultButton="キャンセル",
        cancelButton="キャンセル",
        dismissString="キャンセル",
        icon="warning"
    )

    # キャンセルされた場合は処理を終了
    if answer != "実行する":
        message = "Construction HIstoryの削除をキャンセルしました。"

        print(message)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=message
        )

        return {
            "status": "CANCELLED",
            "message": message,
            "fix_results": [],
            "validation_results": [],
            "failed_results": [],
            "skipped_results": []
        }


    #  Construction Historyを修正
    fix_results = fix_history.fix_selected_history()

    output_lines = ["=== Construction History自動修正の結果 ==="]

    for result in fix_results:
        output_lines.append(
            "対象: {} | 状態: {} | 内容: {}".format(
                result.get("object"),
                result.get("status"),
                result.get("message")
            )
        )

        # 詳細情報がある場合は、ノード名と種類も表示する
        details = result.get("details",[])

        for detail in details:
            output_lines.append(
                "  対象ノード: {} | 種類: {}".format(
                    detail.get("node"),
                    detail.get("type")
                )
            )

    #  修正に失敗した結果を抽出
    fix_errors = [
        result
        for result in fix_results
        if result.get("status") == "ERROR"
    ]

    # ERRORがあれば再検証を中止
    if fix_errors:
        output_lines.append("")
        output_lines.append(
            "履歴の修正に失敗したため、再検証を中止しました。"
        )

        output_text = "\n".join(output_lines)
        print(output_text)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=output_text
        )

        return {
            "fix_results": fix_results,
            "validation_results": [],
            "failed_results": fix_errors
        }

    #  修正に成功した結果を抽出
    fix_successes = [
        result
        for result in fix_results
        if result.get("status") == "OK"
        and result.get("object")
    ]

    fix_skips = [
        result
        for result in fix_results
        if result.get("status") == "SKIP"
    ]

    # 修正に成功したメッシュがない場合は終了
    if not fix_successes:
        output_lines.append("")
        output_lines.append(
            "自動修正できるメッシュがないため、再検証を中止しました。"
        )

        output_text = "\n".join(output_lines)
        print(output_text)

        cmds.scrollField(
            OUTPUT_FIELD,
            edit=True,
            text=output_text
        )

        return {
            "fix_results": fix_results,
            "validation_results": [],
            "failed_results": [],
            "skipped_results": fix_skips
        }

    #  修正成功したメッシュだけを再検証する
    successful_objects = [
        result["object"]
        for result in fix_successes
    ]

    try:
        cmds.select(successful_objects, replace=True)
        validation_results = run_all_checks()

    finally:
        # 元の選択状態に戻す
        cmds.select(selected, replace=True)

    #  再検証結果を集計
    failed_results = [
        result
        for result in validation_results
        if result.get("status") != "OK"
    ]

    output_lines.append("")
    output_lines.append("=== 修正後の再検証結果 ===")
    output_lines.append(
        "検証件数: {}".format(len(validation_results))
    )
    output_lines.append(
        "要確認件数: {}".format(len(failed_results))
    )

    for result in validation_results:
        output_lines.append(
            "対象: {} | 検証: {} | 状態: {} | 内容: {}".format(
                result.get("object"),
                result.get("check"),
                result.get("status"),
                result.get("message")
            )
        )

    output_text = "\n".join(output_lines)
    print(output_text)

    cmds.scrollField(
        OUTPUT_FIELD,
        edit=True,
        text=output_text
    )

    return {
        "fix_results": fix_results,
        "validation_results": validation_results,
        "failed_results": failed_results,
        "skipped_results": fix_skips
    }




def show_ui():
    """検証ツールのウィンドウを表示する。"""

    # 同名のウィンドウがあれば閉じる
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    # ウィンドウを作成する
    window = cmds.window(
        WINDOW_NAME,
        title="Maya → Unreal 検証ツール",
        sizeable=True,
        widthHeight=(520, 720)
    )

    # 全体をスクロール可能にする
    cmds.scrollLayout(
        childResizable=True
    )

    # 全体の縦方向レイアウト
    cmds.columnLayout(
        adjustableColumn=True,
        rowSpacing=10
    )

    # ツールの説明
    cmds.text(
        label="MayaからUnreal Engineへの出力前チェックツール",
        align="left",
        height=30
    )

    # ==================================
    # 01. 検証
    # ==================================

    cmds.frameLayout(
        label="01 | VALIDATION - 検証",
        collapsable=True,
        collapse=False,
        marginWidth=8,
        marginHeight=6
    )

    cmds.text(
        label="選択したメッシュの問題を検出します。",
        align="left"
    )

    cmds.button(
        label="命名規則チェック",
        height=35,
        command=run_name_check
    )

    cmds.button(
        label="Transformチェック",
        height=35,
        command=run_transform_check
    )

    cmds.button(
        label="Cunstruction Historyチェック",
        height=35,
        command=run_history_check
    )

    cmds.button(
        label="N-gonチェック",
        height=35,
        command=run_ngon_check
    )

    cmds.button(
        label="UVチェック",
        height=35,
        command=run_uv_check
    )

    cmds.button(
        label="全項目チェック",
        height=40,
        command=run_all_checks
    )

    # columnLayoutを抜ける
    cmds.setParent("..")

    # frameLayoutを抜ける
    cmds.setParent("..")

    # ==================================
    # 02. 自動修正
    # ==================================

    cmds.frameLayout(
        label="02 | AUTO FIX - 自動修正",
        collapsable=True,
        collapse=False,
        marginWidth=8,
        marginHeight=6
    )

    cmds.columnLayout(
        adjustableColumn=True,
        rowSpacing=5
    )

    cmds.text(
        label="検出された問題を修正して再検証します。",
        align="left"
    )

    cmds.button(
        label="Transform自動修正して再検証",
        height=40,
        command=fix_transforms_and_revalidate
    )

    cmds.button(
        label="Construction History自動修正して再検証",
        height=40,
        command=fix_history_and_revalidate
    )

    cmds.setParent("..")
    cmds.setParent("..")

    # ==================================
    # 03. FBX書き出し
    # ==================================

    cmds.frameLayout(
        label="03 | EXPORT - FBX書き出し",
        collapsable=True,
        collapse=False,
        marginWidth=8,
        marginHeight=6
    )

    cmds.columnLayout(
        adjustableColumn=True,
        rowSpacing=5
    )

    cmds.text(
        label="検証に合格したメッシュをFBXで出力します。",
        align="left"
    )

    cmds.button(
        label="検証してFBX書き出し",
        height=45,
        command=validate_and_export
    )

    cmds.setParent("..")
    cmds.setParent("..")

    # ==================================
    # 04. 実行結果
    # ==================================

    cmds.frameLayout(
        label="04 | RESULT - 実行結果",
        collapsable=True,
        collapse=False,
        marginWidth=8,
        marginHeight=6
    )

    cmds.columnLayout(
        adjustableColumn=True,
        rowSpacing=5
    )

    global OUTPUT_FIELD

    OUTPUT_FIELD = cmds.scrollField(
        editable=False,
        wordWrap=True,
        text="実行結果がここに表示されます。",
        height=180
    )

    cmds.setParent("..")
    cmds.setParent("..")

    # ウィンドウを表示する
    cmds.showWindow(window)

show_ui()