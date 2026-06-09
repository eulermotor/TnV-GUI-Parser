from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QStatusBar, QSizePolicy,QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize,QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence
import sys
import os



# class LoginScreen(QWidget):
#     login_success = Signal(str, str)  # name, email
#     def __init__(self):
#         super().__init__()
#         self.setStatusBar(QStatusBar(self))

#         # ===== CENTRAL WIDGET =====
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         central_widget.setObjectName("Central_Widget")
#         outer_layout = QVBoxLayout()
#         outer_layout.addStretch()

#         # ===== FORM CONTAINER =====
#         form_container = QWidget()
#         form_container.setObjectName("formContainer")
#         form_layout = QVBoxLayout()

#         # Title
#         title = QLabel("WELCOME!")
#         title.setAlignment(Qt.AlignCenter)
#         title.setStyleSheet("font-size: 35px; font-weight: bold;")
#         subtitle = QLabel("Enter your Credentials.")
#         subtitle.setAlignment(Qt.AlignCenter)
#         subtitle.setStyleSheet("font-size: 25px")
        
        
#         # Left side (temporary message area)
#         self.status_label = QLabel("ver 1.0")
#         self.statusBar().addWidget(self.status_label)
#         # Right side (permanent widget)
#         author_label = QLabel("by Vinayak Kushwah")
#         self.statusBar().addPermanentWidget(author_label)
#         self.statusBar().setStyleSheet("""
#             QStatusBar {
#                 border-top: 1px solid gray;
#                 padding: 2px;
#             }
#         """)
#         # ===== GRID =====
#         grid = QGridLayout()
#         grid.setHorizontalSpacing(10)
#         grid.setVerticalSpacing(10)

#         label_width = 140

#         # Name
#         name_label = QLabel("Name:")
#         name_label.setFixedWidth(label_width)

#         self.name_input = QLineEdit()
#         self.name_input.setPlaceholderText("Text..")
#         self.name_input.setFixedWidth(250)

#         # Email
#         email_label = QLabel("Enter your mail ID:")
#         email_label.setFixedWidth(label_width)

#         self.email_input = QLineEdit()
#         self.email_input.setPlaceholderText("Text..")
#         self.email_input.setFixedWidth(250)
#         # email = None
#         # try:
#         #     if email_input.endswith("*@eulermotors.com"):
#         #         email = email_input
#         # except:
#         #     print("Write company mail ID")
#         # Subtext
#         subtext = QLabel("(enter company mail ID only)")
#         subtext.setStyleSheet("font-size: 10px; color: gray;")

#         # Add to grid
#         grid.addWidget(name_label, 0, 0)
#         grid.addWidget(self.name_input, 0, 1)

#         grid.addWidget(email_label, 1, 0)
#         grid.addWidget(self.email_input, 1, 1)

#         grid.addWidget(subtext, 2, 1)  # perfectly under input

#         # Button
#         enter_btn = QPushButton("Enter")
#         enter_btn.setFixedWidth(100)
#         enter_btn.clicked.connect(self.validate_email)
#         form_container.setStyleSheet("""
#             #formContainer {
#                 border: 2px solid gray;
#                 border-radius: 10px;
#                 background-color: #f5f5f5;
#             }
#         """)
#         shortcut = QShortcut(QKeySequence("Return"), self)
#         shortcut.activated.connect(self.validate_email)
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(20)
#         shadow.setOffset(0, 0)
#         form_layout.setContentsMargins(30, 30, 30, 30)
#         form_container.setGraphicsEffect(shadow)
#         # Assemble form
#         form_layout.addWidget(title)
#         # form_layout.addSpacing(10)
#         form_layout.addWidget(subtitle)
#         form_layout.addSpacing(20)
#         form_layout.addLayout(grid)
#         form_layout.addSpacing(20)
#         form_layout.addWidget(enter_btn, alignment=Qt.AlignCenter)

#         form_container.setLayout(form_layout)

#         # ===== CENTERING =====
#         h_layout = QHBoxLayout()
#         h_layout.addStretch()
#         h_layout.addWidget(form_container)
#         h_layout.addStretch()

#         outer_layout.addLayout(h_layout)
#         outer_layout.addStretch()

#         central_widget.setLayout(outer_layout)
#         fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
#         fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
#         central_widget.setStyleSheet("""
#             #Central_Widget {
#                 border-image: url("grp1.png") 0 0 0 0 stretch stretch;
#             }
#         """)
#         self.setFixedSize(900, 600)
        
#     # ===== FUNCTIONS =====
#     def quit(self):
#         self.app.quit()

#     def add_vehicle(self):
#         print("vehicle add window!!")

#     def add_DBC(self):
#         print("DBC add window!!")

#     def themes(self):
#         print("Theme select window")

#     def fontsize(self):
#         print("Set font size")

#     def autosync(self):
#         print("Auto sync")

#     # def toolbar_connect(self):
#     #     self.statusBar().showMessage("Connecting...",3000)

#     # def png_connect(self):
#     #     self.statusBar().showMessage("redirecting to home....",3000)
#     def toggle_fullscreen(self):
#         if self.isFullScreen():
#             self.showNormal()
#             self.setFixedSize(900, 600)  # restore fixed size
#         else:
#             self.showFullScreen()
#     def validate_email(self):
#         name = self.name_input.text()
#         email = self.email_input.text()

#         if not email.endswith("@eulermotors.com"):
#             self.status_label.setText("Write company mail ID")
#             self.status_label.setStyleSheet("color: red;")
#             QTimer.singleShot(3000, self.reset_status)
#             return

#         self.status_label.setText("Valid company email")
#         self.status_label.setStyleSheet("color: green;")
#         QTimer.singleShot(3000, self.reset_status)
#         self.login_success.emit(name, email)
#     def reset_status(self):
#         self.status_label.setText("ver 1.0")
#         self.status_label.setStyleSheet("color: black;")



class LoginScreen(QWidget):
    login_success = Signal(str, str)

    def __init__(self):
        super().__init__()
        bg_widget = QWidget()
        bg_widget.setObjectName("Central_Widget")

        bg_layout = QVBoxLayout(bg_widget)
        # ===== MAIN LAYOUT =====
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(bg_widget)
        # ===== FORM CONTAINER =====
        form_container = QWidget()
        form_container.setObjectName("formContainer")

        form_layout = QVBoxLayout()

        # ===== TITLE =====
        title = QLabel("WELCOME!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 35px; font-weight: bold;")

        subtitle = QLabel("Enter your Credentials.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 20px;")
        

        # ===== GRID =====
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        label_width = 140

        # Name
        name_label = QLabel("Name:")
        name_label.setFixedWidth(label_width)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Text..")
        self.name_input.setFixedWidth(250)

        # Email
        email_label = QLabel("Enter your mail ID:")
        email_label.setFixedWidth(label_width)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Text..")
        self.email_input.setFixedWidth(250)

        # Subtext
        subtext = QLabel("(enter company mail ID only)")
        subtext.setStyleSheet("font-size: 10px; color: gray;")

        # Add to grid
        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self.name_input, 0, 1)

        grid.addWidget(email_label, 1, 0)
        grid.addWidget(self.email_input, 1, 1)

        grid.addWidget(subtext, 2, 1)

        # ===== BUTTON =====
        enter_btn = QPushButton("Enter")
        enter_btn.setFixedWidth(100)
        enter_btn.clicked.connect(self.validate_email)

        # Enter key support
        
        self.name_input.returnPressed.connect(self.validate_name)
       
        self.email_input.returnPressed.connect(self.validate_email)
        # ===== STYLE =====
        form_container.setStyleSheet("""
            #formContainer {
                border: 2px solid gray;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        form_container.setGraphicsEffect(shadow)

        form_layout.setContentsMargins(30, 30, 30, 30)

        # ===== ASSEMBLE FORM =====
        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(20)
        form_layout.addLayout(grid)
        form_layout.addSpacing(20)
        form_layout.addWidget(enter_btn, alignment=Qt.AlignCenter)

        form_container.setLayout(form_layout)

        # ===== CENTER FORM =====
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_container)
        center_layout.addStretch()

        # main_layout.addStretch()
        # main_layout.addLayout(center_layout)
        # main_layout.addStretch()
        bg_layout.addStretch()
        bg_layout.addLayout(center_layout)
        bg_layout.addStretch()
        
        # ===== FOOTER =====
        footer_layout = QHBoxLayout()

        self.status_label = QLabel("ver 1.0")
        self.status_label.setStyleSheet("padding: 4px; color: white;font-size: 10px;font-weight: bold;")

        author_label = QLabel("by Vinayak Kushwah")
        author_label.setStyleSheet("color: white;font-size: 10px;font-weight: bold;")
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(author_label)

        footer_widget = QWidget()
        footer_widget.setLayout(footer_layout)
        footer_widget.setStyleSheet("""
            QWidget {
                border-top: 1px white;
            }
        """)
        
        # main_layout.addWidget(footer_widget)
        bg_layout.addWidget(footer_widget)
        # # ===== BACKGROUND =====
        # # self.setObjectName("LoginScreen")
        # center_layout.setObjectName("Central_Widget")
        # center_layout.setStyleSheet("""
        #     #Central_Widget {
        #         border-image: url("grp1.png") 0 0 0 0 stretch stretch;
        #     }
        # """)
        bg_widget.setStyleSheet(f"""
            #Central_Widget {{
                border-image: url({self.get_resource("grp1.png").replace('\\', '/')}) 0 0 0 0 stretch stretch;
            }}
        """)
        
    def get_resource(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        # This checks if the code is running as an EXE (_MEIPASS) or as a script
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    # ===== VALIDATION =====
    def validate_email(self):
        name = self.name_input.text()
        email = self.email_input.text()

        if not email.endswith("@eulermotors.com"):
            self.status_label.setText("Write company mail ID")
            self.status_label.setStyleSheet("color: red;")
            QTimer.singleShot(3000, self.reset_status)
            return

        self.status_label.setText("Valid company email")
        self.status_label.setStyleSheet("color: green;")
        QTimer.singleShot(3000, self.reset_status)

        self.login_success.emit(name, email)
    def  validate_name(self):
        if not self.name_input.text():
            self.status_label.setText("Name cell empty")
            self.status_label.setStyleSheet("color: red;")
            QTimer.singleShot(3000, self.reset_status)
            return
        else:
            self.email_input.setFocus()
    def reset_status(self):
        self.status_label.setText("ver 1.0")
        self.status_label.setStyleSheet("color: white;font-size: 10px;font-weight: bold;")
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.setFixedSize(900, 600)  # restore fixed size
        else:
            self.showFullScreen()
    
