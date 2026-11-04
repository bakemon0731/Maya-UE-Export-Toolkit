# =========================================
# Maya Production Toolkit
# Launcher
# =========================================

import os
import sys
import importlib


# =========================================
# 01. プロジェクトパス
# =========================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if SCRIPT_DIR not in sys.path:

    sys.path.insert(
        0,
        SCRIPT_DIR
    )


# =========================================
# 02. ホーム画面起動
# =========================================

def show_ui():

    # カードの部品を再読み込み
    import mpt_ui.widgets.tool_card_widget
    importlib.reload(
        mpt_ui.widgets.tool_card_widget
    )

    # ツール登録情報を再読み込み
    import mpt_ui.tool_registry
    importlib.reload(
        mpt_ui.tool_registry
    )

    # メイン画面を再読み込み
    import mpt_ui.main_window
    importlib.reload(
        mpt_ui.main_window
    )

    return mpt_ui.main_window.show_ui()