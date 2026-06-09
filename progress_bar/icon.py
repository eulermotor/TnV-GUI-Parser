# Save this file inside your subfolder, e.g., 'progress_bar/StepIcon.py'
import sys
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedLayout, QApplication
from PySide6.QtGui import QColor, QMovie, QPainter, QPen
from PySide6.QtCore import Qt, QSize,QTimer
import os
# Using the relative import (Recommended)
from .spinner import WaitingSpinner 
class RoundLabel(QLabel):
    def __init__(self, text, bg_color, border_color=None, parent=None):
        super().__init__(text, parent)
        self.bg_color = QColor(bg_color)
        self.border_color = QColor(border_color) if border_color else QColor(bg_color)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        # THIS IS THE MAGIC LINE FOR QUALITY
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Background Circle
        painter.setBrush(self.bg_color)
        painter.setPen(QPen(self.border_color, 2))
        
        # Draw slightly inside the rect to avoid clipping at the edges
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawEllipse(rect)
        
        # Draw Text (calling super().paintEvent might mess up the circle, 
        # so we draw text manually)
        painter.setPen(QColor("black") if self.bg_color == QColor("grey") else QColor("white"))
        font = self.font()
        font.setBold(True)
        font.setPointSize(10) # 14px might be too big for a 30px circle with a border
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
class StepIcon(QWidget):
    def __init__(self, number_str, parent=None):
        super().__init__(parent)
        self.number_text = str(number_str)
        # self.timer = QTimer
        # This container fixes the visual size to 30x30px
        self.setFixedSize(30, 30)
        
        # QStackedLayout: best for flipping between different 'views' in same spot
        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)
        
        # ===============================================
        #  VIEW 1: INITIAL STATE (Grey Label with number)
        # ===============================================
        self.label_grey = RoundLabel(self.number_text, "grey", "black")
        self.label_grey.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.label_grey.setStyleSheet("""
        #     QLabel {
        #         border-radius: 15px; 
        #         background-color: grey;
        #         color: black;
        #         font-weight: bold;
        #         font-size: 14px;
        #         border: 2px solid black;
        #     }
        # """)
        
        # ===============================================
        #  VIEW 2: RUNNING STATE (Spinner)
        # ===============================================
        self.spinner_container = QWidget()
        # Adjusted radius/line so total size (5+5)*2 = 20px (fits in 30px container)
        self.spinner = WaitingSpinner(
            self.spinner_container,
            center_on_parent=True,
            fade=80.0,
            radius=8,                 
            lines=100,                 
            line_length=5,
            line_width=2,
            speed=1.5,
            color=QColor(85, 255, 0)
        )
        # The spinner needs explicit parenting and start() to show up
        # --- STATE 3: Tick Animation ---
        self.tick_label = QLabel()
        self.tick_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # current_dir = os.path.dirname(__file__)
        # tick_path = os.path.join(current_dir, "tick.gif")
        tick_path = self.get_resource("progress_bar/tick.gif")
        self.movie1 = QMovie(tick_path)
        self.movie1.setScaledSize(QSize(30, 30)) # Scale GIF to fit container
        self.tick_label.setMovie(self.movie1)

        # --- STATE 3: wrong Animation ---
        self.wrong_label = QLabel()
        self.wrong_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wrong_path = self.get_resource("progress_bar/wrong.gif")

        self.movie2 = QMovie(wrong_path)
        self.movie2.setScaledSize(QSize(30, 30)) # Scale GIF to fit container
        self.wrong_label.setMovie(self.movie2)
        # ===============================================
        #  VIEW 3: DONE STATE (Green Label with number)
        # ===============================================
        self.label_green = RoundLabel(self.number_text, "#00CC00", "white")
        # self.label_green.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.label_green.setStyleSheet("""
        #     QLabel {
        #         border-radius: 15px;
        #         background-color: #66FF66; 
        #         color: white;
        #         font-weight: bold;
        #         font-size: 14px;
        #     }
        # """)
        self.label_red = RoundLabel(self.number_text, "#FF6666", "white")
        # self.label_red.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.label_red.setStyleSheet("""
        #     QLabel {
        #         border-radius: 15px;
        #         background-color: #FF6666; 
        #         color: white;
        #         font-weight: bold;
        #         font-size: 14px;
        #     }
        # """)

        # Add them to stack
        self.stack.addWidget(self.label_grey)   # Index 0
        self.stack.addWidget(self.spinner_container) # Index 1
        self.stack.addWidget(self.tick_label) # Index 2
        self.stack.addWidget(self.label_green)  # Index 3
        self.stack.addWidget(self.wrong_label)  # Index 4
        self.stack.addWidget(self.label_red)  # Index 5
        
        # Initial View: Grey Label
        self.stack.setCurrentIndex(0)
    def get_resource(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        # This checks if the code is running as an EXE (_MEIPASS) or as a script
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)
    # ===============================================
    # External Commands (No Internal Timers!)
    # ===============================================
    def set_running(self):
        """CMD from backend: Start spinning."""
        self.stack.setCurrentIndex(1)
        self.spinner.start()

    def set_done(self):
        """CMD from backend: Job complete."""
        self.spinner.stop()
        self.movie1.start()
        self.stack.setCurrentIndex(2)
        # self.timer.singleShot(100,self.movie1.stop())
        # # self.stack.setCurrentIndex(3)
        # QTimer.singleShot(500, lambda: (self.movie1.stop(), self.stack.setCurrentIndex(3)))
        # Optional: If you want exactly ONE loop of the GIF:
        # Connect to the finished signal or a specific frame
        QTimer.singleShot(1000, self.transition_to_final)

    def transition_to_final(self):
        self.movie1.stop()
        self.stack.setCurrentIndex(3)
            
    def set_fail(self):
        self.spinner.stop()
        self.movie2.start()
        self.stack.setCurrentIndex(4)
        # self.timer.singleShot(100,self.movie2.stop())
        # QTimer.singleShot(500, lambda: (self.movie2.stop(), self.stack.setCurrentIndex(5)))
        # self.stack.setCurrentIndex(5)
        QTimer.singleShot(1000, self.transition_to_fail)

    def transition_to_fail(self):
        self.movie2.stop()
        self.stack.setCurrentIndex(5)
        
    def reset(self):
        """CMD from UI: Start over."""
        self.spinner.stop()
        self.stack.setCurrentIndex(0)

# # Optional test block (run this file directly to test logic)
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = QWidget()
#     win_lay = QVBoxLayout(window)
    
#     icon_test = StepIcon("1")
#     win_lay.addWidget(icon_test, 0, Qt.AlignmentFlag.AlignCenter)
    
#     # Test buttons
#     from PySide6.QtWidgets import QPushButton
#     btn1 = QPushButton("Run Step 1")
#     btn1.clicked.connect(icon_test.set_running)
#     win_lay.addWidget(btn1)
    
#     btn2 = QPushButton("Done Step 1")
#     btn2.clicked.connect(icon_test.set_done)
#     win_lay.addWidget(btn2)
    
#     window.show()
#     sys.exit(app.exec())