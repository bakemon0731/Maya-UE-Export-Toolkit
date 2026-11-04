
# =========================================
# Maya Production Toolkit
# Tool Manager
# =========================================

import importlib
import sys


class ToolManager:

    # =====================================
    # 01. ツール起動
    # =====================================

    def launch(self, tool_info):

        """
        登録された機能を読み込み、実行する。
        """

        # ---------------------------------
        # 01. 登録情報の確認
        # ---------------------------------

        if not isinstance(tool_info, dict):

            raise TypeError(
                "ツール情報の形式が正しくありません。"
            )

        tool_title = tool_info.get(
            "title",
            "不明な機能"
        )

        if not tool_info.get("enabled", False):

            raise RuntimeError(
                f"{tool_title}は現在利用できません。"
            )

        # ---------------------------------
        # 02. 起動情報の取得
        # ---------------------------------

        module_name = tool_info.get("module")

        function_name = tool_info.get("function")

        if not module_name or not function_name:

            raise ValueError(
                f"{tool_title}の起動情報が登録されていません。"
            )

        # ---------------------------------
        # 03. モジュールの読み込み
        # ---------------------------------

        if module_name in sys.modules:

            module = importlib.reload(
                sys.modules[module_name]
            )

        else:

            module = importlib.import_module(
                module_name
            )

        # ---------------------------------
        # 04. 起動関数の取得
        # ---------------------------------

        launch_function = getattr(
            module,
            function_name,
            None
        )

        if launch_function is None:

            raise AttributeError(
                f"{module_name}に"
                f"{function_name}が存在しません。"
            )

        if not callable(launch_function):

            raise TypeError(
                f"{function_name}は実行可能な関数ではありません。"
            )

        # ---------------------------------
        # 05. 機能の実行
        # ---------------------------------

        return launch_function()
