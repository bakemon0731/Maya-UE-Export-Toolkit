import importlib
import traceback

# =========================================
# 00. Qtライブラリ読み込み
# =========================================

try:

    from PySide6 import QtCore, QtWidgets

    from shiboken6 import wrapInstance

    WINDOW_FLAG = QtCore.Qt.WindowType.Window

except ImportError:

    from PySide2 import QtCore, QtWidgets

    from shiboken2 import wrapInstance

    WINDOW_FLAG = QtCore.Qt.Window


from maya import OpenMayaUI as omui

# Phongマテリアルの情報取得・変換モジュール
from material_tools import phong_to_arnold_converter


# =========================================
# 01. ウィンドウ管理
# =========================================

WINDOW = None

WINDOW_NAME = "PhongToArnoldConverterWindow"


# =========================================
# 02. UIクラス
# =========================================

class PhongToArnoldWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setObjectName(
            WINDOW_NAME
        )

        self.setWindowTitle(
            "Phong → Arnold Converter"
        )

        self.setWindowFlags(
            WINDOW_FLAG
        )

        self.resize(1100, 580)

        self.setMinimumSize(850, 450)

        self.build_ui()

        # 起動時に一覧を取得
        self.refresh_material_list()

    # =====================================
    # 03. UI構築
    # =====================================

    def build_ui(self):

        # ---------------------------------
        # メインレイアウト
        # ---------------------------------

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.setContentsMargins(
            24, 24, 24, 24
        )

        main_layout.setSpacing(16)

        # ---------------------------------
        # HEADER
        # ---------------------------------

        title = QtWidgets.QLabel(
            "Phong → Arnold Converter"
        )

        title.setObjectName(
            "titleLabel"
        )

        description = QtWidgets.QLabel(
            "Phongマテリアルの変換状態を確認し、"
            "Arnold Standard Surfaceへ変換します。"
        )

        description.setObjectName(
            "descriptionLabel"
        )

        main_layout.addWidget(title)

        main_layout.addWidget(description)

        # ---------------------------------
        # 検出件数
        # ---------------------------------

        self.summary_label = QtWidgets.QLabel(
            "マテリアル情報を取得しています..."
        )

        self.summary_label.setObjectName(
            "summaryLabel"
        )

        main_layout.addWidget(
            self.summary_label
        )

        # =================================
        # マテリアル一覧
        # =================================

        self.material_table = QtWidgets.QTableWidget()

        self.material_table.setObjectName(
            "materialTable"
        )

        # 列数を5列に設定
        self.material_table.setColumnCount(5)

        # 列の見出し
        self.material_table.setHorizontalHeaderLabels(
            [
                "Phongマテリアル",
                "変換状態",
                "Arnoldマテリアル",
                "Shading Group",
                "割り当て先"
            ]
        )

        # ---------------------------------
        # テーブルの操作設定
        # ---------------------------------

        try:

            # PySide6

            self.material_table.setEditTriggers(
                QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            )

            self.material_table.setSelectionBehavior(
                QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )

            self.material_table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )

        except AttributeError:

            # PySide2

            self.material_table.setEditTriggers(
                QtWidgets.QAbstractItemView.NoEditTriggers
            )

            self.material_table.setSelectionBehavior(
                QtWidgets.QAbstractItemView.SelectRows
            )

            self.material_table.setSelectionMode(
                QtWidgets.QAbstractItemView.SingleSelection
            )

        # ---------------------------------
        # テーブルの表示設定
        # ---------------------------------

        self.material_table.setAlternatingRowColors(
            True
        )

        self.material_table.setWordWrap(
            True
        )

        self.material_table.verticalHeader().setVisible(
            False
        )

        # 行の並び替えによる選択処理の混乱を防止
        self.material_table.setSortingEnabled(
            False
        )

        # ---------------------------------
        # テーブルの列幅設定
        # ---------------------------------

        header = self.material_table.horizontalHeader()

        try:

            # PySide6

            header.setSectionResizeMode(
                0,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )

            header.setSectionResizeMode(
                1,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )

            header.setSectionResizeMode(
                2,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )

            header.setSectionResizeMode(
                3,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )

            header.setSectionResizeMode(
                4,
                QtWidgets.QHeaderView.ResizeMode.Stretch
            )

        except AttributeError:

            # PySide2

            header.setSectionResizeMode(
                0,
                QtWidgets.QHeaderView.ResizeToContents
            )

            header.setSectionResizeMode(
                1,
                QtWidgets.QHeaderView.ResizeToContents
            )

            header.setSectionResizeMode(
                2,
                QtWidgets.QHeaderView.ResizeToContents
            )

            header.setSectionResizeMode(
                3,
                QtWidgets.QHeaderView.ResizeToContents
            )

            header.setSectionResizeMode(
                4,
                QtWidgets.QHeaderView.Stretch
            )

        # ---------------------------------
        # 選択状態の変更を監視
        # ---------------------------------

        self.material_table.itemSelectionChanged.connect(
            self.update_convert_button_state
        )

        # テーブルをメインレイアウトに追加
        main_layout.addWidget(
            self.material_table,
            1
        )

        # =================================
        # ボタン
        # =================================

        button_layout = QtWidgets.QHBoxLayout()

        button_layout.addStretch()

        # ---------------------------------
        # 一覧更新ボタン
        # ---------------------------------

        self.refresh_button = QtWidgets.QPushButton(
            "一覧を更新"
        )

        self.refresh_button.setObjectName(
            "refreshButton"
        )

        self.refresh_button.clicked.connect(
            self.refresh_material_list
        )

        # ---------------------------------
        # 変換ボタン
        # ---------------------------------

        self.convert_button = QtWidgets.QPushButton(
            "選択したマテリアルを変換"
        )

        self.convert_button.setObjectName(
            "convertButton"
        )

        self.convert_button.clicked.connect(
            self.convert_selected_material
        )

        # 最初は未選択なので無効
        self.convert_button.setEnabled(
            False
        )

        # ---------------------------------
        # 閉じるボタン
        # ---------------------------------

        self.close_button = QtWidgets.QPushButton(
            "閉じる"
        )

        self.close_button.setObjectName(
            "closeButton"
        )

        self.close_button.clicked.connect(
            self.close
        )

        # ボタンを配置
        button_layout.addWidget(
            self.refresh_button
        )

        button_layout.addWidget(
            self.convert_button
        )

        button_layout.addWidget(
            self.close_button
        )

        main_layout.addLayout(
            button_layout
        )

        # =================================
        # デザイン
        # =================================

        self.setStyleSheet("""

            QWidget#PhongToArnoldConverterWindow {
                background-color: #171D27;
            }

            QLabel#titleLabel {
                color: #F0F3F7;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#descriptionLabel {
                color: #AAB6C5;
                font-size: 12px;
                padding-bottom: 12px;
                border-bottom: 1px solid #354253;
            }

            QLabel#summaryLabel {
                color: #68C8DC;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
                background-color: #222B35;
                border: 1px solid #354253;
                border-radius: 5px;
            }

            QTableWidget#materialTable {
                background-color: #222B35;
                alternate-background-color: #283442;
                color: #D6E1EA;
                font-size: 12px;
                border: 1px solid #354253;
                gridline-color: #354253;
            }

            QTableWidget#materialTable::item {
                padding: 6px;
            }

            QTableWidget#materialTable::item:selected {
                background-color: #24647A;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #354253;
                color: #F0F3F7;
                font-weight: bold;
                padding: 9px;
                border: none;
            }

            QPushButton#refreshButton {
                background-color: #24647A;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }

            QPushButton#refreshButton:hover {
                background-color: #32849C;
            }

            QPushButton#convertButton {
                background-color: #287B66;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }

            QPushButton#convertButton:hover {
                background-color: #34977D;
            }

            QPushButton#convertButton:disabled {
                background-color: #354253;
                color: #778596;
            }

            QPushButton#closeButton {
                background-color: #354253;
                color: #D6E1EA;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }

            QPushButton#closeButton:hover {
                background-color: #46586B;
            }

            QToolTip {
                background-color: #222B35;
                color: #F0F3F7;
                border: 1px solid #68C8DC;
                padding: 7px;
                border-radius: 4px;
            }

        """)

    # =====================================
    # 04. 変換ボタンの有効・無効
    # =====================================

    def update_convert_button_state(self):

        """
        マテリアルが選択されている場合だけ
        変換ボタンを有効にする。
        """

        selected_row = self.material_table.currentRow()

        has_selection = selected_row >= 0

        self.convert_button.setEnabled(
            has_selection
        )

    # =====================================
    # 05. Phongマテリアル一覧の更新
    # =====================================

    def refresh_material_list(self):

        try:

            # ---------------------------------
            # Converterモジュールを再読み込み
            # ---------------------------------

            importlib.reload(
                phong_to_arnold_converter
            )

            # ---------------------------------
            # Phongマテリアル情報を取得
            # ---------------------------------

            material_infos = (
                phong_to_arnold_converter
                .get_phong_material_info()
            ) or []

            # ---------------------------------
            # 現在の一覧をクリア
            # ---------------------------------

            self.material_table.setRowCount(0)

            # =================================
            # 変換状態を取得
            # =================================

            conversion_info = {}

            # 同じPhongを何度も検索しないようにする
            for info in material_infos:

                material = info.get(
                    "material"
                )

                if not material:

                    continue

                if material in conversion_info:

                    continue

                # 対応するArnoldマテリアルを検索
                arnold_material = (
                    phong_to_arnold_converter
                    .find_converted_arnold_material(
                        material
                    )
                )

                if arnold_material:

                    conversion_info[material] = {

                        "status": "変換済み",

                        "arnold_material": arnold_material

                    }

                else:

                    conversion_info[material] = {

                        "status": "未変換",

                        "arnold_material": "なし"

                    }

            # =================================
            # 取得した情報をテーブルに追加
            # =================================

            for info in material_infos:

                material = info.get(
                    "material",
                    "不明"
                )

                shading_engine = info.get(
                    "shading_engine"
                )

                members = info.get(
                    "members",
                    []
                ) or []

                # ---------------------------------
                # 変換状態を取得
                # ---------------------------------

                material_conversion = conversion_info.get(
                    material,
                    {
                        "status": "未変換",
                        "arnold_material": "なし"
                    }
                )

                status_text = material_conversion.get(
                    "status"
                )

                arnold_text = material_conversion.get(
                    "arnold_material"
                )

                # ---------------------------------
                # 表示する文字列を準備
                # ---------------------------------

                shading_engine_text = (
                    shading_engine
                    if shading_engine
                    else "なし"
                )

                members_text = (
                    "\n".join(
                        str(member)
                        for member in members
                    )
                    if members
                    else "割り当てなし"
                )

                values = [

                    material,

                    status_text,

                    arnold_text,

                    shading_engine_text,

                    members_text

                ]

                # ---------------------------------
                # テーブルに新しい行を追加
                # ---------------------------------

                row = self.material_table.rowCount()

                self.material_table.insertRow(row)

                for column, value in enumerate(values):

                    item = QtWidgets.QTableWidgetItem(
                        str(value)
                    )

                    # ---------------------------------
                    # 状態列の中央揃え
                    # ---------------------------------

                    if column == 1:

                        try:

                            item.setTextAlignment(
                                QtCore.Qt.AlignmentFlag.AlignCenter
                            )

                        except AttributeError:

                            item.setTextAlignment(
                                QtCore.Qt.AlignCenter
                            )

                    # ---------------------------------
                    # Arnold名の中央揃え
                    # ---------------------------------

                    if column == 2:

                        try:

                            item.setTextAlignment(
                                QtCore.Qt.AlignmentFlag.AlignCenter
                            )

                        except AttributeError:

                            item.setTextAlignment(
                                QtCore.Qt.AlignCenter
                            )

                    # ---------------------------------
                    # アイテムをテーブルに追加
                    # ---------------------------------

                    self.material_table.setItem(
                        row,
                        column,
                        item
                    )

            # =================================
            # 検出件数を集計
            # =================================

            material_count = len(conversion_info)

            converted_count = sum(

                1

                for info in conversion_info.values()

                if info["status"] == "変換済み"

            )

            unconverted_count = (

                material_count - converted_count

            )

            info_count = len(material_infos)

            # ---------------------------------
            # 検出件数を表示
            # ---------------------------------

            self.summary_label.setText(

                "Phong: {}件　｜　変換済み: {}件"
                "　｜　未変換: {}件　｜　割り当て情報: {}件".format(

                    material_count,

                    converted_count,

                    unconverted_count,

                    info_count

                )

            )

            # ---------------------------------
            # テーブルの表示サイズを調整
            # ---------------------------------

            self.material_table.resizeRowsToContents()

            # ---------------------------------
            # Phongが見つからなかった場合
            # ---------------------------------

            if material_count == 0:

                self.summary_label.setText(
                    "Phongマテリアルは見つかりませんでした。"
                )

            # 一覧更新後は選択を解除
            self.material_table.clearSelection()

            self.convert_button.setEnabled(
                False
            )

            print(
                "Phongマテリアル一覧を更新しました。"
            )

        except Exception as error:

            error_text = traceback.format_exc()

            print(error_text)

            self.summary_label.setText(
                "マテリアル情報の取得に失敗しました。"
            )

            QtWidgets.QMessageBox.critical(

                self,

                "取得エラー",

                "Phongマテリアル情報を取得できませんでした。\n\n"
                + str(error)

            )

    # =====================================
    # 06. 選択したPhongをArnoldに変換
    # =====================================

    def convert_selected_material(self):

        """
        テーブルで選択されたPhongマテリアルを
        Arnold Standard Surfaceへ変換する。
        """

        try:

            # ---------------------------------
            # 選択行を取得
            # ---------------------------------

            selected_row = self.material_table.currentRow()

            if selected_row < 0:

                QtWidgets.QMessageBox.warning(

                    self,

                    "選択エラー",

                    "変換するPhongマテリアルを選択してください。"

                )

                return

            # ---------------------------------
            # 選択行のPhong名を取得
            # ---------------------------------

            material_item = self.material_table.item(
                selected_row,
                0
            )

            if not material_item:

                return

            phong_material = material_item.text()

            # ---------------------------------
            # 変換確認
            # ---------------------------------

            answer = QtWidgets.QMessageBox.question(

                self,

                "変換確認",

                "次のPhongマテリアルをArnoldに変換しますか？\n\n"
                + phong_material,

                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No

            )

            if answer != QtWidgets.QMessageBox.StandardButton.Yes:

                return

            # ---------------------------------
            # Converterモジュールを再読み込み
            # ---------------------------------

            importlib.reload(
                phong_to_arnold_converter
            )

            # ---------------------------------
            # 変換処理を実行
            # ---------------------------------

            result = (
                phong_to_arnold_converter
                .auto_convert_phong_to_arnold(
                    [phong_material]
                )
            )

            # =================================
            # 変換結果を取得
            # =================================

            results = result.get(
                "results",
                []
            )

            material_result = None

            for item in results:

                if item.get("material") == phong_material:

                    material_result = item

                    break

            # =================================
            # 変換結果の表示
            # =================================

            if material_result:

                status = material_result.get(
                    "status"
                )

                message = material_result.get(
                    "message",
                    "処理が完了しました。"
                )

                arnold_material = material_result.get(
                    "arnold_material"
                )

                # ---------------------------------
                # 成功
                # ---------------------------------

                if status == "OK":

                    QtWidgets.QMessageBox.information(

                        self,

                        "変換完了",

                        "Arnoldへの変換が完了しました。\n\n"
                        "Phong: {}\n"
                        "Arnold: {}".format(

                            phong_material,

                            arnold_material

                        )

                    )

                # ---------------------------------
                # スキップ
                # ---------------------------------

                elif status == "SKIP":

                    QtWidgets.QMessageBox.information(

                        self,

                        "変換スキップ",

                        "{}\n\n{}".format(

                            phong_material,

                            message

                        )

                    )

                # ---------------------------------
                # エラー
                # ---------------------------------

                elif status == "ERROR":

                    QtWidgets.QMessageBox.warning(

                        self,

                        "変換エラー",

                        "{}\n\n{}".format(

                            phong_material,

                            message

                        )

                    )

            else:

                QtWidgets.QMessageBox.warning(

                    self,

                    "変換結果",

                    "変換結果を取得できませんでした。\n\n"
                    + str(result)

                )

            # =================================
            # 変換後に一覧を更新
            # =================================

            self.refresh_material_list()

        except Exception as error:

            error_text = traceback.format_exc()

            print(error_text)

            QtWidgets.QMessageBox.critical(

                self,

                "変換処理エラー",

                "マテリアルの変換中にエラーが発生しました。\n\n"
                + str(error)

            )


# =========================================
# 07. UI起動
# =========================================

def show_ui():

    global WINDOW

    # -------------------------------------
    # Mayaのメインウィンドウを取得
    # -------------------------------------

    maya_ptr = omui.MQtUtil.mainWindow()

    if not maya_ptr:

        raise RuntimeError(
            "Mayaのメインウィンドウを取得できません。"
        )

    maya_window = wrapInstance(
        int(maya_ptr),
        QtWidgets.QWidget
    )

    # -------------------------------------
    # 古いウィンドウを閉じる
    # -------------------------------------

    old_windows = maya_window.findChildren(
        QtWidgets.QWidget,
        WINDOW_NAME
    )

    for old_window in old_windows:

        old_window.close()

        old_window.deleteLater()

    WINDOW = None

    # -------------------------------------
    # 新しいウィンドウを生成
    # -------------------------------------

    WINDOW = PhongToArnoldWindow(
        maya_window
    )

    WINDOW.show()

    return WINDOW