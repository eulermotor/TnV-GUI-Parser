import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,QMessageBox
)
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QDoubleValidator

class BatteryWindow(QWidget):
    battery_signal = Signal(str,float,float,float)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Battery Details")
        self.setFixedSize(500, 300)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Outer box
        frame = QFrame()
        # frame.setFrameShape(QFrame.Box)
        # frame.setLineWidth(2)

        frame_layout = QVBoxLayout(frame)

        # Title
        title = QLabel("Enter Battery details:")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        frame_layout.addWidget(title)

        # Grid layout
        grid = QGridLayout()
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(10)
        #accepting only float values
        validator = QDoubleValidator(0.0,600.0,2)
        validator.setNotation(QDoubleValidator.StandardNotation)

        labels = [
            "Battery Name:",
            "Battery Model (KW):",
            "Battery Voltage (V):",
            "Battery Capacity (Ah):"
        ]

        self.inputs = []

        for i, text in enumerate(labels):
            label = QLabel(text)
            input_field = QLineEdit()

            input_field.setFixedHeight(28)

            # ❌ Removed border (clean look)
            # input_field.setStyleSheet("""
            #     QLineEdit {
            #         border: none;
            #         border-bottom: 1px solid black;
            #         padding-left: 5px;
            #     }
            # """)
            if i > 0:
                input_field.setValidator(validator)
            if i == 0:
                input_field.setPlaceholderText("Enter battery name..")
            elif i==1:
                input_field.setPlaceholderText("Enter battery KW..")
            elif i==2:
                input_field.setPlaceholderText("Enter battery voltage..")
            elif i==3:
                input_field.setPlaceholderText("Enter battery capacity..")
            grid.addWidget(label, i, 0)
            grid.addWidget(input_field, i, 1)

            self.inputs.append(input_field)

        frame_layout.addLayout(grid)

        # Buttons in same line
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
        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.proceed)
        btn_layout.addWidget(enter_btn)
        btn_layout.addSpacing(50)
        btn_layout.addWidget(cancel_btn)
        frame_layout.addSpacing(20)
        frame_layout.addLayout(btn_layout)

        main_layout.addWidget(frame)

        # Button actions
        cancel_btn.clicked.connect(self.close)
    def proceed(self):
        flag = any(not x.text().strip() for x in self.inputs)
                
        if not flag:
            name = self.inputs[0].text().strip()
            model = float(self.inputs[1].text().strip())
            voltage = float(self.inputs[2].text().strip())
            capacity = float(self.inputs[3].text().strip())
            self.battery_signal.emit(name,model,voltage,capacity)
            self.close()
        else:
            QMessageBox.critical(self,"Empty Cell","Fill-up all the cells")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatteryWindow()
    window.show()
    sys.exit(app.exec())