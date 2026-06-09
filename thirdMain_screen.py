import sys
import os
import glob
from Tyre_size_box import TyreWindow
from DBC_pick_box import VehicleConfigWindow
#from vehicle_type import vehicletype
from Vehicle_name_box import VehicleInputBox
from battery_details import BatteryWindow 
from gear_ratioBox import GearRatioWindow
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QHBoxLayout, QVBoxLayout, QGridLayout, 
                               QLabel, QPushButton, QFrame,QComboBox, QFileDialog,QCheckBox,QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItemModel

class EulerParserMain(QMainWindow):
    Parsing_screen = Signal(str,object,str,str,str,float,str,str,float,float,float,float,int,int,int,str)
    def __init__(self,vehicle_type,user_email,connect_btn_flag, button,statusBar = None):
        super().__init__()
        self.status = statusBar
        # self.status.setStyleSheet("padding: 4px; color: white")
        # self.setWindowTitle("PARSER - EULER MOTORS")
        self.resize(900, 200)
        self.setWindowTitle("Parsing Type")
        # Ensure minimum size is set
        # self.addSpacing(10)
        # self.setMinimumSize(700, 100)
        
        self.connect_btn_t = button
        self.mail = user_email
        self.connect_btn = connect_btn_flag
        # KEY STEP 1: Make this widget's background transparent to allow 
        # the external dark textured background to show through.
        self.setStyleSheet("""
                 #BmsFrame { 
                     background-color: #E1D5E7; 
                     border: 1px solid #9673A6; 
                     border-radius: 6px; 
                 }
                 
                
                 QPushButton { 
                     background-color: white; 
                     border: 1px solid #adb5bd; 
                     border-radius: 4px; 
                     padding: 6px 12px;
                     min-width: 120px;
                 }
                 QPushButton:hover { background-color: #e2e6ea; border-color: #007bff; }
                 QLabel { color: white; font-family: 'Segoe UI', Arial; font-size: 15px; font-weight: bold }
                 QCheckBox {color: white;font-size: 13px}
                 #BMSText {  color: black; font-family: 'Segoe UI', Arial; font-size: 15px; font-weight: bold
                 }
                 QMessageBox {color: black}
             """)
        #QMainWindow { background-color: #f8f9fa; }
        self.vehicle_name = None
        self.trc_files = []
        self.dbc_new_location = None
        self.parsing_type = None
        self.Tyre_size_name = None
        self.DRR = None
        self.bms_file_location = None
        self.Battery_name = None
        self.Battery_Model = 0.0
        self.Battery_Voltage = 0.0
        self.Battery_capacity = 0.0
        self.gear_ratio = 0.0
        self.flag_general = 0
        self.flag_heatmap = 0
        self.flag_google_upload = 0
        self.flag_table = 0
        self.vehicle_type_selected = vehicle_type
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.v1 = ["7002","7003","7005","7006","7009"]
        self.v2 = ["7070","7172","7004","7019","7042"]
        self.v3 = ["7001","7007","7008","7010"]
        self.S_1250 = ["S1","S2","S3","S4"]
        self.LR200 = ["LR00","LR01","LR02","LR03"]
        self.S_1750 = ["X00","X01","X02","X03","X04"]
        # Root layout is Horizontal to hold Left and Right panels
        vehicle_dict = {
            "1250": self.S_1250,
            "1750": self.S_1750,
            "LR200": self.LR200,
            "V1": self.v1,
            "V2": self.v2,
            "V3": self.v3
        }
        self.function_selected = None
        for name, func in vehicle_dict.items():
            if name == self.vehicle_type_selected:
                self.function_selected = func
        self.root_layout = QHBoxLayout(central_widget)
        self.root_layout.setContentsMargins(30, 30, 30, 30)
        self.root_layout.setSpacing(20)

        # 1. Setup Left Panel (Selection Rows)
        self.left_panel = QVBoxLayout()
        self.setup_left_ui()
        
        # 2. Setup Right Panel (BMS Box and Inputs)
        self.right_panel = QVBoxLayout()
        self.setup_right_ui()
        
        # Add panels to root
        self.root_layout.addLayout(self.left_panel, 1)  # Stretch factor 2
        self.root_layout.addLayout(self.right_panel, 1) # Stretch factor 1
        
    def setup_left_ui(self):
        """Creates the vertical selection rows on the left."""
        grid = QGridLayout()
        # msg = QMessageBox(None)
        grid.setVerticalSpacing(40)
        # grid.setFixedWidth(300)
        # grid.setHorizontalSpacing(1)
        # grid.setColumnMinimumWidth(0,5)
        # Row 0: Vehicle Name
        grid.addWidget(QLabel("Select Vehicle name:"), 0, 0)
        # btn_veh = QPushButton("Select vehicle")
        self.btn_veh = QComboBox()
        self.btn_veh.setEditable(False)
        self.btn_veh.addItem("--Select name--")
        self.btn_veh.addItems(self.function_selected)
        # self.btn_veh.setEditable(True)
        # self.btn_veh.addItem("Other")
        # self.btn_veh.currentIndexChanged.connect(self.enter_vehicle_name)
        self.btn_veh.setEditable(True)
        line_edit_v = self.btn_veh.lineEdit()
        self.btn_veh.addItem("Other")
        self.btn_veh.currentTextChanged.connect(self.enter_vehicle_name)
        self.btn_veh.setMinimumHeight(32)
        line_edit_v.setReadOnly(True)
        line_edit_v.setAlignment(Qt.AlignCenter)
        # Optional: disable focus or cursor to hide edit-like behavior
        line_edit_v.setFocusPolicy(Qt.NoFocus)
        for i in range(self.btn_veh.count()):
            self.btn_veh.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
        # btn_veh.clicked.connect(self.open_vehicle_file)
        grid.addWidget(self.btn_veh, 0, 1)

        # Row 1: TRC File
        grid.addWidget(QLabel("Select trc files:"), 1, 0)
        self.btn_trc = QPushButton("select trc...")
        self.btn_trc.clicked.connect(self.open_trc_file)
        
        grid.addWidget(self.btn_trc, 1, 1)


        # Row 2: DBC File
        self.dbc_text = None
        grid.addWidget(QLabel("Select DBC:"), 2, 0)
        self.btn_dbc = QComboBox()
        self.btn_dbc.setEditable(False)
        self.dbc_names = ["Vehicle Testing Marvel","Vehicle Testing NBMS","BMS-Marvel only","BMS-NBMS only","MCU","Xavier","Stark","V7","V8","V9","Charging Log DBC","Select Other"]
        self.btn_dbc.addItem("--Select DBC--")
        self.btn_dbc.addItems(self.dbc_names)
        self.btn_dbc.setEditable(True)
        self.btn_dbc.currentTextChanged.connect(self.open_dbc_file)
        line_dbc = self.btn_dbc.lineEdit()
        line_dbc.setReadOnly(True)
        line_dbc.setAlignment(Qt.AlignCenter)
        # Optional: disable focus or cursor to hide edit-like behavior
        line_dbc.setFocusPolicy(Qt.NoFocus)
        for i in range(self.btn_dbc.count()):
            self.btn_dbc.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
        self.btn_dbc.setMinimumHeight(32)
        grid.addWidget(self.btn_dbc, 2, 1)
        self.toggle_item(1,True)
        self.toggle_item(0,True)
        
        # Row 3: Parsing Type
        grid.addWidget(QLabel("Select parsing type:"), 3, 0)
        self.parsing_dropdown = QComboBox()
        self.parsing_dropdown.setEditable(False)
        self.parsing_dropdown.addItems(["--Select type--","csv file only"])
        # self.parsing_dropdown.lineEdit().setAlignment(Qt.AlignCenter)
        self.parsing_dropdown.currentTextChanged.connect(self.parsing_option)
        self.parsing_dropdown.setEditable(True)
        line_edit = self.parsing_dropdown.lineEdit()
        line_edit.setReadOnly(True)
        line_edit.setAlignment(Qt.AlignCenter)
        # Optional: disable focus or cursor to hide edit-like behavior
        line_edit.setFocusPolicy(Qt.NoFocus)
        for i in range(self.parsing_dropdown.count()):
            self.parsing_dropdown.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
        self.parsing_dropdown.setMinimumHeight(32)
        grid.addWidget(self.parsing_dropdown, 3, 1)
        
        # Row 4: Tyre Size
        grid.addWidget(QLabel("Tyre Size:"), 4, 0)
        # self.btn_tyre = QPushButton("Select tyre size")
        self.btn_tyre = QComboBox()
        self.btn_tyre.setEditable(False)
        self.btn_tyre.addItems(["--Select tyre--","145 R12 LT 8PR","155 R13 LT 8PR","165 R14","185 R14","185 R14-(334)","others"])
        self.btn_tyre.currentTextChanged.connect(self.Tyre)
        self.btn_tyre.setEditable(True)
        self.alignment(self.btn_tyre)
        # btn_tyre.clicked.connect(self.open_tyre_file)
        grid.addWidget(self.btn_tyre, 4, 1)
        # self.left_panel.addStretch()
        self.left_panel.addSpacing(40)
        self.left_panel.addLayout(grid)
        self.left_panel.addStretch()

    def setup_right_ui(self):
        """Creates the BMS frame and specific battery/gear inputs."""
        
        # BMS Auto-Pick Frame
        bms_frame = QFrame()
        bms_frame.setObjectName("BmsFrame")
        bms_frame.setFixedWidth(400)
        bms_layout = QVBoxLayout(bms_frame)

        # BMS Labels
        top_hint = QLabel("4w specific")
        top_hint.setStyleSheet("font-size: 10px; color: #666;")
        
        mid_row = QHBoxLayout()
        self.autopick = QLabel("BMS auto-pick:")
        self.autopick.setObjectName("BMSText")
        bottom_row = QHBoxLayout()
        mid_row.addWidget(self.autopick)
        self.bms_display = QPushButton("--Select bms--")
        self.bms_display.clicked.connect(self.bms_selection)
        self.bms_display.setStyleSheet("background: white; border: 1px solid #999; padding: 2px;")
        mid_row.addWidget(self.bms_display)
        self.bottom_right = QPushButton("reset")
        self.bottom_right.clicked.connect(self.resetbms)
        self.bottom_right.setFixedSize(20,30)
        self.bottom_right.setStyleSheet("background: white; border: 1px solid #999; padding: 2px;")
        self.bottom_hint = QLabel("no bms file found/selected!!")
        self.bottom_hint.setAlignment(Qt.AlignRight)
        self.bottom_hint.setStyleSheet("font-size: 9px; color: #0056b3;")
        bottom_row.addWidget(self.bottom_right)
        bottom_row.addSpacing(40)
        bottom_row.addWidget(self.bottom_hint)
        bms_layout.addWidget(top_hint)
        bms_layout.addLayout(mid_row)
        bms_layout.addLayout(bottom_row)
        # self.right_panel.addStretch()
        self.right_panel.addSpacing(40)
        self.right_panel.addWidget(bms_frame)
        # self.right_panel.addSpacing(30)
        self.right_panel.addSpacing(10)
        # Battery and Gear Grid
        lower_grid = QGridLayout()
        lower_grid.setHorizontalSpacing(0)
        # lower_grid.setVerticalSpacing(25)
        self.heatmap_check = QCheckBox("Heatmap")
        self.heatmap_check.setCheckState(Qt.CheckState.Unchecked)
        self.table_check = QCheckBox("Summary Table")
        self.table_check.setCheckState(Qt.CheckState.Unchecked)
        self.upload_check = QCheckBox("Upload to google sheet")
        self.upload_check.setCheckState(Qt.CheckState.Unchecked)
        self.heatmap_check.checkStateChanged.connect(self.heatmapcase)
        self.table_check.checkStateChanged.connect(self.tablecase)
        self.upload_check.checkStateChanged.connect(self.uploadcase)
        lower_grid.addWidget(self.heatmap_check,0,0)
        lower_grid.addWidget(self.upload_check,0,1)
        lower_grid.setRowMinimumHeight(1, 20)
        lower_grid.addWidget(self.table_check,1,0)
        lower_grid.setRowMinimumHeight(2, 30)
        lower_grid.setRowMinimumHeight(3, 70)
        lower_grid.addWidget(QLabel("Battery Model:"), 2, 0)
        self.btn_bat = QComboBox()
        self.btn_bat.setEditable(False)
        self.btn_bat.addItems(["--Select battery--","G2F - 15.3 KWH 76.8V","G2A-19.2 KWH 96V","G2B-30.72 KWH 307.2","ATH-4 16 KWH 320V","ATH-5 19.2 KWH 384V","others"])
        self.btn_bat.currentTextChanged.connect(self.battery_details)
        self.btn_bat.setEditable(True)
        self.alignment(self.btn_bat)
        lower_grid.addWidget(self.btn_bat, 2, 1)

        lower_grid.addWidget(QLabel("Gear reduction:"), 3, 0)
        self.btn_gear = QComboBox()
        self.btn_gear.addItems(["--Select gear ratio--","12.35","10.45","15.1","others"])
        self.btn_gear.setEditable(False)
        self.btn_gear.currentTextChanged.connect(self.gear_ratio_func)
        self.btn_gear.setEditable(True)
        self.alignment(self.btn_gear)
        lower_grid.addWidget(self.btn_gear, 3, 1)
        # lower_grid.setContentsMargins(0, 0, 0, 0)
        self.next_btn = QPushButton("Start Parsing")
        self.next_btn.setFixedSize(50,30)
        self.next_btn.clicked.connect(self.startparsing)
        # self.right_panel.addStretch()
        self.right_panel.addLayout(lower_grid)
        self.right_panel.addSpacing(20)
        self.right_panel.addWidget(self.next_btn)
        self.right_panel.setAlignment(self.next_btn, Qt.AlignRight)
        self.right_panel.addStretch()

    # --- ACTION METHODS ---
    def startparsing(self):
        
        parsing_checks = {
        self.btn_veh: (["--Select name--", "Other"], "Vehicle Name"),
        self.btn_dbc: (["--Select DBC--", "Select Other"], "Vehicle DBC"),
        self.parsing_dropdown: (["--Select type--", ""], "Parsing Type"),
        self.btn_tyre: (["--Select tyre--", "others"], "Tyre Size"),
        self.btn_bat: (["--Select battery--", "others"], "Battery Details"),
        self.btn_gear: (["--Select gear ratio--", "others"], "Gear Ratio")
        }

        # 2. Validate Dropdowns
        for combo, (invalid_vals, label) in parsing_checks.items():
            if combo.currentText() in invalid_vals:
                QMessageBox.critical(None, "Selection Required", f"Please select a {label}.")
                combo.setFocus() # Highlights the problematic box
                return # STOP the parsing here!

        # 3. Validate Buttons (TRC File)
        # Check if the button text is still the default "select trc..."
        if self.btn_trc.text() == "select trc...":
            QMessageBox.critical(None, "File Missing", "Please select the TRC files before parsing.")
            return
        if self.parsing_dropdown.currentText() == "data summary":
            if not self.bms_file_location:
                QMessageBox.critical(None, "File Missing", "Please select the bms file before parsing.")
                return
        if self.heatmap_check.isChecked():
            self.flag_heatmap = 1
        else:
            self.flag_heatmap = 0
        if self.table_check.isChecked():
            self.flag_table = 1
        else:
            self.flag_table = 0
        if self.upload_check.isChecked():
            self.flag_google_upload = 1
        else:
            self.flag_google_upload = 0
        
        print("Vehicle name: ",self.vehicle_name ,"\n",
        "Vehicle trc_location: ",self.trc_files,"\n",
        "Vehicle dbc_location: ",self.dbc_new_location,"\n",
        "Vehicle parsing type: ",self.parsing_type,"\n",
        "Vehicle tyre size: ",self.Tyre_size_name,"\n",
        "Vehicle DRR: ",self.DRR,"\n",
        "Vehicle bms location: ",self.bms_file_location,"\n",
        "Vehicle battery name: ",self.Battery_name,"\n",
        "Vehicle battery model: ",self.Battery_Model,"\n",
        "Vehicle battery voltage: ",self.Battery_Voltage,"\n",
        "Vehicle capacity: ",self.Battery_capacity,"\n",
        "Vehicle gear ratio: ",self.gear_ratio )    
        self.Parsing_screen.emit(self.vehicle_name,self.trc_files,self.dbc_new_location,self.parsing_type,self.Tyre_size_name,self.DRR,self.bms_file_location,self.Battery_name,self.Battery_Model,self.Battery_Voltage,self.Battery_capacity,self.gear_ratio,self.flag_heatmap,self.flag_table,self.flag_google_upload,self.vehicle_type_selected)
    def open_trc_file(self):
        print("Calling TRC file picker...")
        try:
            file_path_trc, _ = QFileDialog.getOpenFileNames(
                self, "Select TRC File", "", "TRC Files (*.trc);;All Files (*)"
            )
            self.trc_files = file_path_trc
            if file_path_trc:
                self.btn_trc.setText("TRC selected")
                self.autoreadbms()
            print("TRC window opened successfully.")
        except Exception as e:
            print(f"Error: Could not open TRC file window. {e}")

    def open_dbc_file(self,text):
        print("Calling DBC file picker...")
        self.dbc_text = text
        try:
            if self.dbc_text == "Select Other":
                self.DBC_window = VehicleConfigWindow()
                self.DBC_window.show()
                self.DBC_window.dbc_file_location.connect(self.dbc_location)
                text_remove = self.parsing_dropdown.findText("data summary")
                if text_remove>=0:
                    self.parsing_dropdown.removeItem(text_remove)
                    self.flag_general = 0
                    self.heatmap_check.setCheckState(Qt.CheckState.Unchecked)
            elif self.dbc_text == "--Select DBC--":
                self.status.showMessage("select DBC file",3000)
                text_remove = self.parsing_dropdown.findText("data summary")
                if text_remove>=0:
                    self.parsing_dropdown.removeItem(text_remove)
                    self.flag_general = 0
                    self.heatmap_check.setCheckState(Qt.CheckState.Unchecked)
            else:
                path = self.get_resource("")
                dict_dbc = {
                    self.dbc_names[0]: os.path.join(path,"DBC","4W","daily discharging parsing","MARVEL","DAILY_PARSER_MARVEL.dbc"),
                    self.dbc_names[1]: os.path.join(path,"DBC","4W","daily discharging parsing","NBMS","DAILY_PARSER_NBMS.dbc"),
                    self.dbc_names[2]: os.path.join(path,"DBC","4W","BMS","MARVEL4.dbc"),
                    self.dbc_names[3]: os.path.join(path,"DBC","4W","BMS","NBMS_ATHENA_4.dbc"),
                    self.dbc_names[4]: os.path.join(path,"DBC","4W","MCU","Euler_1.dbc"),
                    self.dbc_names[5]: os.path.join(path,"DBC","4W","xavier","XavierDBC.dbc"),
                    self.dbc_names[6]: os.path.join(path,"DBC","4W","stark","stark.dbc"),
                    self.dbc_names[7]: os.path.join(path,"DBC","VCU DBCs","VCU DBC","v7.dbc"),
                    self.dbc_names[8]: os.path.join(path,"DBC","VCU DBCs","VCU DBC","v8.dbc"),
                    self.dbc_names[9]: os.path.join(path,"DBC","VCU DBCs","VCU DBC","v9.dbc"),
                    self.dbc_names[10]: os.path.join(path,"DBC","4W","charging parser","BU_ OBC.dbc")
                }
                for dbc, its_path in dict_dbc.items():
                    if self.dbc_text == dbc:
                        self.dbc_new_location = os.path.normpath(its_path)
                        print(its_path)
                    else:
                        continue
                    if dbc in ["Vehicle Testing Marvel","Vehicle Testing NBMS"]:
                        self.parsing_dropdown.setEditable(True)
                        text_remove = self.parsing_dropdown.findText("data summary")
                        if text_remove < 1:
                            self.parsing_dropdown.addItem("data summary")
                        self.alignment(self.parsing_dropdown)
                        self.flag_general = 1
                        # self.parsing_dropdown.currentTextChanged.connect(self.autoreadbms)
                    else:
                        text_remove = self.parsing_dropdown.findText("data summary")
                        if text_remove>=0:
                            self.parsing_dropdown.removeItem(text_remove)
                            self.flag_general = 0
                            self.heatmap_check.setCheckState(Qt.CheckState.Unchecked)
            print("DBC window opened successfully.")
        except Exception as e:
            print(f"Error: Could not open DBC window. {e}")
    def parsing_option(self,text):
        if text == "--Select type--":
            self.status.showMessage("select Parsing type",3000)
            self.upload_check.setCheckState(Qt.CheckState.Unchecked)
            self.table_check.setCheckState(Qt.CheckState.Unchecked)
            self.heatmap_check.setCheckState(Qt.CheckState.Unchecked)
        elif text == "csv file only":
            self.parsing_type = "csv file only"
            self.upload_check.setCheckState(Qt.CheckState.Unchecked)
            self.table_check.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.parsing_type = text

    def open_tyre_file(self):
        print("Calling Tyre size file...")
        try:
            self.tyre_size_window = TyreWindow()
            self.tyre_size_window.show() 
            print("Tyre size window opened successfully.")
        except Exception as e:
            print(f"Error: Could not open TyreWindow. {e}")

    def battery_details(self,text):
        if text == "others":
            self.battery_window = BatteryWindow()
            self.battery_window.show() 
            self.battery_window.battery_signal.connect(self.battery_box)
            print("Battery window opened successfully.")
        elif text == "--Select battery--":
            self.status.showMessage("select battery type",3000)
        else:#"G2F - 15.3 KWH 76.8V","G2A-19.2 KWH 96V","G2B-30.72 KWH 307.2","ATH-4 16 KWH 320V","ATH-5 19.2 KWH 384V
            battery = {
                "G2F - 15.3 KWH 76.8V": (15.3,73.6,180),
                "G2A-19.2 KWH 96V":(19.2,96,190),
                "G2B-30.72 KWH 307.2V":(30.72,307.2,95),
                "ATH-4 16 KWH 320V":(16,320,47.5),
                "ATH-5 19.2 KWH 384V":(19.2,384,47.5)
            }
            for name,values in battery.items():
                if name == text and self.vehicle_name != "S1":
                    self.Battery_name = text
                    self.Battery_Model = values[0]
                    self.Battery_Voltage = values[1]
                    self.Battery_capacity = values[2]
            if self.vehicle_name == "S1":
                text_remove = self.btn_bat.findText("G2A-18.26 KWH 92.8V")
                if text_remove < 1:
                    self.btn_bat.setEditable(True)
                    self.btn_bat.addItem("G2A-18.26 KWH 92.8V")
                    self.alignment(self.btn_bat)
                self.Battery_name = "G2A-18.26 KWH 92.8V"
                self.Battery_Model = 18.26
                self.Battery_Voltage = 92.8
                self.Battery_capacity = 190
                #S1 = 18.26, 92.8,190
        # except Exception as e:
        #     print(f"Error: Could not open BatteryWindow. {e}")

    def gear_ratio_func(self,text):
    
        if text == "others":
            self.gear_ratio_window = GearRatioWindow()
            self.gear_ratio_window.show() 
            self.gear_ratio_window.gear_ration_sgl.connect(self.extract_gear_ratio)
            print("Gear ratio window opened successfully.")
        elif text == "--Select gear ratio--":
            self.status.showMessage("select gear ratio",3000)
        else:
            gr = {
                "12.35": 12.35,
                "10.45": 10.45,
                "15.1": 15.1
            }
            for names, value in gr.items():
                if text == names:
                    self.gear_ratio = value
    def dbc_location(self,file):
        self.dbc_new_location = file
        name = self.dbc_new_location.split("/")[-1]
        self.btn_dbc.setEditable(True)
        self.btn_dbc.addItem(name)
        self.btn_dbc.setCurrentText(name)
        self.alignment(self.btn_dbc)
    def enter_vehicle_name(self,text):
        if text == "--Select name--":
            self.status.showMessage("select vehicle",3000)
        elif text == "Other":
            # self.btn_veh.setEditable(True)
            # self.btn_veh.setEditText("")
            # self.btn_veh.lineEdit().setFocus()
            # self.vehicle_name = text
            try:
                self.vehicle_window = VehicleInputBox()
                self.vehicle_window.show()
                self.vehicle_window.vehicle_name_manual.connect(self.add_name)
                print("Vehicle selection window opened.")
            except Exception as e:
                print(f"Error: Could not open VehicleInputBox. {e}")
        else:
            self.vehicle_name = text
            print(text)
        self.default()
    def add_name(self,name):
        self.vehicle_name = name
        self.btn_veh.setEditable(True)
        self.btn_veh.addItem(name)
        self.btn_veh.setCurrentText(name)
        self.alignment(self.btn_veh)
    def Tyre(self,text):
        if text == "--Select tyre--":
            self.status.showMessage("Tyre size not selected",3000)
        elif text == "others":
            self.tyre_size_window = TyreWindow()
            self.tyre_size_window.show()
            self.tyre_size_window.tyre_details.connect(self.tyre_other)

        else:
            tyre_drr = {
                "145 R12 LT 8PR": 272,
                "155 R13 LT 8PR": 290,
                "165 R14": 308,
                "185 R14": 321,
                "185 R14-(334)": 334
            }
            for name,drr in tyre_drr.items():
                if name == text:
                    self.Tyre_size_name = name
                    self.DRR = drr

    def alignment(self,object_n):
        line_edit = object_n.lineEdit()
        line_edit.setReadOnly(True)
        line_edit.setAlignment(Qt.AlignCenter)
        # Optional: disable focus or cursor to hide edit-like behavior
        line_edit.setFocusPolicy(Qt.NoFocus)
        for i in range(object_n.count()):
            object_n.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
        object_n.setMinimumHeight(32)
    def tyre_other(self,tyre_name,drr):
        self.Tyre_size_name = tyre_name
        self.DRR = drr
        self.btn_tyre.setEditable(True)
        self.btn_tyre.addItem(tyre_name)
        self.btn_tyre.setCurrentText(tyre_name)
        self.alignment(self.btn_tyre)
    #right side 
    def autoreadbms(self):
        if self.trc_files:
            path = os.path.dirname(self.trc_files[0])
            matches = glob.glob(os.path.join(path, "*bmslog.csv"))
            if matches:
                self.bms_file_location = matches[0]
                tp = self.bms_type(matches[0])
                self.bms_display.setText("BMS selected")
            else:
                self.status.showMessage("No BMS file found in trc folder!!",3000)
    def bms_selection(self):
        try:
            file_path_bms, _ = QFileDialog.getOpenFileNames(
                self, "Select BMS File", "", "BMS Files (*.csv);;All Files (*)"
            )
            self.bms_file_location = file_path_bms[0]
            if file_path_bms:
                self.bms_display.setText("BMS selected")
                self.bms_type(file_path_bms[0])
            print("BMS window opened successfully.")
        except Exception as e:
            print(f"Error: Could not open BMS file window. {e}")
    def bms_type(self,bms_path):
        try:
            df_bms = pd.read_csv(bms_path,dtype=str)
            print(f"✅ {os.path.basename(bms_path)} successfully loaded.")
            data = df_bms.values.tolist()
            #headers = df_bms.columns.tolist()
            sec_row = data[0]
            total = len(sec_row)
            numeric_count = 0
            for val in sec_row:
                try:
                    if pd.notna(val):
                        float(val)
                        numeric_count += 1
                except:
                    pass
            if numeric_count/total < 0.5:
                print("MARVEL BMS DETECTED!!!!")
                self.bottom_hint.setText("bms found \n MARVEL BMS DETECTED!")
                self.toggle_item(2,False)
                self.toggle_item(1,True)
            else:
                print("NBMS DETECTED!!")
                self.bottom_hint.setText("bms found \n NBMS DETECTED!")
                self.toggle_item(2,True)
                self.toggle_item(1,False)
            return df_bms
        except Exception as e:
            print("❌ Error reading bmslog.csv:", e)
            return None
    def resetbms(self):
        if self.bms_file_location:
            self.bms_file_location = None
            self.bottom_hint.setText("no bms file found/selected!!")
            self.bms_display.setText("--Select bms--")
            self.toggle_item(2,True)
            self.toggle_item(1,True)

    def heatmapcase(self):
        if  self.flag_general == 1:
            pass
        else:
            self.heatmap_check.setCheckState(Qt.CheckState.Unchecked)
            self.status.showMessage("Select DBC option!!",3000)
    def tablecase(self):
        if self.parsing_dropdown.currentText() == "data summary":
            pass
        else:
            self.table_check.setCheckState(Qt.CheckState.Unchecked)
            self.status.showMessage("Select data summary as parsing option!!",3000)
    def uploadcase(self):
        self.button_text = self.connect_btn_t.text()
        if self.parsing_dropdown.currentText() == "data summary" and  self.button_text == "Connected":
            # self.upload_check.setCheckState(Qt.CheckState.checked)
            pass
        elif self.parsing_dropdown.currentText() == "data summary" and self.connect_btn == 0 and self.button_text == "Connect":
            self.upload_check.setCheckState(Qt.CheckState.Unchecked)
            self.status.showMessage("Click the connect button to upload!!",3000)
        else:
            self.upload_check.setCheckState(Qt.CheckState.Unchecked)
            self.status.showMessage("Select data summary as parsing option!!",3000)
    def battery_box(self,B_name,B_Model,B_Voltage,B_Capacity):
        self.Battery_name = B_name
        self.Battery_Model = B_Model
        self.Battery_Voltage = B_Voltage
        self.Battery_capacity = B_Capacity
        self.btn_bat.setEditable(True)
        self.btn_bat.addItem(B_name)
        self.btn_bat.setCurrentText(B_name)
        self.alignment(self.btn_bat)
        print(B_name,"\n",B_Model,"\n",B_Voltage,"\n",B_Capacity)
    def extract_gear_ratio(self,text):
        self.gear_ratio = text
        self.btn_gear.setEditable(True)
        self.btn_gear.addItem(str(text))
        self.btn_gear.setCurrentText(str(text))
        self.alignment(self.btn_gear)
        print(str(text))
    def toggle_item(self, row, enabled):
        model = self.btn_dbc.model()
        if model:
            item = model.item(row)
            if item:
                if enabled:
                    # Restore default flags
                    item.setFlags(item.flags() | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                else:
                    # Remove ItemIsEnabled, keeps it grayed out
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
    def default(self):
        dict_vehicle_default = {
            "1250": ("165 R14","G2A-19.2 KWH 96V","12.35"),
            "1750": ("185 R14-(334)","ATH-5 19.2 KWH 384V","15.1"),
            "LR200": ("185 R14","G2B-30.72 KWH 307.2V","15.1"),
            "V1": ("145 R12 LT 8PR","G2F - 15.3 KWH 76.8V","12.35"),
            "V2": ("155 R13 LT 8PR","ATH-4 16 KWH 320V","12.35"),
            "V3": ("155 R13 LT 8PR","G2A-19.2 KWH 96V","12.35")
        }
        for vehicle,value in dict_vehicle_default.items():
            if vehicle == self.vehicle_type_selected and self.vehicle_name != "S1":
                self.btn_tyre.setCurrentText(value[0])
                self.btn_bat.setCurrentText(value[1])
                self.btn_gear.setCurrentText(value[2])
            elif vehicle == self.vehicle_type_selected and self.vehicle_name == "S1":
                text_remove = self.btn_bat.findText("G2A-18.26 KWH 92.8V")
                if text_remove < 1:
                    self.btn_bat.setEditable(True)
                    self.btn_bat.addItem("G2A-18.26 KWH 92.8V")
                    self.alignment(self.btn_bat)
                self.btn_tyre.setCurrentText(value[0])
                self.btn_bat.setCurrentText("G2A-18.26 KWH 92.8V")
                self.btn_gear.setCurrentText(value[2])
    def get_resource(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        # This checks if the code is running as an EXE (_MEIPASS) or as a script
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)
        # "G2F - 14.72 KWH 76.8V": (14.72,73.6,180),
        # "G2A-19.2 KWH 96V":(19.2,96,190),
        # "G2B-30.72 KWH 307.2V":(30.72,307.2,95),
        # "ATH-4 16 KWH 320V":(16,320,47.5),
        # "ATH-5 19.2 KWH 384V":(19.2,384,47.5)
        # #S1 = 18.26, 92.8,190
        # """
        # "12.35": 12.35,
        #         "10.45": 10.45,
        #         "15.1": 15.1
        # """
        #LR00 battery unknown 
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     app.setStyleSheet("""
#         QMainWindow { background-color: #f8f9fa; }
#         #BmsFrame { 
#             background-color: #e9ecef; 
#             border: 1px solid #ced4da; 
#             border-radius: 6px; 
#         }
#         QPushButton { 
#             background-color: white; 
#             border: 1px solid #adb5bd; 
#             border-radius: 4px; 
#             padding: 6px 12px;
#             min-width: 120px;
#         }
#         QPushButton:hover { background-color: #e2e6ea; border-color: #007bff; }
#         QLabel { font-family: 'Segoe UI', Arial; font-size: 15px; font-weight: bold }
#     """)
    
#     window = EulerParserMain()
#     window.show()
#     sys.exit(app.exec())
    
    
