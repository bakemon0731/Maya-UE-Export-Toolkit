import os
import sys
import time
import json
import glob
import traceback
import importlib.util


# =========================================
# 01. Unreal Engineの設定
# =========================================

# 特定のインストール先を使用する場合だけ指定する
# 自動検出する場合はNoneのままにする

UE_ENGINE_ROOT = None

# 例：
# UE_ENGINE_ROOT = r"D:\Epic Games\UE_5.6"


# =========================================
# 02. UEインストール先の検出
# =========================================

def find_ue_python_dir():

    candidates = []

    # -------------------------------------
    # 手動指定されたパス
    # -------------------------------------

    if UE_ENGINE_ROOT:

        candidates.append(UE_ENGINE_ROOT)

    # -------------------------------------
    # Epic Games Launcherの情報を取得
    # -------------------------------------

    program_data = os.environ.get(
        "PROGRAMDATA",
        r"C:\ProgramData"
    )

    launcher_manifest = os.path.join(
        program_data,
        "Epic",
        "UnrealEngineLauncher",
        "LauncherInstalled.dat"
    )

    if os.path.isfile(launcher_manifest):

        try:

            with open(
                launcher_manifest,
                "r",
                encoding="utf-8"
            ) as file:

                manifest_data = json.load(file)

            installations = manifest_data.get(
                "InstallationList",
                []
            )

            for installation in installations:

                install_location = installation.get(
                    "InstallLocation"
                )

                if install_location:

                    candidates.append(
                        install_location
                    )

        except Exception as error:

            print(
                "Launcher情報の読み込みに失敗しました: {}".format(
                    error
                )
            )

    # -------------------------------------
    # 新しいLauncherのマニフェストも確認
    # -------------------------------------

    manifest_directory = os.path.join(
        program_data,
        "Epic",
        "EpicGamesLauncher",
        "Data",
        "Manifests"
    )

    manifest_files = glob.glob(
        os.path.join(
            manifest_directory,
            "*.item"
        )
    )

    for manifest_file in manifest_files:

        try:

            with open(
                manifest_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            install_location = data.get(
                "InstallLocation"
            )

            if install_location:

                candidates.append(
                    install_location
                )

        except Exception:

            continue

    # -------------------------------------
    # 一般的なインストール先も確認
    # -------------------------------------

    common_directories = [
        r"C:\Program Files\Epic Games",
        r"C:\Epic Games",
        r"D:\Epic Games",
        r"E:\Epic Games",
        r"F:\Epic Games"
    ]

    for directory in common_directories:

        if not os.path.isdir(directory):
            continue

        candidates.extend(
            glob.glob(
                os.path.join(
                    directory,
                    "UE_*"
                )
            )
        )

    # -------------------------------------
    # 重複を除去
    # -------------------------------------

    unique_candidates = []

    seen = set()

    for candidate in candidates:

        normalized = os.path.normcase(
            os.path.normpath(candidate)
        )

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_candidates.append(candidate)

    # -------------------------------------
    # remote_execution.pyを検索
    # -------------------------------------

    for engine_root in unique_candidates:

        python_dir = os.path.join(
            engine_root,
            "Engine",
            "Plugins",
            "Experimental",
            "PythonScriptPlugin",
            "Content",
            "Python"
        )

        remote_file = os.path.join(
            python_dir,
            "remote_execution.py"
        )

        if os.path.isfile(remote_file):

            print(
                "Unreal Engineを検出しました:"
            )

            print(engine_root)

            print(
                "Remote Execution: {}".format(
                    remote_file
                )
            )

            return python_dir

    return None


# =========================================
# 03. Remote Executionの読み込み
# =========================================

UE_PYTHON_DIR = find_ue_python_dir()

if UE_PYTHON_DIR is None:

    raise FileNotFoundError(
        "Unreal Engineのremote_execution.pyを"
        "自動検出できませんでした。\n\n"
        "UE_ENGINE_ROOTにUEのインストール先を"
        "指定してください。"
    )


REMOTE_EXECUTION_FILE = os.path.join(
    UE_PYTHON_DIR,
    "remote_execution.py"
)


# -----------------------------------------
# 指定したファイルからモジュールを読み込む
# -----------------------------------------

spec = importlib.util.spec_from_file_location(
    "maya_ue_remote_execution",
    REMOTE_EXECUTION_FILE
)

if spec is None or spec.loader is None:

    raise ImportError(
        "Remote Executionモジュールを読み込めません。"
    )

remote_module = importlib.util.module_from_spec(
    spec
)

sys.modules[spec.name] = remote_module

spec.loader.exec_module(
    remote_module
)

RemoteExecution = remote_module.RemoteExecution


print("Remote Executionの読み込みに成功しました。")


# =========================================
# 03. UE側で実行するインポート処理
# =========================================

def build_import_command(fbx_path, destination_path):

    # Maya側の文字列をUE側のPythonコードに安全に渡す
    fbx_literal = json.dumps(fbx_path)

    destination_literal = json.dumps(destination_path)

    command = (
        "import os as _m2ue_os\n"
        "import unreal as _m2ue_unreal\n"
        "\n"

        # パラメータ
        "_m2ue_fbx_path = " + fbx_literal + "\n"
        "_m2ue_destination = " + destination_literal + "\n"
        "\n"

        "try:\n"

        "    # FBXファイルの存在確認\n"
        "    if not _m2ue_os.path.isfile(_m2ue_fbx_path):\n"
        "        raise RuntimeError('FBXファイルが存在しません: ' + _m2ue_fbx_path)\n"
        "\n"

        "    # インポート先フォルダの確認\n"
        "    if not _m2ue_unreal.EditorAssetLibrary.does_directory_exist(_m2ue_destination):\n"
        "\n"

        "        _m2ue_created = _m2ue_unreal.EditorAssetLibrary.make_directory(_m2ue_destination)\n"
        "\n"

        "        if not _m2ue_created:\n"
        "            raise RuntimeError('インポート先フォルダを作成できませんでした。')\n"
        "\n"

        "    # FBXインポート設定\n"
        "    _m2ue_import_options = _m2ue_unreal.FbxImportUI()\n"
        "\n"

        "    _m2ue_import_options.set_editor_property(\n"
        "        'automated_import_should_detect_type', False\n"
        "    )\n"
        "\n"

        "    _m2ue_import_options.set_editor_property(\n"
        "        'mesh_type_to_import',\n"
        "        _m2ue_unreal.FBXImportType.FBXIT_STATIC_MESH\n"
        "    )\n"
        "\n"

        "    _m2ue_import_options.set_editor_property(\n"
        "        'import_as_skeletal', False\n"
        "    )\n"
        "\n"

        "    _m2ue_import_options.set_editor_property(\n"
        "        'import_mesh', True\n"
        "    )\n"
        "\n"

        "    _m2ue_import_options.set_editor_property(\n"
        "        'import_materials', False\n"
        "    )\n"
        "\n"

        "    _m2ue_import_options.set_editor_property(\n"
        "        'import_textures', False\n"
        "    )\n"
        "\n"

        "    # インポートタスク作成\n"
        "    _m2ue_task = _m2ue_unreal.AssetImportTask()\n"
        "\n"

        "    _m2ue_task.set_editor_property(\n"
        "        'filename', _m2ue_fbx_path\n"
        "    )\n"
        "\n"

        "    _m2ue_task.set_editor_property(\n"
        "        'destination_path', _m2ue_destination\n"
        "    )\n"
        "\n"

        "    _m2ue_task.set_editor_property(\n"
        "        'automated', True\n"
        "    )\n"
        "\n"

        "    _m2ue_task.set_editor_property(\n"
        "        'replace_existing', False\n"
        "    )\n"
        "\n"

        "    _m2ue_task.set_editor_property(\n"
        "        'save', True\n"
        "    )\n"
        "\n"

        "    _m2ue_task.set_editor_property(\n"
        "        'options', _m2ue_import_options\n"
        "    )\n"
        "\n"

        "    # インポート実行\n"
        "    _m2ue_asset_tools = _m2ue_unreal.AssetToolsHelpers.get_asset_tools()\n"
        "\n"

        "    _m2ue_asset_tools.import_asset_tasks(\n"
        "        [_m2ue_task]\n"
        "    )\n"
        "\n"

        "    # インポート結果取得\n"
        "    _m2ue_imported_paths = _m2ue_task.get_editor_property(\n"
        "        'imported_object_paths'\n"
        "    ) or []\n"
        "\n"

        "    if not _m2ue_imported_paths:\n"
        "        raise RuntimeError('インポートされたアセットがありません。')\n"
        "\n"

        "    # 成功結果をMayaに返すためのログ\n"
        "    _m2ue_unreal.log('M2UE_IMPORT_RESULT:SUCCESS')\n"
        "\n"

        "    for _m2ue_asset_path in _m2ue_imported_paths:\n"
        "        _m2ue_unreal.log(\n"
        "            'M2UE_IMPORTED_ASSET:' + str(_m2ue_asset_path)\n"
        "        )\n"
        "\n"

        "except Exception as _m2ue_error:\n"
        "\n"

        "    _m2ue_unreal.log_error('M2UE_IMPORT_RESULT:FAILED')\n"
        "\n"

        "    _m2ue_unreal.log_error(\n"
        "        'M2UE_IMPORT_ERROR:' + str(_m2ue_error)\n"
        "    )\n"
    )

    return command


# =========================================
# 04. MayaからUEへFBXを送信
# =========================================

def import_fbx_to_ue(
    fbx_path,
    destination_path="/Game/MayaRemoteTest",
    discovery_timeout=8.0
):

    remote_execute = RemoteExecution()

    started = False

    try:

        # ---------------------------------
        # FBXファイルの存在確認
        # ---------------------------------

        fbx_path = os.path.abspath(fbx_path)

        if not os.path.isfile(fbx_path):

            return {
                "status": "ERROR",
                "message": "FBXファイルが見つかりません。",
                "details": fbx_path,
                "imported_assets": []
            }

        # ---------------------------------
        # UE保存先の確認
        # ---------------------------------

        if not isinstance(destination_path, str):

            return {
                "status": "ERROR",
                "message": "保存先の形式が正しくありません。",
                "details": str(destination_path),
                "imported_assets": []
            }

        if not destination_path.startswith("/Game/"):

            return {
                "status": "ERROR",
                "message": "保存先は/Game/から始まる必要があります。",
                "details": destination_path,
                "imported_assets": []
            }

        # ---------------------------------
        # Remote Execution開始
        # ---------------------------------

        print("===== UEインポート処理開始 =====")

        print("FBX: " + fbx_path)

        print("UE保存先: " + destination_path)

        remote_execute.start()

        started = True

        # ---------------------------------
        # UEの検出
        # ---------------------------------

        print("Unreal Engineを検索しています...")

        deadline = time.monotonic() + discovery_timeout

        remote_nodes = []

        while time.monotonic() < deadline:

            remote_nodes = remote_execute.remote_nodes

            if remote_nodes:
                break

            time.sleep(0.25)

        if not remote_nodes:

            return {
                "status": "ERROR",
                "message": "Unreal Engineを検出できませんでした。",
                "details": "UEの起動状態とRemote Execution設定を確認してください。",
                "imported_assets": []
            }

        # ---------------------------------
        # UEに接続
        # ---------------------------------

        if len(remote_nodes) > 1:

            return {
                "status": "ERROR",
                "message": "複数のUnreal Engineが検出されました。",
                "details": "対象のUEを1つだけ起動して再実行してください。",
                "imported_assets": []
            }

        target_node = remote_nodes[0]

        print("Unreal Engineを検出しました。")

        remote_execute.open_command_connection(
            target_node
        )

        print("UEへの接続に成功しました。")

        # ---------------------------------
        # UEに送信するコードを作成
        # ---------------------------------

        command = build_import_command(
            fbx_path,
            destination_path
        )

        # ---------------------------------
        # FBXインポート命令を送信
        # ---------------------------------

        print("FBXインポート命令を送信しています...")

        response = remote_execute.run_command(
            command
        )

        # ---------------------------------
        # UEからの実行結果取得
        # ---------------------------------

        if not response.get("success"):

            return {
                "status": "ERROR",
                "message": "UE側でPythonの実行に失敗しました。",
                "details": response,
                "imported_assets": []
            }

        outputs = response.get("output", [])

        output_texts = [
            item.get("output", "")
            for item in outputs
            if isinstance(item, dict)
        ]

        # ---------------------------------
        # インポート成功判定
        # ---------------------------------

        succeeded = any(
            "M2UE_IMPORT_RESULT:SUCCESS" in text
            for text in output_texts
        )

        failed = any(
            "M2UE_IMPORT_RESULT:FAILED" in text
            for text in output_texts
        )

        imported_assets = []

        for output in output_texts:

            marker = "M2UE_IMPORTED_ASSET:"

            if marker in output:

                asset_path = output.split(
                    marker,
                    1
                )[1].strip()

                imported_assets.append(asset_path)

        # ---------------------------------
        # 最終結果
        # ---------------------------------

        if succeeded and imported_assets:

            print("===== UEインポート成功 =====")

            for asset in imported_assets:

                print("インポート: " + asset)

            return {
                "status": "OK",
                "message": "FBXのUEインポートに成功しました。",
                "details": "",
                "imported_assets": imported_assets
            }

        error_messages = [
            text.split("M2UE_IMPORT_ERROR:", 1)[1].strip()
            for text in output_texts
            if "M2UE_IMPORT_ERROR:" in text
        ]

        if failed:

            error_message = "\n".join(error_messages)

        else:

            error_message = (
                "UEから正常なインポート完了通知を取得できませんでした。"
            )

        print("===== UEインポート失敗 =====")

        print(error_message)

        return {
            "status": "ERROR",
            "message": "FBXのUEインポートに失敗しました。",
            "details": error_message,
            "imported_assets": []
        }

    except Exception as error:

        print("===== 通信エラー =====")

        traceback.print_exc()

        return {
            "status": "ERROR",
            "message": str(error),
            "details": traceback.format_exc(),
            "imported_assets": []
        }

    finally:

        # ---------------------------------
        # Remote Execution終了
        # ---------------------------------

        if started:

            try:

                remote_execute.stop()

                print("Remote Executionを終了しました。")

            except Exception:

                traceback.print_exc()