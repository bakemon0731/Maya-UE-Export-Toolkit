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
        widthHeight=(480, 400)
    )

    # 縦方向にUI部品を配置する
    cmds.columnLayout(
        adjustableColumn=True,
        rowSpacing=8
    )

    cmds.text(
        label="選択したオブジェクトの命名規則を検証します。",
        align="left"
    )

    # 検証結果の表示欄
    global OUTPUT_FIELD

    OUTPUT_FIELD = cmds.scrollField(
        editable=False,
        wordWrap=True,
        text="オブジェクトを選択して、チェックボタンを押してください。"
    )

    # チェックボタン
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
        label = "Construction Historyチェック",
        height=35,
        command=run_history_check
    )

    cmds.button(
        label = "N-gonチェック",
        height=35,
        command=run_ngon_check
    )

    cmds.button(
        label = "UVチェック",
        height= 35,
        command=run_uv_check
    )

    cmds.button(
        label = "全項目チェック",
        height=40,
        command=run_all_checks
    )

    # ウィンドウを表示する
    cmds.showWindow(window)


show_ui()