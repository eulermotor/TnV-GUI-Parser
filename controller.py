from PySide6.QtWidgets import (
    QStackedWidget, QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QStatusBar, QSizePolicy,QGraphicsDropShadowEffect,QMessageBox
)
from PySide6.QtGui import QAction, QIcon,QShortcut, QKeySequence
from PySide6.QtCore import Qt, QSize,QTimer, Signal,QThread, QObject
import sys
import os
from login_screen import LoginScreen
from vehicle_type import vehicletype
from vehicle_var_4W import varientselection
from vehicle_var_3W import varientselection3W
from thirdMain_screen import EulerParserMain
from third_main_screen_3W import EulerParserMain3W
from progress_bar_main import progressbar
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import socket
import webbrowser
from urllib.parse import urlparse, parse_qs
class AuthWorker(QObject):
    finished = Signal(str)  # Sends the email (or None) back to the main thread when done

    def __init__(self, credential_path,user_mail):
        super().__init__()
        self.credential_path = credential_path
        self.mail = user_mail
        
    def run_verification(self):
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close() # Free it up so Google Flow can bind to it
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credential_path, 
                scopes=SCOPES,
                redirect_uri=f'http://localhost:{port}/'
            )
            
            # 2. Generate authorization URL
            auth_url, _ = flow.authorization_url(prompt='select_account')
            
            # 3. Spin up our own native socket server with a HARD 30-second timeout
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(20.0) # Absolute wall-clock timeout
            server.bind(('localhost', port))
            server.listen(1)
            
            # Launch Chrome manually
            
            print(f"Opening browser to URL: {auth_url}")
            webbrowser.open(auth_url)
            
            # Wait for Google's redirect response
            try:
                conn, addr = server.accept()
            except socket.timeout:
                print("❌ Verification timed out! (No response within 30 seconds)")
                server.close()
                self.finished.emit(None)
                return
                
            # Read incoming URL parameters from Google redirect redirect
            data = conn.recv(2048).decode('utf-8')
            
            # Send a quick "Success" text response back to the browser window
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            response += "<html><body style='font-family:sans-serif; text-align:center; padding-top:50px;'>"
            response += "<h2>Verification complete!</h2><p>You can close this tab now and return to the application.</p>"
            response += "</body></html>"
            conn.sendall(response.encode('utf-8'))
            conn.close()
            server.close()
            
            first_line = data.split('\r\n')[0]
            request_path = first_line.split(' ')[1] # Grabs just the "/?code=..." part
            
            # Use urllib to convert the string query parameter safely into a dictionary
            parsed_url = urlparse(request_path)
            query_params = parse_qs(parsed_url.query)
            
            # parse_qs stores values as lists, grab the first element safely
            code_list = query_params.get("code")
            if not code_list:
                print("❌ Error: Authorization code not found in redirect URL headers.")
                self.finished.emit(None)
                return
                
            code = code_list[0]
            # 4. Exchange authorization code for actual temporary credentials token
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            oauth2_service = build('oauth2', 'v2', credentials=creds, static_discovery=False, cache_discovery=False)
            user_info = oauth2_service.userinfo().get().execute()
            
            verified_email = user_info.get('email')
            if not verified_email.lower().endswith('@eulermotors.com'):
                print(f"Access Denied: {verified_email} is not a valid Euler Motors account.")
                self.finished.emit("INVALID_DOMAIN")
                return
            if not self.mail == verified_email:
                self.finished.emit("NOT_SIMILAR")
                return
            self.finished.emit(verified_email)
        except Exception as e:
            print(f"Auth background error caught: {e}")
            self.finished.emit(None)
class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        self.connect_btn_flag = 0
        self.vehicle_of_choice = None
        self.user_email = None
        self.setWindowTitle("PARSER")
        # self.setMinimumSize(900, 600)
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon(self.get_resource("logo_only.png")))
        # ===== STACK =====
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        # ===== SCREEN =====
        self.login_screen = LoginScreen()
        self.vehicle_screen = vehicletype()
        self.vehicle_selected_4W = varientselection()
        self.vehicle_selected_3W = varientselection3W()
        
        
        # adding the widgets
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.vehicle_screen)
        self.stack.addWidget(self.vehicle_selected_4W)
        self.stack.addWidget(self.vehicle_selected_3W)
        
        # connect signal
        self.login_screen.login_success.connect(self.goto_main_app)
        self.vehicle_screen.vehicle_signal.connect(self.V_choice)
        self.vehicle_selected_4W.vehicle_variant.connect(self.varient)
        self.vehicle_selected_3W.vehicle_variant.connect(self.varient)
        # Hide toolbar initially
        self.toolbar = None
        
    # ===== AFTER LOGIN =====
    def goto_main_app(self, name, email):
        print(name, email)

        self.user_name = name
        self.user_email = email
        
        # Create toolbar & menu
        self.setup_toolbar()
        self.setup_menu_bar()

        # Status bar
        self.setStatusBar(QStatusBar(self))

        self.status_label = QLabel("ver 1.0")
        self.statusBar().addWidget(self.status_label)

        author_label = QLabel("by Vinayak Kushwah")
        self.statusBar().addPermanentWidget(author_label)

        self.statusBar().setStyleSheet("""
            QStatusBar { border-top: 1px solid gray; padding: 2px; }
        """)
        container = QWidget()
        container.setObjectName("AppBackground")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.stack)

        self.setCentralWidget(container)

        container.setStyleSheet(f"""
            #AppBackground {{
                border-image: url({self.get_resource("app_back.png").replace('\\', '/')}) 0 0 0 0 stretch stretch;
            }}
        """)
        # Load vehicle screen
        
        
        
        self.stack.setCurrentWidget(self.vehicle_screen)
        
        # self.vehicle_of_choice = vehicle_T
        # self.stack.setStyleSheet("""
        #     QStackedWidget {
        #         border-image: url("app_back.png") 0 0 0 0 stretch stretch;
        #     }
        # """)
        #vehcle variant selection screen 4W and 3W
    def get_resource(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        # This checks if the code is running as an EXE (_MEIPASS) or as a script
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)
        
        
        
        
    # ===== COMMON TOOLBAR =====
    def setup_toolbar(self):
        if self.toolbar:
            self.toolbar.show() 
            return

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(40, 20))
        self.addToolBar(self.toolbar)
        spacer0 = QWidget()
        spacer0.setFixedWidth(10)  
        self.toolbar.addWidget(spacer0)
        #previous button
        self.prev_icon = QPushButton()
        self.prev_icon.setFixedSize(28,28)
        self.prev_icon.setIcon(QIcon(self.get_resource("left-arrow_2.png")))
        self.prev_icon.setObjectName("Prev_btn")
        self.prev_icon.setIconSize(QSize(26,26))
        # self.prev_icon.setAlignment(Qt.AlignCenter)
        self.prev_icon.setStyleSheet(f"""
            #Prev_btn {{
                border-radius: 14px;
                background-color: #f0f0f0;
                border: 2px solid #ccc;
            }}        
            
            #Prev_btn:hover {{
                background-color: #DCF0FF;
                border: 10px #4BC4FF;
            }}
            #Prev_btn:pressed {{
                background-color: #a0a0a0;
            }}
        """)
        # background-color: white;
        #QICon {{
            #     border: 1px;
            #     border-radius: 5px;
            #     padding: 5px;
            # }}
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setToolTip("Connect to internet")
        self.connect_btn.clicked.connect(self.handle_connect)
        self.prev_icon.clicked.connect(self.previous_button)
        self.toolbar.addWidget(self.prev_icon)
        spacer1 = QWidget()
        spacer1.setFixedWidth(10)  
        self.toolbar.addWidget(spacer1)
        # self.toolbar.addSeparator()

        home_action = QAction(QIcon(self.get_resource("euler-motors-logo-hd.png")), "Home", self)
        home_action.triggered.connect(self.go_home)

        self.toolbar.addAction(home_action)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        
        self.toolbar.addWidget(self.connect_btn)
        # push everything left
        spacer2 = QWidget()
        spacer2.setFixedWidth(20)  
        self.toolbar.addWidget(spacer2)

        # user icon on right
        user_icon = self.create_user_icon(self.user_name)
        self.toolbar.addWidget(user_icon)
        self.toolbar.addSeparator()
        spacer3 = QWidget()
        spacer3.setFixedWidth(10)  
        self.toolbar.addWidget(spacer3)
    def setup_menu_bar(self):
        if hasattr(self, "menu_created") and self.menu_created:
            return

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("Add new vehicle", self.add_vehicle)
        file_menu.addAction("Add new DBC file", self.add_DBC)
        file_menu.addAction("Quit", self.quit)

        setting_menu = menu_bar.addMenu("&Settings")
        setting_menu.addAction("Themes", self.themes)
        setting_menu.addAction("Font size", self.fontsize)
        setting_menu.addAction("Auto Sync", self.autosync)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("Facing issue!!")
        help_menu.addAction("About")

        self.menu_created = True 
    def go_home(self):
        self.stack.setCurrentWidget(self.login_screen)
        if self.toolbar: self.toolbar.hide()
        if self.statusBar(): self.statusBar().hide()
        if self.connect_btn_flag == 1:
            self.connect_btn.setText("Connect")
            self.connect_btn.setEnabled(True)
            self.connect_btn_flag = 0
    # def setup_background(self):
    def add_vehicle(self):
        print("Add vehicle clicked")

    def add_DBC(self):
        print("Add DBC clicked")

    def quit(self):
        self.close()

    def themes(self):
        print("Themes clicked")

    def fontsize(self):
        print("Font size clicked")

    def autosync(self):
        print("Auto sync clicked")
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.setFixedSize(900, 600)  # restore fixed size
        else:
            self.showFullScreen()
    def previous_button(self):
        #Parsing type selection screen
        
        if self.stack.currentWidget() == self.vehicle_screen:
            self.stack.setCurrentWidget(self.login_screen)
            if self.toolbar: self.toolbar.hide()
            if self.statusBar(): self.statusBar().hide()
            if self.connect_btn_flag == 1:
                self.connect_btn.setText("Connect")
                self.connect_btn.setEnabled(True)
                self.connect_btn_flag = 0
                self.vehicle_of_choice = None
        elif self.stack.currentWidget() in [self.vehicle_selected_4W, self.vehicle_selected_3W]:
            self.stack.setCurrentWidget(self.vehicle_screen)
            if self.connect_btn_flag == 1:
                self.connect_btn.setText("Connect")
                self.connect_btn.setEnabled(True)
                self.connect_btn_flag = 0
            self.vehicle_of_choice = None
        elif hasattr(self, 'parser_main_screen') and self.stack.currentWidget() == self.parser_main_screen:
            if self.vehicle_of_choice == "4W":
                self.stack.setCurrentWidget(self.vehicle_selected_4W)
                # print("it does come here in 4W")
        elif hasattr(self, 'parser_main_screen_3W') and self.stack.currentWidget() == self.parser_main_screen_3W:
            if self.vehicle_of_choice == "3W":
                self.stack.setCurrentWidget(self.vehicle_selected_3W)
                # print("it does come here in 3W")
    def create_user_icon(self, email):
        first_letter = email.strip()[0].upper()

        avatar = QLabel(first_letter)
        avatar.setFixedSize(28, 28)
        avatar.setAlignment(Qt.AlignCenter)

        avatar.setStyleSheet(f"""
            QLabel {{
                border-radius: 14px;
                background-color: white;
                color: black;
                font-weight: bold;
                font-size: 13px;
                border: 2px solid black;
            }}
        """)

        return avatar
    def V_choice(self,vehicle_T):
        self.vehicle_of_choice = vehicle_T
        if self.vehicle_of_choice == "4W":
            self.stack.setCurrentWidget(self.vehicle_selected_4W)
    
        elif self.vehicle_of_choice == "3W":
            self.stack.setCurrentWidget(self.vehicle_selected_3W)

        else:
            self.status_label.setText("Invalid vehicle type")
            self.status_label.setStyleSheet("color: red;")
            QTimer.singleShot(3000, self.reset_status)
        
    def go_to_vehicletype(self):
        current = self.stack.currentWidget()
        if current in [self.vehicle_selected_4W or self.vehicle_selected_3W]:
            self.stack.setCurrentWidget(self.vehicle_screen)
        # elif current == self.parser_main_screen:
        #     self.stack.setCurrentWidget(self.vehicle_selected_4W)
    def varient(self,vehicle_V):
        self.V_variant  = vehicle_V
        if vehicle_V and self.vehicle_of_choice == "4W":
            self.parser_main_screen = EulerParserMain(vehicle_V,self.user_email,self.connect_btn_flag,self.connect_btn,self.statusBar())#self.statusBar
            self.stack.addWidget(self.parser_main_screen)
            self.stack.setCurrentWidget(self.parser_main_screen)
            self.parser_main_screen.Parsing_screen.connect(self.parse)
        elif vehicle_V and self.vehicle_of_choice == "3W":
            self.parser_main_screen_3W = EulerParserMain3W(vehicle_V,self.user_email,self.connect_btn_flag,self.connect_btn,self.statusBar())#self.statusBar
            self.stack.addWidget(self.parser_main_screen_3W)
            self.stack.setCurrentWidget(self.parser_main_screen_3W)
            self.parser_main_screen_3W.Parsing_screen.connect(self.parse)
    def parse(self,vehicle_name,trc_files,dbc_new_location,parsing_type,Tyre_size_name,DRR,bms_file_location,Battery_name,Battery_Model,Battery_Voltage,Battery_capacity,gear_ratio,flag_heatmap,flag_table,flag_google_upload,vehicle_type_new):
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
        # if self.vehicle_of_choice == "3W":
        #     self.V_variant == vehicle_type_new
        self.progress_bar = progressbar(vehicle_name,trc_files,dbc_new_location,parsing_type,Tyre_size_name,DRR,bms_file_location,Battery_name,Battery_Model,Battery_Voltage,Battery_capacity,gear_ratio,flag_heatmap,flag_table,flag_google_upload,vehicle_type_new,self.vehicle_of_choice,self.user_email)
        self.stack.addWidget(self.progress_bar)
        self.stack.setCurrentWidget(self.progress_bar)
        if self.stack.currentWidget() == self.progress_bar:
            self.toolbar.hide()
            # self.toolbar == None 
        self.progress_bar.progress_bar_sgl.connect(self.goto_parser_main_screen)
    def goto_parser_main_screen(self,sig):
        if sig == 1 and self.vehicle_of_choice == "4W":
            self.stack.setCurrentWidget(self.parser_main_screen)
            self.toolbar.show()
        elif sig == 1 and self.vehicle_of_choice == "3W":
            self.stack.setCurrentWidget(self.parser_main_screen_3W)
            self.toolbar.show()
    def go_to_4W(self):
        current = self.stack.currentWidget()
        if current == self.parser_main_screen:
            self.stack.setCurrentWidget(self.vehicle_selected_4W)
    def reset_status(self):
        self.status_label.setText("ver 1.0")
        self.status_label.setStyleSheet("color: black;")

        # from progress_bar_main import progressbar
            
            # self.stack.setCurrentWidget(self.progress_bar)
    def handle_connect(self):
        """Triggered when the user clicks your existing Connect button"""
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Verifying...")
        credentials_path = self.get_resource("backend/credentials.json")
        # verified_email = self.verify_chrome_login()
        self.auth_thread = QThread()
        self.auth_worker = AuthWorker(credentials_path,self.user_email)
        self.auth_worker.moveToThread(self.auth_thread)

        # Connect signals and slots
        self.auth_thread.started.connect(self.auth_worker.run_verification)
        self.auth_worker.finished.connect(self.on_verification_complete)
        
        # Start execution without blocking the main application UI loop
        if self.vehicle_of_choice == None:
            self.status_label.setText("First select the Vehicle type!!")
            self.connect_btn.setText("Connect")
            self.connect_btn.setEnabled(True)
            QTimer.singleShot(3000, self.reset_status)
            self.connect_btn_flag = 0
        else:
            self.auth_thread.start()
    def on_verification_complete(self,verified_email):
        self.auth_thread.quit()
        self.auth_thread.wait()
        if verified_email in [None, "INVALID_DOMAIN"]:
            self.status_label.setText("Verification failed. Please use your @eulermotors.com ID.")
            self.connect_btn.setText("Connect")
            self.connect_btn.setEnabled(True)
            self.connect_btn_flag = 0
            QApplication.processEvents()
            return
        elif verified_email == "NOT_SIMILAR":
            self.status_label.setText("Use same mail ID as your chrome login mail ID.")
            self.connect_btn.setText("Connect")
            self.connect_btn.setEnabled(True)
            self.connect_btn_flag = 0
            return
        # else:
        #     # 2. Lock in their real identity
        #     self.user_email = verified_email
        #     self.status_label.setText(f"Connected: {self.user_email}")
        #     self.connect_btn.setText("Connected")
        #     self.connect_btn_flag = 1
        # --- PHASE 2: VERIFY IF THEY HAVE EDIT PERMISSIONS ON GOOGLE SHEETS ---
        self.status_label.setText("Checking database permissions...")
        
       
        if self.vehicle_of_choice == "4W":
            target_spreadsheet_id = "1L6W5pay9hMtc22DRUZa4-1KNsMNEjhmd48XSKd4CPQ8" 
        elif self.vehicle_of_choice == "3W":
            target_spreadsheet_id = "1TiTbPuTobJOnAO3HbH15xKbTO--J9yP-WsawDKNM0q4"
        else:
            return
        has_edit_rights = self.check_spreadsheet_permission(verified_email, target_spreadsheet_id)
        print(has_edit_rights)
        if has_edit_rights == False:
            # Identity is real, but they aren't authorized on this file!
            self.status_label.setText(f"❌ Access Denied: {verified_email} is not permitted to edit this sheet.")
            self.connect_btn.setText("Connect")
            self.connect_btn.setEnabled(True)
            QTimer.singleShot(3000, self.reset_status)
            self.connect_btn_flag = 0
            return

        # --- PHASE 3: BOTH PASSED! SUCCESS! ---
        self.user_email = verified_email
        self.status_label.setText(f"Connected & Authorized: {self.user_email}")
        self.connect_btn.setText("Connected")
        QTimer.singleShot(300, self.reset_status)
        self.connect_btn_flag = 1
   
    def check_spreadsheet_permission(self, verified_email, spreadsheet_id):
        """
        Queries the master Google Drive API to verify if the logged-in 
        user has permission to edit the target spreadsheet.
        """
        try:
            # 1. Build your master drive service using your background credentials
            creds = self.get_credentials() # Using your master token.json
            drive_service = build('drive', 'v3', credentials=creds, static_discovery=False, cache_discovery=False)
            
            print(f"Checking spreadsheet access for: {verified_email}...")
            
            # 2. Fetch the metadata list of everyone who has access to this sheet
            param_fields = "permissions(emailAddress, role, type)"
            perm_list = drive_service.permissions().list(fileId=spreadsheet_id, fields=param_fields).execute()
            permissions = perm_list.get('permissions', [])
            
            # 3. Scan the access control list
            for perm in permissions:
                user_role = perm.get('role')
                # Look only for people who can write/modify (owner or writer)
                if user_role in ['owner', 'writer']:
                    
                    # Case A: Explicitly added by their exact email address
                    if perm.get('emailAddress', '').lower() == verified_email.lower():
                        print("Verified! on spreadsheet")
                        return True
                    
                    # Case B: The sheet is set to company-wide editing ("Anyone at Euler Motors with link can edit")
                    if perm.get('type') == 'domain' and verified_email.lower().endswith('@eulermotors.com'):
                        print("Verified! on spreadsheet")
                        return True
                    
                        
            # If the loop finishes without finding editing rights, they are locked out
            return False

        except Exception as e:
            print(f"Failed to verify spreadsheet access rules: {e}")
            return False
    def get_credentials(self):
        creds = None
        
        # The file token.json stores the user's access and refresh tokens.
        # It is created automatically when the authorization flow completes for the first time.
        # token_path = os.path.join(self.path_current,"backend","token.json")
        token_path = self.get_resource("backend/token.json")
        # Credentials_path = os.path.join(self.path_current,"backend","credentials.json")
        Credentials_path = self.get_resource("backend/credentials.json")
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Credentials_path, self.SCOPES)
                # Starts a local webserver to handle the auth redirect
                creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return creds