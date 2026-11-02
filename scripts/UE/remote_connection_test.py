import os
import sys
import time
import traceback


# =========================================
# 01. Unreal EngineのPythonパス
# =========================================

UE_PYTHON_DIR = (
    r"C:\Program Files\Epic Games\UE_5.6"
    r"\Engine\Plugins\Experimental"
    r"\PythonScriptPlugin\Content\Python"
)

REMOTE_EXECUTION_FILE = os.path.join(
    UE_PYTHON_DIR,
    "remote_execution.py"
)


# =========================================
# 02. Remote Execution読み込み
# =========================================

if not os.path.isfile(REMOTE_EXECUTION_FILE):

    raise FileNotFoundError(
        "remote_execution.pyが見つかりません。\n"
        "UE_PYTHON_DIRを確認してください。\n"
        + REMOTE_EXECUTION_FILE
    )

if UE_PYTHON_DIR not in sys.path:

    sys.path.insert(
        0,
        UE_PYTHON_DIR
    )

from remote_execution import RemoteExecution


# =========================================
# 03. UE接続テスト
# =========================================

def test_connection():

    remote_execute = RemoteExecution()

    started = False

    print("===== UE接続テスト開始 =====")

    try:

        # Remote Executionの開始
        remote_execute.start()

        started = True

        print("UEの検出を開始しました。")

        # UEの検出を待つ
        time.sleep(2)

        # 検出されたUEを取得
        remote_nodes = remote_execute.remote_nodes

        if not remote_nodes:

            print("UEを検出できませんでした。")

            print(
                "Remote Executionの設定を確認してください。"
            )

            return False

        print(
            "検出したUEの数: {}".format(
                len(remote_nodes)
            )
        )

        # 最初に検出したUEを接続先にする
        target_node = remote_nodes[0]

        print("UEへの接続を開始します。")

        # コマンド接続を開く
        remote_execute.open_command_connection(
            target_node
        )

        print("UEへの接続に成功しました。")

        # UE側で実行するPythonコード
        command = (
            'import unreal\n'
            'unreal.log("Mayaからのリモート通信に成功しました！")'
        )

        # UEにPythonコードを送信
        result = remote_execute.run_command(
            command
        )

        print("===== UEからの実行結果 =====")

        print(result)

        print("===== UE接続テスト成功 =====")

        return True

    except Exception:

        print("UE接続中にエラーが発生しました。")

        traceback.print_exc()

        return False

    finally:

        # Remote Executionを終了
        if started:

            try:

                remote_execute.stop()

                print("Remote Executionを終了しました。")

            except Exception:

                print("通信終了時にエラーが発生しました。")

                traceback.print_exc()