import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFrame,QMessageBox
)
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QDoubleValidator

class GearRatioWindow(QWidget):
    gear_ration_sgl = Signal(float)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gear Ratio")
        self.setFixedSize(420, 160)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Outer frame (box)
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(2)

        frame_layout = QVBoxLayout(frame)

        # Title
        title = QLabel("Enter Gear ratio:")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        frame_layout.addWidget(title)

        # Input + example layout
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type here...")
        self.input_field.setFixedHeight(32)

        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid black;
                border-radius: 8px;
                padding-left: 10px;
            }
        """)
        validator = QDoubleValidator(0.0,600.0,2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.input_field.setValidator(validator)
        example = QLabel("Ex. 12.35")
        example.setStyleSheet("font-size: 11px;")

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(example)

        frame_layout.addLayout(input_layout)

        # Buttons layout (Enter + Cancel)
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        enter_btn = QPushButton("Enter")
        enter_btn.clicked.connect(self.proceed)
        cancel_btn = QPushButton("Cancel")

        for btn in (enter_btn, cancel_btn):
            btn.setFixedSize(80, 30)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid black;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

        cancel_btn.clicked.connect(self.close)
        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.proceed)
        btn_layout.addWidget(enter_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(cancel_btn)

        frame_layout.addLayout(btn_layout)

        # Add frame to main layout
        main_layout.addWidget(frame)
    def proceed(self):
        if self.input_field.text():
            self.gear_ration_sgl.emit(float(self.input_field.text().strip()))
            self.close()
        else:
            QMessageBox.critical(self,"Empty Cell","Please enter the gear ratio")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GearRatioWindow()
    window.show()
    sys.exit(app.exec())