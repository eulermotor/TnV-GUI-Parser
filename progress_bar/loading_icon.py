import sys
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QColor, QMovie
from PySide6.QtCore import QTimer, QSize, Qt
import os
# Assuming your WaitingSpinner is saved in spinner.py
from .spinner import WaitingSpinner 

class CreatingIcon(QWidget):
    def __init__(self,number):
        super().__init__()
        
        # self.setWindowTitle("Four State Circular Icon")
        # self.resize(200, 200)

        # 1. Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. Setup the Stacked Widget (Our 30x30px Circular Container)
        self.circular_container = QStackedWidget()
        self.circular_container.setFixedSize(30, 30)
        main_layout.addWidget(self.circular_container)

        # --- STATE 1: Grey Label ---
        self.label_grey = QLabel(str(number))
        self.label_grey.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_grey.setStyleSheet("""
            QLabel {
                border-radius: 15px;
                background-color: grey;
                color: black;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid black;
            }
        """)

        # --- STATE 2: Waiting Spinner ---
        # Adjusted radius and line_length so (5 + 5) * 2 = 20px (Fits inside 30px)
        self.spinner = WaitingSpinner(
            self.circular_container,
            center_on_parent=True,
            roundness=100.0,
            fade=80.0,
            radius=8,                 
            lines=100,                 
            line_length=5,
            line_width=2,
            speed=1.5,
            color=QColor(85, 255, 0)
        )

        # --- STATE 3: Tick Animation ---
        self.tick_label = QLabel()
        self.tick_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_dir = os.path.dirname(__file__)
        tick_path = os.path.join(current_dir, "tick.gif")

        self.movie = QMovie(tick_path)
        # self.movie = QMovie("tick.gif")
        self.movie.setScaledSize(QSize(30, 30)) # Scale GIF to fit container
        self.tick_label.setMovie(self.movie)

        # --- STATE 4: Green Label ---
        self.label_green = QLabel(str(number))
        self.label_green.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_green.setStyleSheet("""
            QLabel {
                border-radius: 15px;
                background-color: #66FF66;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        # 3. Add all states to the Stacked Widget
        self.circular_container.addWidget(self.label_grey)   # Index 0
        self.circular_container.addWidget(self.spinner)      # Index 1
        self.circular_container.addWidget(self.tick_label)   # Index 2
        self.circular_container.addWidget(self.label_green)  # Index 3

        # 4. Setup Timer for the 500ms delay transitions
        self.current_state = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # 500ms
        self.timer.timeout.connect(self.next_state)

        # Start the sequence
        self.run_sequence()

    def run_sequence(self):
        """Starts the animation sequence from the beginning."""
        self.current_state = 0
        self.circular_container.setCurrentIndex(self.current_state)
        self.timer.start()

    def next_state(self):
        """Advances to the next widget in the stack."""
        self.current_state += 1

        # Handle specific actions per state
        if self.current_state == 1:
            self.spinner.start()
        elif self.current_state == 2:
            self.spinner.stop()
            self.movie.start()
        elif self.current_state == 3:
            self.movie.stop()
        
        # If we reach the end, stop the timer
        if self.current_state >= self.circular_container.count():
            self.timer.stop()
            return

        # Show the current state
        self.circular_container.setCurrentIndex(self.current_state)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = CreatingIcon()
#     window.show()
#     sys.exit(app.exec())