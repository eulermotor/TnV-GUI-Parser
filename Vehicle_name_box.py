import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QLabel,
    QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout,QMessageBox
)
from PySide6.QtCore import Signal,QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
class VehicleInputBox(QDialog):
    vehicle_name_manual = Signal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Input")

        # Label
        label = QLabel("Enter vehicle name:")

        # Text box
        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Type here...")
        self.textbox.setFixedHeight(20)
        self.textbox.setFixedWidth(370)
        regex = QRegularExpression("^[a-zA-Z0-9-]*$")

        # Attach it to your line edit
        validator = QRegularExpressionValidator(regex, self.textbox)
        self.textbox.setValidator(validator)
        # Buttons
        enter_button = QPushButton("Enter")
        self.cancel_button = QPushButton("Cancel")
        enter_button.clicked.connect(self.takevariable)
        self.cancel_button.clicked.connect(self.exit_now)
        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(enter_button)
        button_layout.addWidget(self.cancel_button)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.textbox)
        layout.addLayout(button_layout)

        self.setLayout(layout)
    def takevariable(self):
        self.name_to_send = self.textbox.text().strip()
        if self.name_to_send:
            self.vehicle_name_manual.emit(self.name_to_send)
            self.close()
        else:
            QMessageBox.critical(self,"Empty Cell!!","Enter vehicle name")
    def exit_now(self):
        self.close()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VehicleInputBox()
    window.show()
    sys.exit(app.exec())