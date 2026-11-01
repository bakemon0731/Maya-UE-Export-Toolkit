import os
import sys
import importlib

import maya.cmds as cmds

from PySide6 import QtCore, QtWidgets
from maya import OpenMayaUI as omui
from shiboken6 import wrapInstance


# =========================================
# 01. パス設定
# =========================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__))

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


# =========================================
# 02. モジュール読み込み
# =========================================

import validate_names
import validate_transforms
import validate_history
import validate_ngons
import validate_uvs

import fix_transforms
import fix_history
import fix_names

import export_fbx


# =========================================
# 03. ウィンドウ管理
# =========================================

WINDOW = None
WINDOW_NAME = "ExportToolkitTestWindow"


# =========================================
# 04. 個別検証
# =========================================

def run_validation(result_view, check_function, check_title):

    try:

        results = check_function() or []

        if not results:

            result_view.setPlainText(
                "検証結果がありません。\n"
                "オブジェクトを選択してください。"
            )

            return []

        lines = []

        lines.append(
            "===== {}チェック結果 =====".format(check_title)
        )

        lines.append("")

        for result in results:

            lines.append(
                "オブジェクト: {}".format(
                    result.get("object", "不明")
                )
            )

            lines.append(
                "結果: {}".format(
                    result.get("status", "不明")
                )
            )

            lines.append(
                "説明: {}".format(
                    result.get("message", "")
                )
            )

            details = result.get("details", [])

            if details:

                lines.append("追加情報:")

                for detail in details:

                    if isinstance(detail, dict):

                        for key, value in detail.items():

                            lines.append(
                                " {}: {}".format(key, value)
                            )

                    else:

                        lines.append(" " + str(detail))

            lines.append("")

        output_text = "\n".join(lines)

        result_view.setPlainText(output_text)

        print(output_text)

        return results

    except Exception as error:

        message = "検証エラー: {}".format(error)

        result_view.setPlainText(message)

        print(message)

        return []


# =========================================
# 05. 全項目チェック
# =========================================

def run_all_validations(result_view, validation_checks, display=True):

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    if not selected:

        if display:

            result_view.setPlainText(
                "オブジェクトを選択してください。"
            )

        return {
            "results": [],
            "errors": []
        }

    all_results = []
    errors = []

    # 5種類の検証を実行
    for label, check_function in validation_checks:

        try:

            results = check_function() or []

            all_results.extend(results)

        except Exception as caught_exception:

            errors.append({
                "check": label,
                "type": type(caught_exception).__name__,
                "message": str(caught_exception)
            })

    # オブジェクト単位で結果を整理
    object_results = {}

    for result in all_results:

        object_name = result.get("object") or "不明"

        if object_name not in object_results:

            object_results[object_name] = []

        object_results[object_name].append(result)

    lines = []

    lines.append("===== 全項目チェック結果 =====")
    lines.append("")

    # 検証結果を表示
    for object_name, results in object_results.items():

        lines.append(
            "オブジェクト: {}".format(object_name)
        )

        lines.append("")

        for result in results:

            lines.append(
                "[{}] {}".format(
                    result.get("status", "不明"),
                    result.get("check", "不明")
                )
            )

            lines.append(
                " 説明: {}".format(
                    result.get("message", "")
                )
            )

            details = result.get("details", [])

            if details:

                lines.append(" 追加情報:")

                for detail in details:

                    if isinstance(detail, dict):

                        for key, value in detail.items():

                            lines.append(
                                "  {}: {}".format(key, value)
                            )

                    else:

                        lines.append(
                            "  " + str(detail)
                        )

            lines.append("")

    # ステータス集計
    ok_count = sum(
        1 for result in all_results
        if result.get("status") == "OK"
    )

    ng_count = sum(
        1 for result in all_results
        if result.get("status") == "NG"
    )

    skip_count = sum(
        1 for result in all_results
        if result.get("status") == "SKIP"
    )

    result_error_count = sum(
        1 for result in all_results
        if result.get("status") == "ERROR"
    )

    exception_count = len(errors)

    error_count = result_error_count + exception_count

    # 実行サマリー
    lines.append("===== 実行サマリー =====")

    lines.append(
        "検証対象オブジェクト数: {}".format(len(selected))
    )

    lines.append(
        "取得した検証結果数: {}".format(len(all_results))
    )

    lines.append("OK件数: {}".format(ok_count))
    lines.append("NG件数: {}".format(ng_count))
    lines.append("SKIP件数: {}".format(skip_count))
    lines.append("ERROR件数: {}".format(error_count))
    lines.append("例外が発生した数: {}".format(exception_count))

    # エラー詳細
    if errors:

        lines.append("")
        lines.append("===== エラー詳細 =====")

        for error_info in errors:

            lines.append(
                "検証項目: {}".format(error_info["check"])
            )

            lines.append(
                "エラーの種類: {}".format(error_info["type"])
            )

            lines.append(
                "エラーの詳細: {}".format(error_info["message"])
            )

            lines.append("")

    output_text = "\n".join(lines)

    if display:

        result_view.setPlainText(output_text)

        print(output_text)

    return {
        "results": all_results,
        "errors": errors
    }


# =========================================
# 06. 確認ダイアログ
# =========================================

def ask_confirmation(parent, title, message):

    dialog = QtWidgets.QMessageBox(parent)

    dialog.setIcon(
        QtWidgets.QMessageBox.Icon.Warning
    )

    dialog.setWindowTitle(title)

    dialog.setText(message)

    dialog.setStandardButtons(
        QtWidgets.QMessageBox.StandardButton.Yes
        | QtWidgets.QMessageBox.StandardButton.No
    )

    dialog.button(
        QtWidgets.QMessageBox.StandardButton.Yes
    ).setText("実行する")

    dialog.button(
        QtWidgets.QMessageBox.StandardButton.No
    ).setText("キャンセル")

    dialog.setDefaultButton(
        QtWidgets.QMessageBox.StandardButton.No
    )

    answer = dialog.exec()

    return (
        answer
        == QtWidgets.QMessageBox.StandardButton.Yes
    )


# =========================================
# 07. 自動修正結果の表示
# =========================================

def append_fix_results(lines, fix_results):

    for result in fix_results:

        object_name = result.get("object", "不明")

        if isinstance(object_name, str):

            object_name = object_name.split("|")[-1]

        lines.append(
            "対象: {}".format(object_name)
        )

        lines.append(
            "状態: {}".format(
                result.get("status", "不明")
            )
        )

        lines.append(
            "内容: {}".format(
                result.get("message", "")
            )
        )

        details = result.get("details", [])

        if details:

            lines.append("追加情報:")

            for detail in details:

                if isinstance(detail, dict):

                    for key, value in detail.items():

                        lines.append(
                            " {}: {}".format(key, value)
                        )

                else:

                    lines.append(" " + str(detail))

        lines.append("")


# =========================================
# 08. 修正後の再検証
# =========================================

def finish_fix_and_revalidate(
    result_view,
    validation_checks,
    selected,
    fix_results,
    operation_title
):

    lines = []

    lines.append(
        "===== {}の結果 =====".format(operation_title)
    )

    if not fix_results:

        lines.append("修正結果がありません。")

        result_view.setPlainText(
            "\n".join(lines)
        )

        return

    append_fix_results(lines, fix_results)

    # =====================================
    # ERRORを抽出
    # =====================================

    fix_errors = [
        result
        for result in fix_results
        if result.get("status") == "ERROR"
    ]

    if fix_errors:

        lines.append(
            "修正エラーが発生したため、再検証を中止しました。"
        )

        result_view.setPlainText(
            "\n".join(lines)
        )

        return

    # =====================================
    # 修正に成功したオブジェクトを取得
    # =====================================

    fix_successes = [
        result
        for result in fix_results
        if result.get("status") == "OK"
        and result.get("object")
    ]

    successful_objects = [
        result.get("object")
        for result in fix_successes
    ]

    if not successful_objects:

        lines.append(
            "修正に成功したメッシュがないため、再検証を中止しました。"
        )

        result_view.setPlainText(
            "\n".join(lines)
        )

        return

    # =====================================
    # 修正前・修正後のパスを対応付ける
    # =====================================

    selection_mapping = {}

    for result in fix_results:

        details = result.get("details", [])

        for detail in details:

            if isinstance(detail, dict):

                old_path = detail.get("変更前パス")
                new_path = detail.get("変更後パス")

                if old_path and new_path:

                    selection_mapping[old_path] = new_path

    # 修正前のパスを修正後のパスに置き換える
    selection_to_restore = [
        selection_mapping.get(obj, obj)
        for obj in selected
    ]

    # =====================================
    # 修正後の再検証
    # =====================================

    validation_data = None

    selection_restore_error = None

    try:

        cmds.select(
            successful_objects,
            replace=True
        )

        validation_data = run_all_validations(
            result_view,
            validation_checks,
            display=False
        )

    except Exception as error:

        lines.append("")
        lines.append(
            "再検証中にエラーが発生しました: {}".format(error)
        )

    finally:

        # =================================
        # 元の選択状態を復元
        # =================================

        try:

            valid_selection = [
                obj
                for obj in selection_to_restore
                if cmds.objExists(obj)
            ]

            if valid_selection:

                cmds.select(
                    valid_selection,
                    replace=True
                )

            else:

                cmds.select(clear=True)

        except Exception as error:

            selection_restore_error = str(error)

    # =====================================
    # 再検証結果が取得できなかった場合
    # =====================================

    if validation_data is None:

        if selection_restore_error:

            lines.append(
                "選択状態の復元エラー: {}".format(
                    selection_restore_error
                )
            )

        result_view.setPlainText(
            "\n".join(lines)
        )

        print("\n".join(lines))

        return

    # =====================================
    # 再検証結果の取得
    # =====================================

    validation_results = validation_data["results"]

    validation_errors = validation_data["errors"]

    failed_results = [
        result
        for result in validation_results
        if result.get("status") != "OK"
    ]

    lines.append("")
    lines.append("===== 修正後の再検証結果 =====")

    lines.append(
        "検証件数: {}".format(
            len(validation_results)
        )
    )

    lines.append(
        "要確認件数: {}".format(
            len(failed_results)
        )
    )

    # =====================================
    # 個別の検証結果
    # =====================================

    for result in validation_results:

        object_name = result.get("object", "不明")

        if isinstance(object_name, str):

            object_name = object_name.split("|")[-1]

        lines.append(
            "対象: {} | 検証: {} | 状態: {} | 内容: {}".format(
                object_name,
                result.get("check"),
                result.get("status"),
                result.get("message")
            )
        )

    # =====================================
    # 再検証エラーの表示
    # =====================================

    if validation_errors:

        lines.append("")
        lines.append("===== 再検証エラー =====")

        for error_info in validation_errors:

            lines.append(
                "検証項目: {}".format(
                    error_info["check"]
                )
            )

            lines.append(
                "種類: {}".format(
                    error_info["type"]
                )
            )

            lines.append(
                "内容: {}".format(
                    error_info["message"]
                )
            )

    # =====================================
    # 選択状態の復元エラー
    # =====================================

    if selection_restore_error:

        lines.append("")
        lines.append(
            "選択状態の復元エラー: {}".format(
                selection_restore_error
            )
        )

    # =====================================
    # 最終結果表示
    # =====================================

    output_text = "\n".join(lines)

    result_view.setPlainText(output_text)

    print(output_text)

# =========================================
# 09. 命名規則自動修正
# =========================================

def run_name_auto_fix(
    result_view,
    validation_checks,
    parent
):

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    if not selected:

        result_view.setPlainText(
            "オブジェクトが選択されていません。\n"
            "命名規則の自動修正を中止しました。"
        )

        return

    fix_candidates = []
    skipped_objects = []

    for obj in selected:

        object_name = obj.split("|")[-1]

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

        if not mesh_shapes:

            skipped_objects.append(object_name)

            continue

        if not object_name.startswith("SM_"):

            fix_candidates.append(object_name)

    if not fix_candidates:

        result_view.setPlainText(
            "命名規則の修正対象がありません。\n"
            "すべてのメッシュがSM_で始まっています。"
        )

        return

    fix_list = "\n".join(
        "- " + name
        for name in fix_candidates
    )

    skipped_list = "\n".join(
        "- " + name
        for name in skipped_objects
    ) if skipped_objects else "なし"

    message = (
        "命名規則の自動修正対象を確認してください。\n\n"
        "【修正対象】\n"
        + fix_list
        + "\n\n【スキップ対象】\n"
        + skipped_list
        + "\n\n対象のオブジェクト名の先頭にSM_を追加します。\n\n"
        "続行しますか？"
    )

    confirmed = ask_confirmation(
        parent,
        "命名規則自動修正の確認",
        message
    )

    if not confirmed:

        result_view.setPlainText(
            "命名規則の自動修正をキャンセルしました。"
        )

        return

    try:

        importlib.reload(fix_names)

        fix_results = fix_names.fix_selected_names()

        finish_fix_and_revalidate(
            result_view,
            validation_checks,
            selected,
            fix_results,
            "命名規則自動修正"
        )

    except Exception as error:

        message = (
            "命名規則の自動修正中にエラーが発生しました: {}".format(
                error
            )
        )

        result_view.setPlainText(message)

        print(message)



# =========================================
# 09. Transform自動修正
# =========================================

def run_transform_auto_fix(
    result_view,
    validation_checks,
    parent
):

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    if not selected:

        result_view.setPlainText(
            "オブジェクトが選択されていません。\n"
            "Transform自動修正を中止しました。"
        )

        return

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

        if mesh_shapes:

            fix_candidates.append(object_name)

        else:

            skipped_objects.append(object_name)

    if not fix_candidates:

        lines = [
            "Transform自動修正の対象となるメッシュがありません。",
            "",
            "スキップ対象:"
        ]

        for name in skipped_objects:
            lines.append("- " + name)

        result_view.setPlainText(
            "\n".join(lines)
        )

        return

    fix_list = "\n".join(
        "- " + name
        for name in fix_candidates
    )

    skipped_list = "\n".join(
        "- " + name
        for name in skipped_objects
    ) if skipped_objects else "なし"

    message = (
        "Transform自動修正の対象を確認してください。\n\n"
        "【修正対象（メッシュ）】\n"
        + fix_list
        + "\n\n【スキップ対象（メッシュShapeなし）】\n"
        + skipped_list
        + "\n\nTranslate・Rotate・Scaleを基準値に戻します。\n"
        "ワールド境界を確認しながら処理します。\n\n"
        "続行しますか？"
    )

    confirmed = ask_confirmation(
        parent,
        "Transform自動修正の確認",
        message
    )

    if not confirmed:

        result_view.setPlainText(
            "Transform自動修正をキャンセルしました。"
        )

        return

    try:

        importlib.reload(fix_transforms)

        fix_results = fix_transforms.fix_selected_transforms()

        finish_fix_and_revalidate(
            result_view,
            validation_checks,
            selected,
            fix_results,
            "Transform自動修正"
        )

    except Exception as error:

        message = (
            "Transform自動修正中にエラーが発生しました: {}".format(
                error
            )
        )

        result_view.setPlainText(message)

        print(message)


# =========================================
# 10. Construction History自動修正
# =========================================

def run_history_auto_fix(
    result_view,
    validation_checks,
    parent
):

    importlib.reload(fix_history)

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    if not selected:

        result_view.setPlainText(
            "オブジェクトが選択されていません。\n"
            "Construction History削除を中止しました。"
        )

        return

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
            shape
            for shape in shapes
            if cmds.nodeType(shape) == "mesh"
        ]

        object_name = obj.split("|")[-1]

        if not mesh_shapes:

            skipped_objects.append(
                (object_name, "メッシュShapeがありません")
            )

            continue

        history = cmds.listHistory(
            obj,
            pruneDagObjects=True
        ) or []

        if not history:

            skipped_objects.append(
                (object_name, "Construction Historyがありません")
            )

            continue

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

            node_details = ", ".join(
                "{} ({})".format(
                    node,
                    history_types[node]
                )
                for node in unsupported_nodes
            )

            skipped_objects.append(
                (
                    object_name,
                    "対応対象外の履歴: " + node_details
                )
            )

        else:

            history_candidates.append(object_name)

    if not history_candidates:

        lines = [
            "Construction Historyの削除対象がありません。",
            "",
            "スキップ対象:"
        ]

        for name, reason in skipped_objects:

            lines.append(
                "- {}：{}".format(name, reason)
            )

        result_view.setPlainText(
            "\n".join(lines)
        )

        return

    history_list = "\n".join(
        "- " + name
        for name in history_candidates
    )

    skipped_list = "\n".join(
        "- {}：{}".format(name, reason)
        for name, reason in skipped_objects
    ) if skipped_objects else "なし"

    message = (
        "Construction Historyの処理対象を確認してください。\n\n"
        "【削除対象】\n"
        + history_list
        + "\n\n【スキップ対象】\n"
        + skipped_list
        + "\n\n削除対象のメッシュからConstruction Historyを削除します。\n"
        "削除後はモデリング操作の履歴を編集できなくなります。\n\n"
        "続行しますか？"
    )

    confirmed = ask_confirmation(
        parent,
        "Construction History削除の確認",
        message
    )

    if not confirmed:

        result_view.setPlainText(
            "Construction Historyの削除をキャンセルしました。"
        )

        return

    try:

        fix_results = fix_history.fix_selected_history()

        finish_fix_and_revalidate(
            result_view,
            validation_checks,
            selected,
            fix_results,
            "Construction History自動修正"
        )

    except Exception as error:

        message = (
            "Construction History削除中にエラーが発生しました: {}".format(
                error
            )
        )

        result_view.setPlainText(message)

        print(message)


# =========================================
# 11. FBX書き出し
# =========================================

def run_validate_and_export(
    result_view,
    validation_checks
):
    """全項目を検証し、すべてOKの場合だけFBXを書き出す。"""

    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    if not selected:

        result_view.setPlainText(
            "オブジェクトを選択してください。\n"
            "FBX書き出しを中止しました。"
        )

        return

    # まず全項目の検証を実行
    validation_data = run_all_validations(
        result_view,
        validation_checks,
        display=True
    )

    results = validation_data["results"]
    errors = validation_data["errors"]

    # 検証結果が取得できなかった場合
    if not results:

        result_view.setPlainText(
            "検証結果がありません。\n"
            "FBX書き出しを中止しました。"
        )

        return

    # OK以外の結果を抽出
    failed_results = [
        result
        for result in results
        if result.get("status") != "OK"
    ]

    # NG・SKIP・ERROR・例外があれば中止
    if failed_results or errors:

        lines = [
            result_view.toPlainText(),
            "",
            "===== FBX書き出し判定 =====",
            "検証に問題があるため、FBX書き出しを中止しました。",
            ""
        ]

        for result in failed_results:

            lines.append(
                "対象: {} | 検証: {} | 状態: {} | 内容: {}".format(
                    result.get("object", "不明"),
                    result.get("check", "不明"),
                    result.get("status", "不明"),
                    result.get("message", "")
                )
            )

        for error_info in errors:

            lines.append(
                "例外: {} | {}".format(
                    error_info["check"],
                    error_info["message"]
                )
            )

        output_text = "\n".join(lines)

        result_view.setPlainText(output_text)

        print(output_text)

        return

    # すべてOKの場合だけFBX書き出し
    try:

        importlib.reload(export_fbx)

        export_result = export_fbx.export_selected_fbx()

        status = export_result.get("status")

        lines = [
            "===== FBX書き出し結果 ====="
        ]

        if status == "OK":

            lines.append("すべての検証に合格しました。")
            lines.append("FBX書き出しが完了しました。")

            lines.append(
                "保存先: {}".format(
                    export_result.get("file_path", "不明")
                )
            )

        elif status == "CANCELLED":

            lines.append("検証はすべてOKです。")
            lines.append("FBX書き出しはキャンセルされました。")

        else:

            lines.append("検証はすべてOKです。")
            lines.append("FBX書き出しに失敗しました。")

            lines.append(
                "エラー: {}".format(
                    export_result.get("message", "詳細不明")
                )
            )

        output_text = "\n".join(lines)

        result_view.setPlainText(output_text)

        print(output_text)

        return export_result

    except Exception as error:

        message = (
            "FBX書き出し中にエラーが発生しました: {}".format(
                error
            )
        )

        result_view.setPlainText(message)

        print(message)


# =========================================
# 12. UI作成
# =========================================

def show_ui():

    global WINDOW

    # Mayaのメインウィンドウ
    maya_ptr = omui.MQtUtil.mainWindow()

    maya_window = wrapInstance(
        int(maya_ptr),
        QtWidgets.QWidget
    )

    # 古いウィンドウを削除
    old_windows = maya_window.findChildren(
        QtWidgets.QWidget,
        WINDOW_NAME
    )

    for old_window in old_windows:

        old_window.close()
        old_window.deleteLater()

    WINDOW = None

    # 全モジュールを再読み込み
    importlib.reload(validate_names)
    importlib.reload(validate_transforms)
    importlib.reload(validate_history)
    importlib.reload(validate_ngons)
    importlib.reload(validate_uvs)

    importlib.reload(fix_transforms)
    importlib.reload(fix_history)
    importlib.reload(fix_names)
    importlib.reload(export_fbx)

    # 検証関数一覧
    validation_checks = [

        ("命名規則", validate_names.validate_selected_names),

        ("Transform", validate_transforms.validate_selected_transforms),

        ("Construction History", validate_history.validate_selected_history),

        ("N-gon", validate_ngons.validate_selected_ngons),

        ("UV", validate_uvs.validate_selected_uvs)

    ]

    # =====================================
    # ウィンドウ
    # =====================================

    WINDOW = QtWidgets.QWidget(maya_window)

    WINDOW.setObjectName(WINDOW_NAME)

    WINDOW.setWindowTitle(
        "Maya → Unreal Export Toolkit"
    )

    WINDOW.setWindowFlags(
        QtCore.Qt.Window
    )

    WINDOW.resize(540, 900)

    # =====================================
    # メインレイアウト
    # =====================================

    main_layout = QtWidgets.QVBoxLayout(WINDOW)

    main_layout.setContentsMargins(
        24, 24, 24, 24
    )

    main_layout.setSpacing(16)

    # =====================================
    # HEADER
    # =====================================

    eyebrow = QtWidgets.QLabel(
        "MAYA / UNREAL ENGINE"
    )

    eyebrow.setObjectName("eyebrowLabel")

    title = QtWidgets.QLabel(
        "EXPORT TOOLKIT"
    )

    title.setObjectName("titleLabel")

    description = QtWidgets.QLabel(
        "Asset Validation & Export System"
    )

    description.setObjectName("descriptionLabel")

    main_layout.addWidget(eyebrow)
    main_layout.addWidget(title)
    main_layout.addWidget(description)

    # =====================================
    # 01. 項目検証機能
    # =====================================

    validation_group = QtWidgets.QGroupBox(
        "01 / 項目検証機能"
    )

    validation_layout = QtWidgets.QGridLayout(
        validation_group
    )

    validation_layout.setContentsMargins(
        14, 24, 14, 14
    )

    validation_layout.setSpacing(10)

    # 全項目チェック
    all_button = QtWidgets.QPushButton(
        "全項目一括チェック"
    )

    all_button.setObjectName("allCheckButton")

    all_button.clicked.connect(
        lambda checked=False:
            run_all_validations(
                result_view,
                validation_checks
            )
    )

    validation_layout.addWidget(
        all_button,
        0, 0, 1, 2
    )

    # 個別検証ボタン
    for index, (label, check_function) in enumerate(validation_checks):

        button = QtWidgets.QPushButton(label)

        button.setObjectName("checkButton")

        button.clicked.connect(
            lambda checked=False,
            func=check_function,
            check_title=label:
                run_validation(
                    result_view,
                    func,
                    check_title
                )
        )

        row = 1 + index // 2
        column = index % 2

        validation_layout.addWidget(
            button,
            row,
            column
        )

    main_layout.addWidget(validation_group)

    # =====================================
    # 02. 自動修正機能
    # =====================================

    auto_fix_group = QtWidgets.QGroupBox(
        "02 / 自動修正機能"
    )

    auto_fix_layout = QtWidgets.QGridLayout(
        auto_fix_group
    )

    auto_fix_layout.setContentsMargins(
        14, 24, 14, 14
    )

    auto_fix_layout.setSpacing(10)

    # Transform自動修正
    transform_fix_button = QtWidgets.QPushButton(
        "Transform自動修正・再検証"
    )

    transform_fix_button.setObjectName(
        "fixButton"
    )

    transform_fix_button.clicked.connect(
        lambda checked=False:
            run_transform_auto_fix(
                result_view,
                validation_checks,
                WINDOW
            )
    )

    # Construction History自動修正
    history_fix_button = QtWidgets.QPushButton(
        "Construction History削除・再検証"
    )

    history_fix_button.setObjectName(
        "fixButton"
    )

    history_fix_button.clicked.connect(
        lambda checked=False:
            run_history_auto_fix(
                result_view,
                validation_checks,
                WINDOW
            )
    )

    # 命名規則自動修正
    name_fix_button = QtWidgets.QPushButton(
        "命名規則自動修正・再検証"
    )

    name_fix_button.setObjectName(
        "fixButton"
    )

    name_fix_button.clicked.connect(
        lambda checked=False:
            run_name_auto_fix(
                result_view,
                validation_checks,
                WINDOW
            )
    )

    auto_fix_layout.addWidget(
        transform_fix_button,
        0, 0
    )

    auto_fix_layout.addWidget(
        history_fix_button,
        0, 1
    )

    auto_fix_layout.addWidget(
        name_fix_button,
        1, 0, 1, 2
    )

    main_layout.addWidget(auto_fix_group)

    # =====================================
    # 03. FBX書き出し
    # =====================================

    export_group = QtWidgets.QGroupBox(
        "03 / FBX書き出し"
    )

    export_layout = QtWidgets.QVBoxLayout(
        export_group
    )

    export_layout.setContentsMargins(
        14, 24, 14, 14
    )

    export_button = QtWidgets.QPushButton(
        "検証してFBX書き出し"
    )

    export_button.setObjectName(
        "exportButton"
    )

    export_button.clicked.connect(
        lambda checked=False:
            run_validate_and_export(
                result_view,
                validation_checks
            )
    )

    export_layout.addWidget(export_button)

    main_layout.addWidget(export_group)

    # =====================================
    # 04. 検証結果表示
    # =====================================

    report_group = QtWidgets.QGroupBox(
        "04 / 検証結果表示"
    )

    report_layout = QtWidgets.QVBoxLayout(
        report_group
    )

    report_layout.setContentsMargins(
        14, 24, 14, 14
    )

    result_view = QtWidgets.QPlainTextEdit()

    result_view.setObjectName("resultView")

    result_view.setReadOnly(True)

    result_view.setPlaceholderText(
        "検証・自動修正・FBX書き出しの結果がここに表示されます。"
    )

    report_layout.addWidget(result_view)

    main_layout.addWidget(
        report_group,
        1
    )

    # =====================================
    # 05. デザイン
    # =====================================

    WINDOW.setStyleSheet("""

        QWidget#ExportToolkitTestWindow {
            background-color: #171D27;
        }

        QLabel#eyebrowLabel {
            color: #68C8DC;
            font-size: 11px;
            font-weight: bold;
        }

        QLabel#titleLabel {
            color: #F0F3F7;
            font-size: 27px;
            font-weight: bold;
        }

        QLabel#descriptionLabel {
            color: #AAB6C5;
            font-size: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #354253;
        }

        QGroupBox {
            color: #68C8DC;
            font-size: 12px;
            font-weight: bold;
            border: 1px solid #354253;
            border-radius: 8px;
            margin-top: 12px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 6px;
            background-color: #171D27;
        }

        QPushButton#allCheckButton {
            background-color: #24647A;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: bold;
            padding: 14px;
            border: none;
            border-radius: 6px;
        }

        QPushButton#allCheckButton:hover {
            background-color: #32849C;
        }

        QPushButton#checkButton {
            background-color: #252F3C;
            color: #D6E1EA;
            font-size: 12px;
            padding: 12px 8px;
            border: 1px solid #354253;
            border-radius: 6px;
        }

        QPushButton#checkButton:hover {
            background-color: #354759;
            border: 1px solid #68C8DC;
        }

        QPushButton#fixButton {
            background-color: #35483F;
            color: #D7E9DF;
            font-size: 12px;
            font-weight: bold;
            padding: 12px 8px;
            border: 1px solid #4E7561;
            border-radius: 6px;
        }

        QPushButton#fixButton:hover {
            background-color: #416A55;
            border: 1px solid #72B993;
        }

        QPushButton#fixButton:pressed {
            background-color: #294638;
        }

        QPushButton#exportButton {
            background-color: #24647A;
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
            padding: 15px;
            border: none;
            border-radius: 6px;
        }

        QPushButton#exportButton:hover {
            background-color: #32849C;
        }

        QPushButton#exportButton:pressed {
            background-color: #19495C;
        }

        QPlainTextEdit#resultView {
            background-color: #222B35;
            color: #D6E1EA;
            font-size: 12px;
            border: none;
            border-radius: 5px;
            padding: 10px;
        }

    """)

    WINDOW.show()
