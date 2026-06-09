import random
import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import getpass
import requests

import pandas as pd
import glob
import sys
import numpy as np
import re
from PySide6.QtCore import QThread, Signal

class ProcessingWorkerupload(QThread):
    job_starting = Signal(int)
    job_completed = Signal(int)
    job_failed = Signal(int,str)
    def __init__(self,path_n,vehicle_varient,vehicle_name,vehicle_type,email_c,remarks):
        super().__init__()
        self.VVAR = vehicle_varient
        self.VNAME = vehicle_name
        self.VTYPE = vehicle_type
        self.email_to_use = email_c
        self.path_new = os.path.abspath(os.path.dirname(path_n[-1]))
        self.remark_of_error = remarks
    def run(self):
        self.job_starting.emit(0)
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        # https://script.google.com/macros/s/AKfycbwP-zkPuItPlqzbQcwqcANp77PjPZ54_fyyyIC2JZDOt743KCFu-U5Cx9JyABavXzIt/exec
        self.WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwP-zkPuItPlqzbQcwqcANp77PjPZ54_fyyyIC2JZDOt743KCFu-U5Cx9JyABavXzIt/exec"
        if self.VTYPE == "4W":
            self.SECRET_KEY = "4W@Euler"
        else:
            self.SECRET_KEY = "3W@Euler"
        self.path_current = self.get_resource("")
        self.UPLOAD()
    def get_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        # It is created automatically when the authorization flow completes for the first time.
        token_path = os.path.join(self.path_current,"backend","token.json")
        Credentials_path = os.path.join(self.path_current,"backend","credentials.json")
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

    def log_upload_to_sheet(self,sheets_service, spreadsheet_id, file_name, user_email):
        """
        Appends a new logging row into the target Google Sheet.
        Columns: Name, Date, Time, Mail Id
        """
        try:
            # Generate real-time stamps
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M:%S')
            file_name_new = file_name.split(".")[0]
            # Structure data as a 2D array matrix row
            row_data = [[file_name_new, current_date, current_time, user_email,self.remark_of_error]]
            body = {'values': row_data}
            
            # 'Sheet1!A1' tells Google to look at the first tab called Sheet1. 
            # Combined with APPEND, it automatically finds the last empty row below row 1.
            range_name = 'Sheet1!A1' 
            
            sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED', # Parses strings natively (e.g. keeps dates as dates)
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(" Successfully logged metadata to Google Sheet.")
        except Exception as e:
            print(f"⚠️ Failed to log to Google Sheet: {e}")
            self.job_failed.emit(0,e)


    def upload_and_log_file(self,file_path, folder_id, spreadsheet_id):
        try:
            # Initialize credentials once
            creds = self.get_credentials()
            
            # Build both API clients
            drive_service = build('drive', 'v3', credentials=creds, static_discovery=False, cache_discovery=False)
            sheets_service = build('sheets', 'v4', credentials=creds, static_discovery=False, cache_discovery=False)
            
            # --- STEP 1: GET THE EMAIL OF CLIENT INITIATING THIS ---
            # Fetch profile metadata of whoever is logged into token.json
            
            user_email = self.email_to_use
            
            # --- STEP 2: UPLOAD THE DESKTOP FILE ---
            file_name = os.path.basename(file_path)
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)
            
            print(f"Uploading {file_name} to Drive...")
            file = drive_service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id'
            ).execute()
            
            print(f" Success! File uploaded to Drive. ID: {file.get('id')}")
            
            # --- STEP 3: LOG DATA TO EXCEL/SHEETS ---
            self.log_upload_to_sheet(sheets_service, spreadsheet_id, file_name, user_email)
            #app script trigger
            return file.get('id')

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    def send_data_to_google(self,data_to_process):
        # Automatically grabs the logged-in Windows/Mac OS username (e.g., "john.smith")
        current_os_user = getpass.getuser()
        
        payload = {
            "secret_key": self.SECRET_KEY,
            "os_user": current_os_user,
            "data": data_to_process
        }
        
        try:
            # Send data to your permanent Gateway Web App
            response = requests.post(self.WEB_APP_URL, json=payload)
            
            if response.status_code == 200:
                print("Server Response:", response.json())
                self.job_completed.emit(0)
            else:
                print(f"HTTP Error: {response.status_code}")
                self.job_failed.emit(0,response.status_code)
                
        except Exception as e:
            print(f"Network error: {e}")
            self.job_failed.emit(0,e)
    def UPLOAD(self):
        # REPLACE THESE WITH YOUR ACTUAL VALUES
        # print("Choose the vehicle type: ")
        # x = int(input("1) 4W\n2) 3W\n"))
        # print("Choose the vehicle varient: ")
        # y = int(input("1) V1\n2) V2\n3) V3\n"))
        # print("Choose the vehicle name: ")
        # z = int(input("1) 7002\n2) 7003\n3) 7005\n4) 7006\n5) 7009\n"))
        def generating_name(v_type,v_varient,v_name):#name = 4WV17002mmyyrandom
            now = datetime.now()
            current_date = now.strftime('%m-%d')
            c_date = current_date.replace("-","") 
            if v_varient.endswith("_2.0"):
                new_var = v_varient.removesuffix("_2.0") + "2p0"
            else:
                new_var = v_varient
            n_var = new_var.replace("_", "")
            if v_name == "PT12 2.0":
                v_name = "PT122p0"
            elif v_name == "R1 2.0":
                v_name = "R12p0"
            name = f"{v_type}_{n_var}_{v_name}_{c_date}{random.randint(1000,9999)}.csv"
            return name
        path_dir = self.path_new
        old_path = os.path.join(path_dir,"Final_summary.csv")
        
        VEHICLE_FOLDERS_V1 = {
            "7002":"1UgXA7o1Bt-1_gfkeOw-7G0p_Xe-YUR68",
            "7003":"17etnPZ1o9MTk4CxsG6tTWD0oGqbPfg_z",
            "7005":"1UU5SitVE3aWO9yBm4R_-XbFfdt8krreM",
            "7006":"1ogDG2UgdGy1OFGxezrshI6-MT5IE0Fxo",
            "7009":"1dVWj8v3DSrgBWBEfaPtaqSKuAsNbDa6X"
        }
        
        VEHICLE_FOLDERS_V2 = {
        "7004": "1DiMKA5-yHn4OFiYlNB-nJBoHTz1aRHT1",
        "7019": "1WX_Cl8RLc1aUPTbnslLbWZO-qvPH02RN",
        "7042": "1JWerYUia6bSPwUpox0ukYfmlM3MzULpP",
        "7070": "1Jn6qVPyavaLnx3jxB1MlmqtkE_Hr-FOR",
        "7172": "1NcpR2x5RPJjel0PXvi7Oo1c07kXkt6a9"
        
        }
        VEHICLE_FOLDERS_V3 = {
        "7001": "18RwkF1GD5gt_p0A1v4Ph4Z6SNdR15-78",
        "7007": "1yRJGMJAOOyEuAyhr37_lza7ZYJVyAlwy",
        "7008": "1sVN11w4m9IuBohKUOAil5xoE8usInIGf",
        "7010": "15K3_NZnjQPOIvmJkGM7VJfA2tQBeFaqu"
        
        }
        VEHICLE_FOLDERS_1250 = {
        "S1": "1-IB3X6sHyzQm2blFNg6FH3uvVx9rz_73",
        "S2": "1XHLdp93-BcVwvdczkkWYwl_2iDEcOU1r",
        "S3": "18jU8MkCED_lVLhwsYEEXCL179go9UjV4",
        "S4": "1vFgU_cWTPieUIXvKVL9x0S6A-L3LpwM8"
        
        }
        VEHICLE_FOLDERS_1750 = {
        "X00": "1S8O6Sj6Q2R_p3oYlEJ-glUwBaWLWP91C",
        "X01": "1qoKtHL-XbEMtCzarYQNWyOs3EmNL6Hve",
        "X02": "1_hBxEi6deDmpLulgpmItUUda-idxlWsd",
        "X03": "1NsHu7YIcqNvFhDEwQ3OrV_4ZAj_VDYQZ",
        "X04": "17r_ern6SYdwUTEw-XPemM_2d6tq9SBFZ"
       
        }
        VEHICLE_FOLDERS_LR200 = {
        "LR00": "1iZ5dpN3gTYlw3CATAm5f9daG1pe-RFu5",
        "LR01": "1d8K2cefEDDDSoiDypwaskMMP7ZXOhz9W",
        "LR02": "1iGfdELFBz_XqWJemueY2acTlZdWlh8M4",
        "LR03": "1DN8TfhGgVqBqA-7Wjgu7l7JUQt6585K3"
        }
        SR_HL = {}
        TR_HL = {
            "HT1":"1hFtA73UON6tFXKkigJyJ4dtkGF2xwhQC",
            "HX3":"1RLg9MILK3OmZhM39UjSuRf3NzgChiU4b",
            "J1":"1-1M4rt_QrNQxTpleFJPbtguu3s4f6t9G",
            "M1":"1aO6HtBfi9Hy8vbAvIT-jDH8KeQJ56fnx",
            "PX1":"1BM6NS3xnlLQ7R9y7XpcK5UGHnK72-3gQ",
            "PX2":"1vYhlhIzJbODg3BT2KjKEhbi3s-2HpglI",
            "PX3":"1thLDpiJG41TQiUduPDHlulYsIXs8UoCM",
            "R6":"1qWztwcO0owsPsklLJc_ARagkfza1qpto"
        },
        XR_HL = {
            "HX1":"1wCgXY0PYZGfYr-BTJdttRY5suUC1G7k3"
        }
        SR_HC = {}
        TR_HC ={
            "PT6":"1YJlABhYAcq2FUGv8fLvUHpbrwVCYi6mg",
            "PT10":"1O7tFQlQPi9gXwZk_4rGu6AWnVdEhbHWl",
            "PT12":"11VgsB9r5kYs4l4YdH6a6jE-NMnISHaoK",
            "PT13":"1T8PTx0SYxoaunqcbKXpcQy3rXGjvdZNL"
        }
        XR_HC = {}
        SR_HR = {
            "NV7":"1yV6J__6kaBrj-LqLIl4XZeA_ecGoejyl"
        }
        TR_HR = {
            "NP1":"14CSWYuptWNW1XB299gRlNLgc1MzAPVqF",
            "NP2":"1yoQHXIW7R8tPjCC2WYXJZGRQmlahBlfE",
            "PT1":"1UDbVSAV-f5QGbUweKT87CMnlMfiRkxZ4"
        }
        XR_HR = {}
        SR_NEO = {
            "NE3":"1lKW_Gt-knRxnWfIN08XY5h6PCThDBK0D"
        }
        TR_NEO = {}
        XR_NEO = {
            "NE1":"1RmpoxiFthL-LvAy5fNOELWqDG6kQnnXS",
            "NE4":"1GPFjzZQYgJsR4KY-4ni_QjcgPi3wlYxQ"
        }
        SR_HR_2P0 = {
            "NV2":"14uOzfWJ0D2SJKEXwPpJscqV9VdYXjWM-"
        }
        TR_HR_2P0 = {
            "PT12 2.0":"1EnIM32tHzvJlT0CTOzjDe1Km0BVXZyv8"
        }
        XR_HR_2P0 = {
            "P4":"1pJbvuhm49_iNcRtcvSUComoaISzvWstY",
            "PT4":"1yKWp5QQnQaqrFXC1Ng1JkEF56jTazL6e"
        }
        SR_HL_2P0 = {}
        TR_HL_2P0 = {}
        XR_HL_2P0 = {
            "R1 2.0":"1WGq4zKaTdF6CtCCdSPeF7dfEBKvVVwTp"
        }

        DICT = {
            "V1":(VEHICLE_FOLDERS_V1,"1TwJNYdGF3b2rgrfAzL7ehWpZ_EYELb1R"),
            "V2":(VEHICLE_FOLDERS_V2,"1beNtUU1RlSRpgzIJoA3HLBwCC8PaBy9t"),
            "V3":(VEHICLE_FOLDERS_V3,"1rnnDx1nQaZ0AVmduDibMqS9bYkbNf_wd"),
            "1250":(VEHICLE_FOLDERS_1250,"1SdCZsxE4o6n5AbpVVdEqqb5iw6VA9p0x"),
            "1750":(VEHICLE_FOLDERS_1750,"1IuAcAI1ZMYM7UUzcKI4-LM5GTNMyeabC"),
            "LR200":(VEHICLE_FOLDERS_LR200,"10H8QfQiBuenbrETo4i0iotsGvuQLejRK"),
            "SR_HL": (SR_HL,"16BD2PbNvk_wwnlMpjAyxxLnWdwVpZAlw"), 
            "TR_HL": (TR_HL,"1LVJrEf-Z5ChW1aiGOgiMvWEgMiKkvDd8"),
            "XR_HL": (XR_HL,"1e5KRnCp8ImE6614bqPrn7FRtdEH--rYr"),
            "SR_HC": (SR_HC,"1niqwGUbWBpWpAL-XeaorxFkCB34oKzXj"),
            "TR_HC": (TR_HC,"1XcEXoNEJFZlZ3BJH1Q5oI1jRJF_eOKal"),
            "XR_HC": (XR_HC,"1Xkd0gMfJ-BHNJn9qpGACenxdYw4A0P0y"),
            "SR_HR": (SR_HR,"1AVRmbRHDWCuiFb8axZH-m-nyTt6HaCV7"),
            "TR_HR": (TR_HR,"1gUe_QYp02xP-CVjvmwCns7lBVEPOiyAl"),
            "XR_HR": (XR_HR,"1h20gxytbzuq8mT1ORbgNSNZL6sFH5pfC"),
            "SR_NEO": (SR_NEO,"1pLTHsm650Vl6pk4y5ZT0VgrtFMw-heKP"),
            "TR_NEO": (TR_NEO,"1WxOTLBrsGGYKp9dIQ4H6BrEYtYu9n3wU"),
            "XR_NEO": (XR_NEO,"14ksTq_HLz42bhZNLovX7gDrvkKJt3R5p"),
            "SR_HR_2.0":(SR_HR_2P0,"1j0E5Bf3ObDGj8yDJAQILtCNwxuqjjzAu"),
            "TR_HR_2.0":(TR_HR_2P0,"1iNBmQXAFWaBFX4_Sx5-3_JoNknsVDfQ9"),
            "XR_HR_2.0":(XR_HR_2P0,"10MH-kce9vHgRDHIxIZYajV53leeT37oQ"),
            "SR_HL_2.0":(SR_HL_2P0,"1nexmW13BkJTOidyKNjxzhRlyhu8CaGEX"), 
            "TR_HL_2.0":(TR_HL_2P0,"19ruyxdvKii6-5evxR7-SmWifepNtYuyk"),
            "XR_HL_2.0":(XR_HL_2P0,"1XsTwpDLwvQzwJwapKp4iz0Lf4EgHcbk3"),
        }
        for varient, value in DICT.items():
            if self.VVAR == varient:
                dictionary_name = value[0]
                others_ID = value[1]
        v_name = self.VNAME
        Target_location = None
        for name, values in dictionary_name.items():
            if v_name == name:
                Target_location = values
        if Target_location == None:
            Target_location = others_ID

        name = generating_name(self.VTYPE,self.VVAR,self.VNAME)
        new_path = os.path.join(path_dir,name)
        if os.path.exists(old_path):
            os.rename(old_path,new_path)
        else:
            print("Unable to find Final_summary.csv!")
        TARGET_FOLDER_ID = Target_location
        FILE_TO_UPLOAD = new_path 
        if self.VTYPE == "4W":
            LOG_SPREADSHEET_ID = '1d4AbAJPHwDoYDPhXIRqrGVTjhcr7YFjQMl3iJlIekSw'
        else:
            LOG_SPREADSHEET_ID = '1dm_yPK6Qln2zhQmjQGWqvB_cELmchBTSODOFvW4etj4'
        self.upload_and_log_file(FILE_TO_UPLOAD, TARGET_FOLDER_ID,LOG_SPREADSHEET_ID)
        #1d4AbAJPHwDoYDPhXIRqrGVTjhcr7YFjQMl3iJlIekSw
        self.send_data_to_google("Uploading data!!")
    def get_resource(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        # This checks if the code is running as an EXE (_MEIPASS) or as a script
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)


    