# from PySide6.QtWidgets import QApplication,QMainWindow
# import sys
# from controller import MainController

# from PySide6.QtGui import QPalette, QColor
# from PySide6.QtCore import Qt
# # QApplication.setDesktopSettingsAware(False)
# def apply_light_theme(app):
#     # Create a fresh palette
#     palette = QPalette()
    
#     # Define standard Light Mode colors
#     white = QColor(255, 255, 255)
#     black = QColor(0, 0, 0)
#     light_gray = QColor(240, 240, 240)
#     dark_gray = QColor(100, 100, 100)
#     blue_highlight = QColor(0, 120, 215)

#     # Apply colors to roles
#     palette.setColor(QPalette.Window, light_gray)
#     palette.setColor(QPalette.WindowText, black)
#     palette.setColor(QPalette.Base, white)
#     palette.setColor(QPalette.AlternateBase, light_gray)
#     palette.setColor(QPalette.ToolTipBase, white)
#     palette.setColor(QPalette.ToolTipText, black)
#     palette.setColor(QPalette.Text, black)
#     palette.setColor(QPalette.Button, light_gray)
#     palette.setColor(QPalette.ButtonText, black)
#     palette.setColor(QPalette.BrightText, Qt.red)
#     palette.setColor(QPalette.Link, blue_highlight)
#     palette.setColor(QPalette.Highlight, blue_highlight)
#     palette.setColor(QPalette.HighlightedText, white)
    
#     # These roles are often why fonts "disappear" in Dark Mode
#     palette.setColor(QPalette.Disabled, QPalette.Text, dark_gray)
#     palette.setColor(QPalette.Disabled, QPalette.WindowText, dark_gray)
#     palette.setColor(QPalette.Disabled, QPalette.ButtonText, dark_gray)

#     app.setPalette(palette)
# app = QApplication(sys.argv)
# app.setStyle("Fusion")
# apply_light_theme(app)
# window = MainController()
# window.show()

# app.exec()
import os
import sys

# --- STEP 1: FORCE GRAPHICS & THEME IMMEDIATELY ---
# This tells Windows 11 "Don't even try to use Dark Mode" at the OS level
os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"
# Force a stable rendering engine to prevent driver-search timeouts
os.environ["QT_RHI_BACKEND"] = "d3d11"

# from PySide6.QtWidgets import QApplication, QMainWindow, QSplashScreen
# from PySide6.QtGui import QPalette, QColor, QPixmap
# from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSplashScreen, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QPixmap, QColor, QPalette
from PySide6.QtCore import Qt, QSize
def apply_light_theme(app):
    palette = QPalette()
    # Define standard Light Mode colors
    white = QColor(255, 255, 255)
    black = QColor(0, 0, 0)
    light_gray = QColor(240, 240, 240)
    dark_gray = QColor(100, 100, 100)
    blue_highlight = QColor(0, 120, 215)

    # Apply colors to roles
    palette.setColor(QPalette.Window, light_gray)
    palette.setColor(QPalette.WindowText, black)
    palette.setColor(QPalette.Base, white)
    palette.setColor(QPalette.AlternateBase, light_gray)
    palette.setColor(QPalette.ToolTipBase, white)
    palette.setColor(QPalette.ToolTipText, black)
    palette.setColor(QPalette.Text, black)
    palette.setColor(QPalette.Button, light_gray)
    palette.setColor(QPalette.ButtonText, black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, blue_highlight)
    palette.setColor(QPalette.Highlight, blue_highlight)
    palette.setColor(QPalette.HighlightedText, white)
    
    # These roles are often why fonts "disappear" in Dark Mode
    palette.setColor(QPalette.Disabled, QPalette.Text, dark_gray)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, dark_gray)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, dark_gray)
    app.setPalette(palette)
class ModernSplash(QSplashScreen):
    def __init__(self):
        # Create a plain white pixmap for the "block"
        # Adjust 400, 200 to whatever size you want the white card to be
        card_size = QSize(400, 250)
        pixmap = QPixmap(card_size)
        pixmap.fill(Qt.white)
        super().__init__(pixmap)

        # Create a layout to hold your logo and text
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        # 1. Add the Logo (Scaled down)
        self.logo_label = QLabel()
        logo_full_path = resource_path("euler-motors-logo-hd.png")
        logo_pix = QPixmap(logo_full_path)
        # Scale the logo so it doesn't break the small white block
        scaled_logo = logo_pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_logo)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("background: transparent; border: none;")
        self.layout.addWidget(self.logo_label)

        # 2. Add the Message Label
        self.msg_label = QLabel("Initializing Parser...")
        # self.msg_label.setStyleSheet("color: #333333; font-family: Segoe UI; font-size: 14px; font-weight: bold;")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #333333;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 400;
            }
        """)
        self.layout.addWidget(self.msg_label)

        # Apply a thin, light gray border ONLY to the main container (the splash itself)
        # We use 'QSplashScreen' as a selector so it doesn't apply to the labels inside
        self.setStyleSheet("""
            QSplashScreen {
                border: 1px solid #D1D1D1;
                background-color: white;
            }
        """)
        
        # Add a subtle border to the white block so it stands out on light backgrounds
        self.setStyleSheet("border: 1px solid #CCCCCC;")

    def show_message(self, text):
        self.msg_label.setText(text)
        QApplication.processEvents()
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
if __name__ == "__main__":
    # --- STEP 2: SHOW SOMETHING INSTANTLY ---
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_light_theme(app)
    # check_path = resource_path("check-mark.png")
    check_path = resource_path("check-mark.png").replace("\\", "/")
    app.setStyleSheet(f"""
        QCheckBox {{
            color: #000000;
        }}
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border: 1px solid #666666;
            background-color: #ffffff;
            border-radius: 2px;
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid #0078D7;
        }}
        QCheckBox::indicator:checked {{
            background-color: #ffffff;
            border: 1px solid #000000;
            image: url("{check_path}");
        }}
    """)
    
    splash = ModernSplash()
    splash.show()
    
    # --- Start Heavy Imports ---
    # Force the UI to draw the splash/theme immediately
    
    splash.show_message("Loading Data Libraries...")
    app.processEvents()
    # --- STEP 3: LAZY IMPORT ---
    # Only import the controller AFTER the app has initialized its basic state
    from controller import MainController
    splash.show_message("Done!")
    window = MainController()
    window.show()
    splash.finish(window)
    
    
    sys.exit(app.exec())