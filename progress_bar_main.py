from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QStatusBar, QSizePolicy,QGraphicsDropShadowEffect,QStackedWidget, QCheckBox,QMessageBox,QTextEdit
)
from PySide6.QtCore import Qt, QSize,QTimer, Signal,QObject
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence,QColor,QTextCursor
# from progress_bar.loading_icon import CreatingIcon
from progress_bar.icon import StepIcon
import os
import sys
from backend.vortex_new import ProcessingWorker
from backend.file_summarizer import ProcessingWorkersummary
from backend.file_summary_3w import ProcessingWorkersummary_3W
import pandas as pd
import collections
import threading
# from thirdMain_screen import EulerParserMain
# class TerminalRedirector(QObject):
#     text_written = Signal(str, str)

#     def __init__(self, color="black"):
#         super().__init__()
#         self.color = color

#     def write(self, text):
#         if text and text.strip():
#             self.text_written.emit(text, self.color)

#     def flush(self):
#         pass
import collections

class ThreadSafeLogger:
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock() # Prevents the "Thread::run" error

    def write(self, text, *args, **kwargs):
        if text:
            with self.lock:
                self.buffer.append(str(text))

    def flush(self):
        pass

    def get_all(self):
        with self.lock:
            if not self.buffer:
                return ""
            data = "".join(self.buffer)
            self.buffer = [] # Clear it out
            return data
class progressbar(QWidget):
    # progress_detail = Signal(str)
    progress_bar_sgl = Signal(int)
    def __init__(self,vehicle_name,trc_files,dbc_new_location,parsing_type,Tyre_size_name,DRR,bms_file_location,Battery_name,Battery_Model,Battery_Voltage,Battery_capacity,gear_ratio,flag_heatmap,flag_table,flag_google_upload,vehicle_varient,vehicle_of_choice,user_email):
        super().__init__()
        outer_layout = QVBoxLayout(self)
        self.setStyleSheet("""
                QPushButton { 
                            background-color: white; 
                            border: 1px solid #adb5bd; 
                            border-radius: 4px; 
                            padding: 6px 12px;
                            min-width: 120px;
                        }
                 QPushButton:hover { background-color: #e2e6ea; border-color: #007bff; }
        """
        )
        self.remarks = None
        self.V_type = vehicle_of_choice
        self.V_name = vehicle_name
        self.trc_list = trc_files
        self.dbc = dbc_new_location
        self.parsing = parsing_type
        self.tyresize = Tyre_size_name
        self.DRRn = DRR
        self.bms_loc = bms_file_location
        self.bat_name = Battery_name
        self.bat_model = Battery_Model
        self.bat_volt = Battery_Voltage
        self.bat_cap = Battery_capacity
        self.g_ratio = gear_ratio        
        self.heatmap = flag_heatmap
        self.table = flag_table
        self.api = flag_google_upload
        self.V_variants = vehicle_varient
        self.email = user_email
        dbc_name = os.path.splitext(os.path.basename(self.dbc))[0]
        self.main = QWidget()
        main_layout = QHBoxLayout(self.main)
        self.block_1 = QWidget()
        self.block_2 = QWidget()
        self.block_3 = QWidget()
        self.block_4 = QWidget()
        self.main.setObjectName("main")
        self.main.setMaximumHeight(300)
        self.main.setFixedWidth(700)
        one_layout = QVBoxLayout(self.block_1)
        two_layout = QVBoxLayout(self.block_2)
        three_layout = QVBoxLayout(self.block_3)
        four_layout = QVBoxLayout(self.block_4)
        self.block_1.setFixedSize(150,80)
        self.block_2.setFixedSize(150,80)
        self.block_3.setFixedSize(150,80)
        self.block_4.setFixedSize(150,80)
        self.flag_start_summary = 0
        self.abortion_flag = 0
        self.reparse_flag = 0
        self.first_widget = StepIcon("1")
        # first_widget.setObjectName("first")
        self.first_label = QLabel("")
        
        self.second_widget = StepIcon("2")
        # second_widget.setObjectName("second")
        self.second_label = QLabel("")
        
        self.third_widget = StepIcon("3")
        # third_widget.setObjectName("third")
        self.third_label = QLabel("")
        
        self.fourth_widget = StepIcon("4")
        # fourth_widget.setObjectName("fourth")
        self.fourth_label = QLabel("")

        one_layout.addWidget(self.first_widget, alignment=Qt.AlignCenter)
        one_layout.addWidget(self.first_label,alignment=Qt.AlignCenter)
        two_layout.addWidget(self.second_widget, alignment=Qt.AlignCenter)
        two_layout.addWidget(self.second_label,alignment=Qt.AlignCenter)
        three_layout.addWidget(self.third_widget, alignment=Qt.AlignCenter)
        three_layout.addWidget(self.third_label,alignment=Qt.AlignCenter)
        four_layout.addWidget(self.fourth_widget, alignment=Qt.AlignCenter)
        four_layout.addWidget(self.fourth_label,alignment=Qt.AlignCenter)
        self.worker = ProcessingWorker(self.trc_list,self.dbc,self.parsing)
        self.worker.job_starting.connect(self.on_job_started)
        self.worker.job_completed.connect(self.on_job_completed)
        self.worker.job_failed.connect(self.on_job_failure)
        self.worker.data.connect(self.remarks_from_csv)
        # worker.finished -> self.on_all_jobs_done (built-in QThread signal)

        
        self.worker.finished.connect(self.on_all_jobs_done)
        #summary worker 
        self.worker1 = ProcessingWorkersummary(self.V_name,self.trc_list,self.dbc,self.tyresize, self.DRRn,self.bms_loc,self.bat_name,self.bat_model,self.bat_volt, self.bat_cap,self.g_ratio,self.V_variants)
        self.worker1.job_starting.connect(self.on_job_started_summary)
        self.worker1.job_completed.connect(self.on_job_completed_summary)
        self.worker1.job_failed.connect(self.on_job_failure_summary)
        # self.worker1.data.connect(self.heatmap_data)
        # worker.finished -> self.on_all_jobs_done (built-in QThread signal)
        
        self.worker1.finished.connect(self.on_all_jobs_done_summary)  
        #summary worker 3W
        self.worker_3W = ProcessingWorkersummary_3W(self.V_name,self.trc_list,self.dbc,self.tyresize, self.DRRn,self.bat_name,self.bat_model,self.bat_volt, self.bat_cap,self.g_ratio,self.V_variants)
        self.worker_3W.job_starting.connect(self.on_job_started_summary_3W)
        self.worker_3W.job_completed.connect(self.on_job_completed_summary_3W)
        self.worker_3W.job_failed.connect(self.on_job_failure_summary_3W)
        self.worker_3W.finished.connect(self.on_all_jobs_done_summary_3W)
        self.topbox = QWidget()
        self.topbox.setFixedSize(750,250)
        self.top_layout = QHBoxLayout(self.topbox)
        self.RHS_w = QWidget()
        self.RHS_layout = QVBoxLayout(self.RHS_w)
        # self.RHS_w.setObjectName("RHS")
        # self.RHS_w.setMaximumHeight(150)
        # self.RHS_w.setFixedWidth(250)
        rhs_title = QLabel("DBC selected:")
        rhs_title.setAlignment(Qt.AlignLeft| Qt.AlignTop)
        rhs_title.setStyleSheet("font-size: 11px; color: white;")
        rhs_box = QPushButton(dbc_name)
        rhs_box.setFixedSize(250,30)
        rhs_box.setStyleSheet("background-color: white; color: black; font-family: Consolas;border: 1px solid #999; padding: 2px;")
        self.RHS_layout.addWidget(rhs_title)
        self.RHS_layout.addSpacing(5)
        self.RHS_layout.addWidget(rhs_box,alignment=Qt.AlignLeft | Qt.AlignTop)
        
        
        # Start button to trigger backend
        # self.start_btn = QPushButton("Simulate Backend Job Start")
        # self.start_btn.setStyleSheet("background-color: white; color: black; padding: 10px;")
        # self.start_btn.clicked.connect(self.start_process)
        self.console_output = QTextEdit()
        self.console_output.setFixedSize(400,200)
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: white; color: black; font-family: Consolas;")
        self.top_layout.addSpacing(20)
        self.top_layout.addWidget(self.console_output)
        self.top_layout.addSpacing(70)
        self.top_layout.addWidget(self.RHS_w,alignment= Qt.AlignTop)
        main_layout.addStretch()
        # main_layout.addSpacing(20)
        main_layout.addWidget(self.block_1)
        # main_layout.addSpacing(40)
        main_layout.addWidget(self.block_2)
        # main_layout.addSpacing(40)
        main_layout.addWidget(self.block_3)
        # main_layout.addSpacing(40)
        main_layout.addWidget(self.block_4)
        # main_layout.addSpacing(20)
        main_layout.addStretch()
        self.cancel_btn = QPushButton("Abort Mission")
        self.cancel_btn.clicked.connect(self.abort_mission)
        self.cancel_btn.setFixedSize(150,30)
        outer_layout.addStretch()
        # outer_layout.addSpacing(10)
        outer_layout.addWidget(self.topbox, alignment=Qt.AlignCenter) 
        outer_layout.addSpacing(15)
        outer_layout.addWidget(self.main, alignment=Qt.AlignCenter)
        outer_layout.addSpacing(5)
        outer_layout.addWidget(self.cancel_btn, alignment=Qt.AlignCenter)
        # outer_layout.addWidget(self.start_btn, 0, Qt.AlignmentFlag.AlignCenter)
        outer_layout.addStretch()
        self.setStyleSheet("""
            #main {
                border: 2px solid grey;
                padding: 20px 60px;
                border-radius: 10px;
                background-color: white;
            }
        """)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("Critical Error")
        # self.msg.setDetailedText("The full traceback or technical log can go here.")
        self.msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
        # if self.parsing == "csv file only":
        #     self.start_process()
        # elif self.parsing == "data summary":
        #     self.start_summary_process()
         # 1. Setup the Loggers (No signals here!)
        self.stdout_logger = ThreadSafeLogger()
        self.stderr_logger = ThreadSafeLogger()

        # Save original stream to restore them later! (CRITICAL)
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        sys.stdout = self.stdout_logger
        sys.stderr = self.stderr_logger

        # 2. Setup a Timer to update the UI every 100ms
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.pull_logs_to_ui)
        QTimer.singleShot(500, self.start_everything)
        # self.log_timer.start(100) # 100 milliseconds
        # VITALITY CHECK:
        print("UI LOGGING STARTING...")
        # self.console_output.insertPlainText("IF YOU SEE THIS, THE BOX WORKS\n")
        # self.stdout_logger.write("IF YOU SEE THIS, THE LOGGER WORKS\n")
    # def update_console(self, text,color_name):
    #     # 1. Move cursor to the end
    #     self.console_output.moveCursor(self.console_output.textCursor().End)
        
    #     # 2. Set the color for the NEXT text we insert
    #     self.console_output.setTextColor(QColor(color_name))
        
    #     # 3. Insert the text
    #     self.console_output.insertPlainText(text)
        
    #     # 4. Auto-scroll to the bottom
    #     scrollbar = self.console_output.verticalScrollBar()
    #     scrollbar.setValue(scrollbar.maximum())
    def abort_mission(self):
        if self.reparse_flag == 0:
            if hasattr(self, 'worker') and self.worker.isRunning():
                # 1. Tell the worker to stop
                self.worker.stop()
                self.abortion_flag = 1
                # 2. Inform the user
                print("Stopping csv code... Please wait.")
                # self.stop_btn.setEnabled(False)
                # self.stop_btn.setText("STOPPING...")
                
                # 3. Clean up the thread once it actually quits
                self.worker.finished.connect(self.on_worker_actually_stopped)
            elif hasattr(self, 'worker1') and self.worker1.isRunning():
                # 1. Tell the worker to stop
                self.worker1.stop()
                self.abortion_flag = 1
                # 2. Inform the user
                print("Stopping file summary code... Please wait.")
                # self.stop_btn.setEnabled(False)
                # self.stop_btn.setText("STOPPING...")
                
                # 3. Clean up the thread once it actually quits
                self.worker1.finished.connect(self.on_worker_actually_stopped)
            elif hasattr(self, 'worker_3W') and self.worker_3W.isRunning():
                # 1. Tell the worker to stop
                self.worker_3W.stop()
                self.abortion_flag = 1
                # 2. Inform the user
                print("Stopping file summary code... Please wait.")
                # self.stop_btn.setEnabled(False)
                # self.stop_btn.setText("STOPPING...")
                
                # 3. Clean up the thread once it actually quits
                self.worker_3W.finished.connect(self.on_worker_actually_stopped)
        elif self.reparse_flag == 1:
            print("Reparsing begin!")
            self.progress_bar_sgl.emit(1)
    def on_worker_actually_stopped(self):
        print("Worker successfully halted.")
        self.log_timer.stop()
        self.first_widget.reset()
        self.second_widget.reset()
        self.third_widget.reset()
        self.fourth_widget.reset()
        self.worker.terminate()
        self.worker1.terminate()
        self.worker_3W.terminate()
        # Restore sys.stdout if you're done
        sys.stdout = self.original_stdout
        self.cancel_btn.setText("PARSING HALTED")
        self.progress_bar_sgl.emit(1)
    def start_everything(self):
        self.log_timer.start(100) # Start pulling logs every 100ms
        print("SYSTEM: Logger engaged and Timer started.") # This SHOULD show up now
        
        if self.parsing == "csv file only":
            self.start_process()
        elif self.parsing == "data summary":
            self.start_summary_process()
    def pull_logs_to_ui(self):
        # Handle Standard Output (Black/Green text)
        stdout_text = self.stdout_logger.get_all()
        if stdout_text:
            self.append_to_console(stdout_text, "black")

        # Handle Errors (Red text)
        stderr_text = self.stderr_logger.get_all()
        if stderr_text:
            self.append_to_console(stderr_text, "#FF4444")

    def append_to_console(self, text, color_name):
        self.console_output.moveCursor(QTextCursor.End)
        self.console_output.setTextColor(QColor(color_name))
        self.console_output.insertPlainText(text)
        
        # # Auto-scroll
        # scrollbar = self.console_output.verticalScrollBar()
        # scrollbar.setValue(scrollbar.maximum())
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

    def start_process(self):
        """Starts the background thread."""
        # self.start_btn.setEnabled(False)
        # self.start_btn.setText("Parsing Started...")
        
        # Reset all icons to grey before starting
        # for icon in self.checkpoints:
        #     icon.reset()
        self.first_widget.reset()
        self.second_widget.reset()
        self.third_widget.reset()
        self.fourth_widget.reset()
        # Start background loop
        self.worker.start()

    def on_job_started(self, job_index_id):
        """Slot: called when worker signals job start."""
        # Find the correct StepIcon object in our list and command it
        # Safety check: ensure id is within valid range of list
        # if 0 <= job_index_id < len(self.checkpoints):
        #     icon_object = self.checkpoints[job_index_id]
        #     icon_object.set_running() # Command icon to spin
        self.job_index_pcan_generator_start = job_index_id
        if self.parsing == "csv file only":
            if job_index_id == 0:
                self.first_widget.set_running()
                self.first_label.setText("Fetching .trc files")
            elif job_index_id == 1:
                self.second_widget.set_running()
                self.second_label.setText("Creating .csv files")
            elif job_index_id == 2:
                self.third_widget.set_running()
                self.third_label.setText("Merging files")
            elif job_index_id == 3:
                self.fourth_widget.set_running()
                self.fourth_label.setText("Generating Pcan.csv")
            # elif job_index_id == 3 and self.heatmap == 1:
            #     self.fourth_widget.set_running()
        elif self.parsing == "data summary":
            if job_index_id == 0:
                self.first_widget.set_running()
                self.first_label.setText("Creating csv file..")
            elif job_index_id == 1:
                self.second_widget.set_running()
                self.second_label.setText("Combining csv files..")
    def on_job_completed(self, job_index_id):
        """Slot: called when worker signals job success."""
        # if 0 <= job_index_id < len(self.checkpoints):
        #     icon_object = self.checkpoints[job_index_id]
        #     icon_object.set_done() # Command icon to stop, go green
        self.job_index_pcan_generator_complete = job_index_id
        if self.parsing == "csv file only":
            if job_index_id == 0:
                self.first_widget.set_done()
                self.first_label.setText("Fetched .trc files Successfully")
            elif job_index_id == 1:
                self.second_widget.set_done()
                self.second_label.setText("Created .csv files of trc")
            elif job_index_id == 2:
                self.third_widget.set_done()
                self.third_label.setText("Merged all the csv files")
            elif job_index_id == 3:
                if self.heatmap == 0:
                    self.fourth_widget.set_done()
                    self.fourth_label.setText("Created combined csv!!")
                    QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
                    print("Parsing done and created csv.")
                    sys.stdout.flush()
                    sys.stderr.flush()
                    self.restore_terminal()
                if self.heatmap == 1:
                    self.heatmap_generation()
                    print("start heatmap worker")
        elif self.parsing == "data summary":
            if job_index_id == 0:
                self.first_widget.set_done()
                self.first_label.setText("Created csv files")
            elif job_index_id == 1:
                self.second_widget.set_done()
                self.second_label.setText("Generated combined csv")
    def on_all_jobs_done(self):
        """Slot: called when whole thread ends."""
        if self.parsing == "data summary":
            self.flag_start_summary = 1
        elif self.heatmap == 0 and self.parsing == "csv file only":
            # QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
            self.cancel_btn.setText("Re-parse")
            self.reparse_flag = 1
            print("Parsing done")
        if self.parsing == "data summary" and self.abortion_flag == 0:
            if self.flag_start_summary == 1 and self.V_type == "4W":
                self.worker1.start()
            elif self.flag_start_summary == 1 and self.V_type == "3W":
                self.worker_3W.start()
        elif self.abortion_flag == 1:
            QMessageBox.information(None, "Stop!", "Mission Abort!!")
        # self.start_btn.setEnabled(True)
        # self.start_btn.setText("Process Finished. Click to restart.")
        
        
    def on_job_failure(self,job_index_id,reason):
        if self.parsing == "csv file only":
            if job_index_id == 0:
                self.first_widget.set_fail()
                self.msg.setText("File selection error.")
            elif job_index_id == 1:
                self.second_widget.set_fail()
                self.msg.setText("File conversion error.")
            elif job_index_id == 2:
                self.third_widget.set_fail()
                self.msg.setText("File combining error.")
            elif job_index_id == 3:
                self.fourth_widget.set_fail()
                self.msg.setText("Pcan.csv generation error.")
        elif self.parsing == "data summary":
            if job_index_id == 0:
                self.first_widget.set_fail()
                self.msg.setText("File creation error.")
            elif job_index_id == 1:
                self.second_widget.set_fail()
                self.msg.setText("Pcan.csv generation error.")
        msg_button = self.msg.exec()
        self.msg.setInformativeText(reason)
        # if msg_button == QMessageBox.Retry:
        #     print("User clicked Retry")
    def remarks_from_csv(self,list_n):
        if len(list_n) == 0:
            self.remarks = "No errors"
        else:    
            self.remarks = ", ".join(list_n)

    def start_summary_process(self):
        """Starts the background thread."""
        # self.start_btn.setEnabled(False)
        # self.start_btn.setText("Parsing Started...")
        
        # Reset all icons to grey before starting
        # for icon in self.checkpoints:
        #     icon.reset()
        self.first_widget.reset()
        self.second_widget.reset()
        self.third_widget.reset()
        self.fourth_widget.reset()
        # Start background loop
        self.worker.start()

        
    def on_job_started_summary(self,job_index):
        if job_index == 0:
            self.third_widget.set_running()
            self.third_label.setText("Processing bms.csv")
        elif job_index == 1:
            self.third_label.setText("Processing pcan.csv")
        elif job_index == 2:
            self.fourth_widget.set_running()
            self.fourth_label.setText("Summarizing them")
    def on_job_completed_summary(self,job_index):
        if job_index == 0:
            self.third_label.setText("Processed bms")
        elif job_index == 1:
            self.third_widget.set_done()
            self.third_label.setText("Processed both csv")
        elif job_index == 2:
            if self.heatmap == 0 and self.table == 0 and self.api == 0:
                self.fourth_widget.set_done()
                self.fourth_label.setText("Created data summary!!")
            elif self.heatmap == 1:
                self.heatmap_generation()
                print("start heatmap worker")
                print("process heatmap")
            elif self.heatmap == 0 and self.table == 1:
                self.table_generation()
                print("starting table worker")
            elif self.heatmap == 0 and self.table == 0 and self.api == 1:
                self.upload_on_gsheet()
                print("starting upload to google sheet!!")
    def on_all_jobs_done_summary(self):
        if self.heatmap == 0 and self.abortion_flag == 0 and self.table == 0 and self.api == 0:
            QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
            print("Parsing done and created file summary")
            sys.stdout.flush()
            sys.stderr.flush()
            self.restore_terminal()
            self.cancel_btn.setText("Re-parse")
            self.reparse_flag = 1
        elif self.abortion_flag == 1:
            QMessageBox.information(None, "Stop!", "Mission Abort!!")
    def on_job_failure_summary(self,job_index_id,reason):
        if job_index_id in [1,0]:
            self.third_widget.set_fail()
            if job_index_id == 0:
                self.msg.setText("BMS file corrupt")
            else:
                self.msg.setText("PCAN file corrupt")
            self.third_label.setText("Failed!")
        elif job_index_id ==2:
            self.fourth_widget.set_fail()
            self.msg.setText("Pcan.csv generation error.")
            self.fourth_label.setText("Failed!")
        msg_button = self.msg.exec()
        self.msg.setInformativeText(reason)
        sys.stdout.flush()
        sys.stderr.flush()
        self.restore_terminal()
        self.cancel_btn.setText("Re-parse")
        self.reparse_flag = 1
    def on_job_started_summary_3W(self,job_index):
        if job_index == 0:
            self.third_widget.set_running()
            self.third_label.setText("Processing bms data")
        elif job_index == 1:
            self.third_label.setText("Processing pcan data")
        elif job_index == 2:
            self.fourth_widget.set_running()
            self.fourth_label.setText("Summarizing them")
    def on_job_completed_summary_3W(self,job_index):
        if job_index == 1:
            self.third_widget.set_done()
            self.third_label.setText("Processed combined csv")
        elif job_index == 2:
            if self.heatmap == 0 and self.table == 0 and self.api == 0:
                self.fourth_widget.set_done()
                self.fourth_label.setText("Created data summary!!")
            elif self.heatmap == 1:
                self.heatmap_generation()
                print("start heatmap worker")
                print("process heatmap")
            elif self.heatmap == 0 and self.table == 1:
                self.table_generation()
                print("starting table worker")
            elif self.heatmap == 0 and self.table == 0 and self.api == 1:
                self.upload_on_gsheet()
                print("starting upload to google sheet!!")
    def on_all_jobs_done_summary_3W(self):
        if self.heatmap == 0 and self.abortion_flag == 0 and self.table == 0 and self.api == 0:
            QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
            print("Parsing done and created file summary")
            sys.stdout.flush()
            sys.stderr.flush()
            self.restore_terminal()
            self.cancel_btn.setText("Re-parse")
            self.reparse_flag = 1
        elif self.abortion_flag == 1:
            QMessageBox.information(None, "Stop!", "Mission Abort!!")
    def on_job_failure_summary_3W(self,job_index_id,reason):
        if job_index_id in [1,0]:
            self.third_widget.set_fail()
            if job_index_id == 0:
                self.msg.setText("BMS file corrupt")
            else:
                self.msg.setText("PCAN file corrupt")
            self.third_label.setText("Failed!")
        
        elif job_index_id ==2:
            self.fourth_widget.set_fail()
            self.msg.setText("Pcan.csv generation error.")
            self.fourth_label.setText("Failed!")
            
        msg_button = self.msg.exec()
        self.msg.setInformativeText(reason)
        sys.stdout.flush()
        sys.stderr.flush()
        self.restore_terminal()
        self.cancel_btn.setText("Re-parse")
        self.reparse_flag = 1
    # def heatmap_data(self,torque_max, rpm_max, mode):
    #     print("Torque max: ",torque_max,"\n")
    #     print("RPM max: ",rpm_max,"\n")
    #     print("Mode: ",mode,"\n")
    def torque_and_rpm(self,vehicle_var,vehicle_name):
        self.trc_l = os.path.abspath(os.path.dirname(self.trc_list[-1]))
        pcan_path = os.path.join(self.trc_l, "pcan.csv")
        if not os.path.exists(pcan_path):
            print("pcan.csv doesnt exist in the current folder")
            self.job_failed.emit(1,"Unable to find pcan.csv")
            return 
        df_pcan = pd.read_csv(pcan_path)
        rows = df_pcan
        rhino = []
        for i, row in rows.iterrows():
            gearMode         = row["controller_vehicle_status"]
            torque           = row["TORQUE"]
            if self.V_variants == "1750":
                if gearMode not in ["R", "N", "Z"] and not (gearMode == "H" and torque not in range(-130,220)):
                    if gearMode == "H":
                            rhino.append(gearMode)
            else:
                if gearMode not in ["R", "N", "Z"] and not (gearMode == "H" and torque not in range(-130,150)):
                    if gearMode == "H":
                            rhino.append(gearMode)
        Eco = rows["controller_vehicle_status"].isin(["E"]).sum()
        Thunder = rows["controller_vehicle_status"].isin(["S"]).sum()
        Rhino = len(rhino)
        Total = Eco + Thunder + Rhino
    #we are comparing the percentage removing neutral and reverse
        eco_percentage = (Eco / Total * 100) if Total else 0
        rhino_percentage = (Rhino / Total * 100) if Total else 0
        Thunder_percentage = (Thunder / Total * 100) if Total else 0
        mode = max(
            ("ECO", eco_percentage),
            ("RHINO", rhino_percentage),
            ("THUNDER", Thunder_percentage),
            key=lambda x: x[1]
        )[0]
        MODE = mode
        dict_vehicle = {
            "V1": (420,("ECO",65,5032),("THUNDER",130,6709)), 
            "V2":(120,("ECO",100,5087),("THUNDER",125,7122)), 
            "V3":(420,("ECO",100,4578),("THUNDER",145,7122),("RHINO",145,3561)),
            "1250":(420,("ECO",100,5318),("THUNDER",125,7446),("RHINO",145,3723)), 
            "1750":(270,("ECO",120,6198),("THUNDER",180,8677),("RHINO",210,4339)), 
            # "LR200":(420,("ECO",65,5032),("THUNDER",130,6709),("RHINO",130,6709))
        }
        torque_max = 0
        rpm_max = 0
        vehicle_ARMS = 0 
        if vehicle_var == "LR200":
            vehicle_ARMS = 135
            if vehicle_name in ["LR01","LR02"]:
                if MODE == "ECO":
                    torque_max = 100
                    rpm_max = 5103
                elif MODE == "THUNDER":
                    torque_max = 125
                    rpm_max = 7144
                elif MODE == "RHINO":
                    torque_max = 140
                    rpm_max = 3572
            else:
                if MODE == "ECO":
                    torque_max = 100
                    rpm_max = 6198
                elif MODE == "THUNDER":
                    torque_max = 125
                    rpm_max = 8677
                elif MODE == "RHINO":
                    torque_max = 140
                    rpm_max = 4339
        else:
            for vehicle, value in dict_vehicle.items():
                if vehicle == vehicle_var:
                    vehicle_ARMS = value[0]
                    for i in range(1,len(value)):
                        if MODE == value[i][0]:
                            torque_max = value[i][1]
                            rpm_max = value[i][2]
            
        return torque_max,rpm_max
    def arms_and_rpm(self,V_variants,V_name):
        rpm_max = 6500 #default
        ARMS_max = 400
        if V_variants == "XR_NEO":
            ARMS_max = 250
            rpm_max = 6000
        elif V_variants == "SR_HR":
            ARMS_max = 300
            rpm_max = 7000
        elif V_variants == "XR_HR":
            ARMS_max = 325
        return ARMS_max,rpm_max
        
    def heatmap_generation(self):
        option1 = None
        if self.V_type == "4W":
            result = self.torque_and_rpm(self.V_variants,self.V_name)
            T_max,RPM_max = result
            option1 = T_max
        elif self.V_type == "3W":
            result_3W = self.arms_and_rpm(self.V_variants,self.V_name)
            ARMS_max, RPM_max = result_3W
            option1 = ARMS_max
        from backend.heatmap import ProcessingWorkerheatmap
        self.worker_h = ProcessingWorkerheatmap(self.trc_list,option1,RPM_max,self.V_type)
        self.worker_h.job_starting.connect(self.on_job_started_heatmap)
        self.worker_h.job_completed.connect(self.on_job_completed_heatmap)
        self.worker_h.job_failed.connect(self.on_job_failure_heatmap)
        self.worker_h.finished.connect(self.on_all_jobs_done_heatmap)
        self.worker_h.start()
    def on_job_started_heatmap(self,job_index):
        if job_index == 0:
            self.fourth_label.setText("Generating heatmap")
    def on_job_completed_heatmap(self,job_index): 
        if job_index == 0 and self.table == 0 and self.api == 0:
            self.fourth_label.setText("Generated Heatmap!!")
            self.fourth_widget.set_done()
        elif job_index == 0 and self.table == 1:
            self.fourth_label.setText("Generated Heatmap!!")
            self.table_generation()
        elif job_index == 0 and self.table == 0 and self.api == 1:
            self.fourth_label.setText("Generated Heatmap!!")
            self.upload_on_gsheet()
    def on_job_failure_heatmap(self,job_index,reason):
        if job_index == 0:
            self.fourth_widget.set_fail()
            self.msg.setText("Heatmap generation error")
        msg_button = self.msg.exec()
        self.fourth_label.setText("Failed!")
        self.msg.setInformativeText(reason)
        sys.stdout.flush()
        sys.stderr.flush()
        self.restore_terminal()
        self.cancel_btn.setText("Re-parse")
        self.reparse_flag = 1
    def on_all_jobs_done_heatmap(self):
        if self.table == 0:
            QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
            print("Parsing done and created heatmap")
            sys.stdout.flush()
            sys.stderr.flush()
            self.restore_terminal()
            self.cancel_btn.setText("Re-parse")
            self.reparse_flag = 1
        
    def restore_terminal(self):
        """Give control back to the original system terminal."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        self.log_timer.stop()
    def table_generation(self):
        from backend.table import ProcessingWorkertable
        self.worker_t = ProcessingWorkertable(self.trc_list,self.V_variants,self.V_name,self.bat_name,self.tyresize,self.V_type,self.g_ratio)
        self.worker_t.job_starting.connect(self.on_job_started_table)
        self.worker_t.job_completed.connect(self.on_job_completed_table)
        self.worker_t.job_failed.connect(self.on_job_failure_table)
        self.worker_t.finished.connect(self.on_all_jobs_done_table)
        self.worker_t.start()
    def on_job_started_table(self,job_index):
        if job_index == 0:
            self.fourth_label.setText("Generating table")
    def on_job_completed_table(self,job_index):
        if job_index == 0 and self.api == 0:
            self.fourth_label.setText("Generated table!!")
            self.fourth_widget.set_done()
            QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
            print("Parsing done and created table")
        elif job_index == 0 and self.api ==1:
            self.fourth_label.setText("Generated table!!")
            self.upload_on_gsheet()
    def on_job_failure_table(self,job_index,reason):
        if job_index == 0:
            self.fourth_widget.set_fail()
            self.msg.setText("Table generation error")
        msg_button = self.msg.exec()
        self.msg.setInformativeText(reason)
        self.fourth_label.setText("Failed!")
        sys.stdout.flush()
        sys.stderr.flush()
        self.restore_terminal()
        self.cancel_btn.setText("Re-parse")
        self.reparse_flag = 1
    def on_all_jobs_done_table(self):
        if self.api == 0:
            sys.stdout.flush()
            sys.stderr.flush()
            self.restore_terminal()
            self.cancel_btn.setText("Re-parse")
            self.reparse_flag = 1
    def upload_on_gsheet(self):
        from backend.google_upload import ProcessingWorkerupload
        self.worker_google = ProcessingWorkerupload(self.trc_list,self.V_variants,self.V_name,self.V_type,self.email,self.remarks)
        self.worker_google.job_starting.connect(self.on_job_started_upload)
        self.worker_google.job_completed.connect(self.on_job_completed_upload)
        self.worker_google.job_failed.connect(self.on_job_failure_upload)
        self.worker_google.finished.connect(self.on_all_jobs_done_upload)
        self.worker_google.start()
    def on_job_started_upload(self,job_index):
        if job_index == 0:
            self.fourth_label.setText("Uploading to sheet!")
    def on_job_completed_upload(self, job_index):
        if job_index == 0:
            self.fourth_label.setText("Uploaded Successfully!!")
            self.fourth_widget.set_done()
            QMessageBox.information(None, "DONE!", "Parsing Complete\n Click home button to re-parse.")
            print("Parsing done and uploaded summary")
    def on_job_failure_upload(self, job_index,reason):
        if job_index == 0:
            self.fourth_widget.set_fail()
            self.msg.setText("Upload error")
        msg_button = self.msg.exec()
        self.msg.setInformativeText(reason)
        sys.stdout.flush()
        sys.stderr.flush()
        self.restore_terminal()
        self.cancel_btn.setText("Re-parse")
        self.reparse_flag = 1  
    def on_all_jobs_done_upload(self):
        sys.stdout.flush()
        sys.stderr.flush()
        self.restore_terminal()
        self.cancel_btn.setText("Re-parse")
        self.reparse_flag = 1