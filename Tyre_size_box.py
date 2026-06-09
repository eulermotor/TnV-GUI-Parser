import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout,QMessageBox
)
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QDoubleValidator


class TyreWindow(QWidget):
    tyre_details = Signal(str,float)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tyre Details")
        self.setFixedSize(350, 200)

        # ✅ Clean modern style
        # self.setStyleSheet("""
        #     QWidget {
        #         background-color: #f5f5f5;
        #         font-size: 14px;
        #     }
        #     QLineEdit {
        #         border-bottom: 2px solid #888;
        #         padding: 5px;
        #         background: transparent;
        #         color: black;
        #     }
        #     QPushButton {
        #         padding: 6px;
        #         min-width: 100px;
        #     }
        # """)

        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Enter tyre size & details:")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")

        # ---- Tyre Name ----
        tyre_layout = QHBoxLayout()
        tyre_label = QLabel("Tyre Name:")
        self.tyre_input = QLineEdit()
        self.tyre_input.setFixedSize(200, 25)
        self.tyre_input.setPlaceholderText("Enter tyre name here...")

        tyre_layout.addWidget(tyre_label)
        tyre_layout.addSpacing(10)
        tyre_layout.addWidget(self.tyre_input)
        tyre_layout.addSpacing(40)

        # ---- DRR ----
        drr_layout = QHBoxLayout()
        drr_label = QLabel("DRR:")
        self.drr_input = QLineEdit()
        self.drr_input.setFixedSize(200, 25)
        validator = QDoubleValidator(0.0,500.0,2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.drr_input.setValidator(validator)
        self.drr_input.setPlaceholderText("Enter number only")

        drr_layout.addWidget(drr_label)
        drr_layout.addSpacing(56)
        drr_layout.addWidget(self.drr_input)
        drr_layout.addSpacing(40)
        validator = QDoubleValidator(0.0,600.0,2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        # ---- Buttons (VERTICAL) ----
        self.enter_btn = QPushButton("Enter")
        self.enter_btn.clicked.connect(self.proceed)
        self.cancel_btn = QPushButton("Cancel")
        self.drr_input.setValidator(validator)

        # self.enter_btn.clicked.connect(self.submit_data)
        self.cancel_btn.clicked.connect(self.close)
        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.proceed)
        btn_layout = QHBoxLayout()   # ✅ horizontal
        # btn_layout.addStretch()      # left space
        btn_layout.addWidget(self.enter_btn)
        btn_layout.addWidget(self.cancel_btn)
        # btn_layout.addStretch()      # right space

        # Add everything
        main_layout.addStretch()
        main_layout.addWidget(title)
        main_layout.addSpacing(10)
        main_layout.addLayout(tyre_layout)
        main_layout.addLayout(drr_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def proceed(self):
        tyre = self.tyre_input.text()
        drr = float(self.drr_input.text().strip())
        if tyre and drr:
            self.tyre_details.emit(tyre,drr)
            self.close()
        else:
            if not tyre:
                QMessageBox.critical(self,"Empty Cell","Enter tyre name!!")
            elif not drr:
                QMessageBox.critical(self,"Empty Cell","Enter tyre DRR (Dynamic Rolling radius)!!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TyreWindow()
    window.show()
    sys.exit(app.exec())