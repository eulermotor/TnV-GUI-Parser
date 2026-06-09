from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QStatusBar, QSizePolicy,QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize,QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QColor


class vehicletype(QWidget):
    vehicle_signal = Signal(str)
    # def __init__(self):
    #     super().__init__()
        
    #     vehicle_layout = QHBoxLayout(vehicle_type)
        
    #     # ===== FORM CONTAINER =====
    #     form_container = QWidget()
    #     form_container.setObjectName("formContainer")

    #     form_layout = QVBoxLayout()
    #     # creating button
    #     four_W = QPushButton("4W")
    #     four_W.setFixedWidth(200)
    #     four_W.clicked.connect(self.four_wheel)
    #     three_W = QPushButton("3W")
    #     three_W.setFixedWidth(200)
    #     three_W.clicked.connect(self.three_wheel)
    #     vehicle_layout.addWidget(four_W)
    #     vehicle_layout.addSpacing(20)
    #     vehicle_layout.addWidget(three_W)
    #     # main_layout = QVBoxLayout(self)
    #     # main_layout.setContentsMargins(0, 0, 0, 0)

        
    #     # ===== TITLE =====
    #     title = QLabel("Select the Vehicle Type")
    #     title.setAlignment(Qt.AlignCenter)
    #     title.setStyleSheet("font-size: 35px; font-weight: bold; color: white")
    #     form_layout.addWidget(title)
    #     form_layout.addSpacing(20)
    #     form_layout.addWidget(vehicle_type, alignment=Qt.AlignCenter)
    #     form_container.setLayout(form_layout)
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # ===== TITLE =====
        title = QLabel("Select the Vehicle Type")
        title.setAlignment(Qt.AlignCenter)
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(40)
        # shadow.setXOffset(3)           # Horizontal displacement
        # shadow.setYOffset(3)           # Vertical displacement
        # shadow.setColor(QColor(0, 0, 0, 255))
        title.setStyleSheet("font-size: 35px; font-weight: bold; color: #808080; padding: 5px")#808080
        # title.setGraphicsEffect(shadow)
        # ===== BUTTON LAYOUT =====
        button_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                border: 2px solid #444;
                border-radius: 15px;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
                min-width: 120px;
                min-height: 60px;
                background-color: #f5f5f5;
            }
            QPushButton:hover {
                background-color: #cce5ff;
            }
        """
        four_W = QPushButton("4W")
        four_W.setFixedWidth(200)
        four_W.clicked.connect(self.four_wheel)

        three_W = QPushButton("3W")
        three_W.setFixedWidth(200)
        three_W.clicked.connect(self.three_wheel)
        four_W.setStyleSheet(button_style)
        three_W.setStyleSheet(button_style)
        button_layout.addStretch()
        button_layout.addWidget(four_W)
        button_layout.addSpacing(150)
        button_layout.addWidget(three_W)
        button_layout.addStretch()
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(20)
        # shadow.setOffset(0, 0)
        # title.setGraphicsEffect(shadow)

        # ===== ADD TO MAIN =====
        # main_layout.addStretch()
        main_layout.addSpacing(100)  # push from top slightly
        main_layout.addWidget(title_container)

        main_layout.addSpacing(60)  # space between title and buttons
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def four_wheel(self):
        print("4W selected!")
        self.vehicle_signal.emit("4W")   # ✅ emit signal

    def three_wheel(self):
        print("3W selected!")
        self.vehicle_signal.emit("3W")   # ✅ emit signal
    