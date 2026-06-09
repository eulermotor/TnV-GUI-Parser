import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog,QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence
import os
class VehicleConfigWindow(QWidget):
    dbc_file_location = Signal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Config")
        self.resize(400, 100)
        self.path_new = None
        # --- DBC file upload ---
        dbc_label = QLabel("Add your DBC file:")

        self.dbc_input = QLineEdit()
        self.dbc_input.setPlaceholderText("Select .dbc file")

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_dbc)
        # if self.dbc_input.text():
        #     self.path_new = self.dbc_input.text()
        dbc_layout = QHBoxLayout()
        dbc_layout.addWidget(self.dbc_input)
        dbc_layout.addWidget(browse_btn)

        # --- Buttons (Enter & Cancel) ---
        self.enter_btn = QPushButton("Enter")
        self.enter_btn.clicked.connect(self.proceed)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.exit_n)
        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.proceed)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.enter_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.setAlignment(Qt.AlignCenter)  # center buttons

        # --- Main layout ---
        main_layout = QVBoxLayout()
        main_layout.addSpacing(10)
        main_layout.addWidget(dbc_label)
        main_layout.addLayout(dbc_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def browse_dbc(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select DBC File", "", "DBC Files (*.dbc)"
        )
        if file_path:
            self.path_new = file_path
            self.dbc_input.setText(file_path)
        # if self.dbc_input.:
        #     self.path_new = self.dbc_input.text()
        
    def proceed(self):
        if self.dbc_input.text():
            self.path_new = self.dbc_input.text()
            if os.path.exists(self.path_new):
                self.dbc_file_location.emit(self.path_new)
                self.close()
            else:
                QMessageBox.critical(self,"Invalid path.","Enter a valid path.")
        else:
            QMessageBox.critical(self,"Empty Cell!!","Select the DBC first.")
    def exit_n(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VehicleConfigWindow()
    window.show()
    sys.exit(app.exec())
    