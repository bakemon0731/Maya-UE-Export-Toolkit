
# =========================================
# Maya Production Toolkit
# Tool Card Widget
# =========================================

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets


class ToolCardWidget(QtWidgets.QFrame):

    # ボタンがクリックされたことを知らせるSignal
    clicked = QtCore.Signal()

    def __init__(
        self,
        category,
        title,
        description,
        status="利用可能",
        enabled=True,
        parent=None
    ):

        super().__init__(parent)

        self.setObjectName("toolCard")

        self.setMinimumHeight(175)

        # =====================================
        # メインレイアウト
        # =====================================

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.setContentsMargins(
            16, 14, 16, 14
        )

        main_layout.setSpacing(10)

        # =====================================
        # 上部：カテゴリーと状態
        # =====================================

        top_layout = QtWidgets.QHBoxLayout()

        self.category_label = QtWidgets.QLabel(
            category
        )

        self.category_label.setObjectName(
            "toolCardCategory"
        )

        self.status_label = QtWidgets.QLabel(
            status
        )

        self.status_label.setAlignment(
            QtCore.Qt.AlignCenter
        )

        if status == "利用可能":

            self.status_label.setObjectName(
                "statusAvailable"
            )

        elif status == "準備中":

            self.status_label.setObjectName(
                "statusPreparing"
            )

        else:

            self.status_label.setObjectName(
                "statusPlanned"
            )

        top_layout.addWidget(
            self.category_label
        )

        top_layout.addStretch()

        top_layout.addWidget(
            self.status_label
        )

        main_layout.addLayout(
            top_layout
        )

        # =====================================
        # タイトル
        # =====================================

        self.title_label = QtWidgets.QLabel(
            title
        )

        self.title_label.setObjectName(
            "toolCardTitle"
        )

        self.title_label.setWordWrap(True)

        main_layout.addWidget(
            self.title_label
        )

        # =====================================
        # 説明
        # =====================================

        self.description_label = QtWidgets.QLabel(
            description
        )

        self.description_label.setObjectName(
            "toolCardDescription"
        )

        self.description_label.setWordWrap(True)

        main_layout.addWidget(
            self.description_label
        )

        main_layout.addStretch()

        # =====================================
        # 起動ボタン
        # =====================================

        self.open_button = QtWidgets.QPushButton(
            "開く" if enabled else "準備中"
        )

        self.open_button.setObjectName(
            "toolCardButton"
        )

        self.open_button.setEnabled(enabled)

        self.open_button.setToolTip(
            description
        )

        self.open_button.clicked.connect(
            self.clicked.emit
        )

        main_layout.addWidget(
            self.open_button
        )

        # -------------------------------------
        # カード全体の説明
        # -------------------------------------

        self.setToolTip(description)
