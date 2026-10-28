import os
import maya.cmds as cmds
import maya.mel as mel


def export_selected_fbx():
    """選択したオブジェクトをFBXとして書き出す。"""

    # 選択中のオブジェクトを取得する
    selected = cmds.ls(
        selection=True,
        long=True,
        type="transform"
    ) or []

    # 選択がない場合は書き出さない
    if not selected:
        print("オブジェクトを選択してください")

        return {
            "status": "NG",
            "message": "オブジェクトが選択されていません"
        }

    # FBXの保存先を選択する
    paths = cmds.fileDialog2(
        fileMode=0,
        caption="FBXの保存先を選択",
        fileFilter="FBX Files (*.fbx)"
    )

    # ダイアログをキャンセルした場合
    if not paths:
        print("FBX書き出しをキャンセルしました")

        return {
            "status": "CANCELLED",
            "message": "書き出しをキャンセルしました"
        }

    file_path = paths[0]

    # 拡張子がなければ追加する
    if not file_path.lower().endswith(".fbx"):
        file_path += ".fbx"

    try:
        # FBXプラグインが読み込まれているか確認する
        if not cmds.pluginInfo(
            "fbxmaya",
            query=True,
            loaded=True
        ):
            #FBXプラグインがない場合、読み込む
            cmds.loadPlugin("fbxmaya")

        # MELで扱いやすいようにパスを整える
        mel_path = file_path.replace("\\", "/")
        mel_path = mel_path.replace('"', '\\"')

        # Unreal Engine向けのFBX書き出し設定(有効化)
        mel.eval("FBXExportSmoothingGroups -v true;")
        mel.eval("FBXExportTangents -v true;")
        mel.eval("FBXExportTriangulate -v true;")
        mel.eval("FBXExportUpAxis y;")

        # 選択したオブジェクトをFBXとして書き出す
        mel.eval(
            'FBXExport -f "{}" -s;'.format(mel_path)
        )

        # ファイルが作成されたか確認する
        if not os.path.isfile(file_path):
            raise RuntimeError(
                "書き出し先にFBXファイルが見つかりません"
            )

        result = {
            "status": "OK",
            "message": "FBX書き出しが完了しました",
            "file_path": file_path,
            "objects": [
                obj.split("|")[-1]
                for obj in selected
            ]
        }

        print(result["message"])
        print("保存先:", file_path)
        print("書き出したオブジェクト:", result["objects"])

        return result

    except Exception as error:
        result = {
            "status": "ERROR",
            "message": str(error),
            "file_path": file_path
        }

        print("FBX書き出しエラー")
        print("エラーの種類:", type(error).__name__)
        print("エラーの詳細:", error)

        return result


if __name__ == "__main__":
    export_selected_fbx()