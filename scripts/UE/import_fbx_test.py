import os
import unreal


# =========================================
# 01. 設定
# =========================================

# インポートするFBXのファイルパス
FBX_FILE_PATH = r"C:\Users\nani7\Desktop\SM_Rock.fbx"

# UEのContent Browser内の保存先
DESTINATION_PATH = "/Game/MayaImports"


# =========================================
# 02. FBX自動インポート
# =========================================

def import_fbx():

    # -------------------------------------
    # FBXファイルの存在確認
    # -------------------------------------

    if not os.path.isfile(FBX_FILE_PATH):

        unreal.log_error(
            "FBXファイルが存在しません: {}".format(
                FBX_FILE_PATH
            )
        )

        return

    # -------------------------------------
    # インポート先フォルダの確認
    # -------------------------------------

    if not unreal.EditorAssetLibrary.does_directory_exist(
        DESTINATION_PATH
    ):

        created = unreal.EditorAssetLibrary.make_directory(
            DESTINATION_PATH
        )

        if not created:

            unreal.log_error(
                "インポート先フォルダを作成できませんでした。"
            )

            return

    # -------------------------------------
    # インポート設定
    # -------------------------------------

    # FBXをUEにインポートするときの設定を管理するオブジェクト
    import_options = unreal.FbxImportUI()

    # Static Meshとしてインポートする
    import_options.set_editor_property(
        "automated_import_should_detect_type",
        False
    )

    import_options.set_editor_property(
        "mesh_type_to_import",
        unreal.FBXImportType.FBXIT_STATIC_MESH
    )

    import_options.set_editor_property(
        "import_as_skeletal",
        False
    )

    import_options.set_editor_property(
        "import_mesh",
        True
    )

    # 今回はMeshのインポートに限定する
    import_options.set_editor_property(
        "import_materials",
        False
    )

    import_options.set_editor_property(
        "import_textures",
        False
    )

    # -------------------------------------
    # インポートタスク作成
    # -------------------------------------

    task = unreal.AssetImportTask()

    task.set_editor_property(
        "filename",
        FBX_FILE_PATH
    )

    task.set_editor_property(
        "destination_path",
        DESTINATION_PATH
    )

    task.set_editor_property(
        "automated",
        True
    )

    task.set_editor_property(
        "replace_existing",
        False
    )

    task.set_editor_property(
        "save",
        True
    )

    task.set_editor_property(
        "options",
        import_options
    )

    # -------------------------------------
    # インポート実行
    # -------------------------------------

    unreal.log(
        "===== FBXインポート開始 ====="
    )

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
        [task]
    )

    # -------------------------------------
    # インポート結果取得
    # -------------------------------------

    imported_paths = task.get_editor_property(
        "imported_object_paths"
    ) or []

    if imported_paths:

        unreal.log(
            "===== FBXインポート成功 ====="
        )

        for asset_path in imported_paths:

            unreal.log(
                "インポートしたアセット: {}".format(
                    asset_path
                )
            )

    else:

        unreal.log_error(
            "FBXインポートに失敗しました。"
            "Output Logを確認してください。"
        )


# =========================================
# 03. 実行
# =========================================

import_fbx()