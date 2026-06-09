import sys
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QThread, Signal, Qt

# Assuming icon_creator.py lives in subfolder 'progress_bar/'
from progress_bar.StepIcon import StepIcon 
from backend.vortex_new import ProcessingWorker

# ========================================================
# 2. THE MAIN UI CONTAINER
# ========================================================
class ProgressBarMain(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Backend Link Test")
        # self.resize(800, 300)
        
        # Apply black background as seen in your image
        # self.setStyleSheet("background-color: black;")

        # Main Layout
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- White Container (Your UI Panel) ---
        self.ui_panel = QWidget()
        self.ui_panel.setStyleSheet("""
            QWidget#ui_panel {
                background-color: white; 
                border-radius: 10px;
                padding: 10px;
            }
            QLabel { color: black; font-size: 12px; font-weight: bold;}
        """)
        # We need an explicit objectName to apply the CSS ID selector
        self.ui_panel.setObjectName("ui_panel")
        
        self.panel_layout = QHBoxLayout(self.ui_panel)
        self.panel_layout.setContentsMargins(15, 10, 15, 10)
        self.panel_layout.setSpacing(20) # Space between checkpoints

        # ------------------------------------------------------------------
        # Create Checkpoints to match image (Object Approach)
        # ------------------------------------------------------------------
        # Stores [ (StepIcon_Object, Label_Object), ... ]
        self.checkpoints = [] 

        checkpoint_data = [
            ("1", "Fetching .trc files"),
            ("2", "Creating .csv files"),
            ("3", "Merging files"),
            ("4", "Pcan.csv generated")
        ]

        for number_str, text_str in checkpoint_data:
            checkpoint_container = QWidget()
            cp_lay = QVBoxLayout(checkpoint_container)
            cp_lay.setContentsMargins(0,0,0,0)
            cp_lay.setSpacing(5)
            
            # 1. Create the custom Icon Widget
            icon = StepIcon(number_str)
            cp_lay.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
            
            # 2. Create the text label
            label = QLabel(text_str)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True) # Helps long text
            label.setMinimumWidth(100)
            cp_lay.addWidget(label)
            
            self.panel_layout.addWidget(checkpoint_container)
            
            # Add to list for easy access via ID
            self.checkpoints.append(icon)

        self.root_layout.addWidget(self.ui_panel)

        # ========================================================
        # 3. WORKER THREAD SETUP
        # ========================================================
        self.worker = ProcessingWorker()
        self.worker.job_starting.connect(self.on_job_started)
        self.worker.job_completed.connect(self.on_job_completed)

        # self.worker_thread = WorkerThread()

        # Connect Worker Signals to UI Slots (The Link)
        # ---------------------------------------------
        # worker.job_starting(0) -> self.on_job_started(0)
        # self.worker_thread.job_starting.connect(self.on_job_started)
        
        # # worker.job_completed(0) -> self.on_job_completed(0)
        # self.worker_thread.job_completed.connect(self.on_job_completed)
        
        # worker.finished -> self.on_all_jobs_done (built-in QThread signal)
        self.worker.finished.connect(self.on_all_jobs_done)

        # Start button to trigger backend
        self.start_btn = QPushButton("Simulate Backend Job Start")
        self.start_btn.setStyleSheet("background-color: white; color: black; padding: 10px;")
        self.start_btn.clicked.connect(self.start_process)
        self.root_layout.addWidget(self.start_btn, 0, Qt.AlignmentFlag.AlignCenter)

    # ========================================================
    # UI SLOTS (These run on main thread)
    # ========================================================
    def start_process(self):
        """Starts the background thread."""
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Parsing Started...")
        
        # Reset all icons to grey before starting
        for icon in self.checkpoints:
            icon.reset()
            
        # Start background loop
        self.worker.start()

    def on_job_started(self, job_index_id):
        """Slot: called when worker signals job start."""
        # Find the correct StepIcon object in our list and command it
        # Safety check: ensure id is within valid range of list
        if 0 <= job_index_id < len(self.checkpoints):
            icon_object = self.checkpoints[job_index_id]
            icon_object.set_running() # Command icon to spin

    def on_job_completed(self, job_index_id):
        """Slot: called when worker signals job success."""
        if 0 <= job_index_id < len(self.checkpoints):
            icon_object = self.checkpoints[job_index_id]
            icon_object.set_done() # Command icon to stop, go green

    def on_all_jobs_done(self):
        """Slot: called when whole thread ends."""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Process Finished. Click to restart.")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ProgressBarMain()
#     window.show()
#     sys.exit(app.exec())