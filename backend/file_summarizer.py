import os
import pandas as pd
import logging
import glob
import csv
from datetime import datetime
import openpyxl
import math
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import re
from matplotlib.table import Table
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
import warnings
warnings.filterwarnings("ignore")
from collections import defaultdict
from PySide6.QtCore import QThread, Signal
import time
# Setup logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ProcessingWorkersummary(QThread):
    job_starting = Signal(int)
    job_completed = Signal(int)
    job_failed = Signal(int,str)
    # data = Signal(int,int,str)
    def __init__(self,vehicle_name,trc_files,dbc_new_location,Tyre_size_name,DRR,bms_file_location,Battery_name,Battery_Model,Battery_Voltage,Battery_capacity,gear_ratio,vehicle_variant):
        super().__init__()
        # self.trc_list_location = trc_list
        # self.dbc_location = dbc_loc
        self.V_name = vehicle_name
        self.trc_list = os.path.dirname(trc_files[0])
        self.dbc = dbc_new_location
        self.tyresize = Tyre_size_name
        self.DRRn = DRR
        self.bms_loc = bms_file_location
        self.bat_name = Battery_name
        self.bat_model = Battery_Model
        self.bat_volt = Battery_Voltage
        self.bat_cap = Battery_capacity
        self.g_ratio = gear_ratio 
        self.Variant = vehicle_variant
        self.flag_marvel = 0
        self.flag_nbms = 0
        # self.run()
        self._is_running = True
    def stop(self):
        self._is_running = False
        
    def run(self):
        # logging.info(f"📂 Processing folder: {os.path.basename(self.trc_list)}")
        print(f"📂 Processing folder: {os.path.basename(self.trc_list)}")
        print(f"befroe making final_summary.xlsx {self.trc_list}")
        self.summary_file = os.path.normpath(os.path.join(self.trc_list, "Final_summary.xlsx"))
        # --- STEP 0: Fetching ---
        time.sleep(1)
        directory = os.path.dirname(self.bms_loc)
        for filename in os.listdir(directory):
            if filename.lower().endswith("bmslog.csv") and filename != "bmslog.csv":
                os.rename(
                    os.path.join(trc_dir, filename),
                    os.path.join(trc_dir, "bmslog.csv")
                )
                break
        bms_path = os.path.normpath(os.path.join(directory,"bmslog.csv"))
        df_bms = pd.read_csv(bms_path)
        self.job_starting.emit(0)
        if not self._is_running: return
        result = self.process_bms_data(df_bms,self.summary_file,self.bat_volt,self.bat_cap)
        if not self._is_running: return
        # Check if user cancelled selection or it failed
        if not result or not result[0]:
            # self.job_failed.emit(0,"Cancelled process / no result in return")
            print("BMS processing error!!")
            self.job_failed.emit(0,"Unable to process BMS file")
            return # Stop processing
        time.sleep(3)
        # Unpack results for the next steps
        # result = (True, trc_files, dbc, dbc_signal_order, trc_dir)
        energy_consumed_wh, start_date_only= result
        self.job_completed.emit(0)
        time.sleep(2)
        self.job_starting.emit(1)
        print(f"just before pcan error{self.trc_list}")
        pcan_path = os.path.normpath(os.path.join(self.trc_list, "pcan.csv"))
        print(f"pcan_path detected {pcan_path}")
        if not os.path.exists(pcan_path):
            print("pcan.csv doesnt exist in the current folder")
            self.job_failed.emit(1,"Unable to find pcan.csv")
            return 
        time.sleep(2)
        df_pcan = pd.read_csv(pcan_path)
        pcan_result = self.process_pcan_data(df_pcan, self.summary_file, energy_consumed_wh, self.DRRn, self.g_ratio)
        torque_max, rpm_max, mode = pcan_result
        if not pcan_result or not pcan_result[0]:
            print("pcan.csv result doesnt exist in the current folder ")
            self.job_failed.emit(1,"Unable to process pcan file")
            return # Stop processing
        else:
            # self.data.emit(torque_max, rpm_max, mode)
            self.job_completed.emit(1)
        time.sleep(1)
        self.job_starting.emit(2)
        success = self.convert_xlsx_to_csv(self.summary_file)
        if success:
            self.job_completed.emit(2)
        else:
            return
        if not self._is_running: return
    def get_bms_error_description(code: int) -> str:
        """Map BMS error codes to descriptions."""
        descriptions = {
            0: "No error.",
            2: "Internal values out of bounds.",
            4: "Resource access failure (e.g., CMU, ignition, charger PID).",
            7: "Parameter out of bounds – likely BMS Creator config issue.",
            13: "Queue overrun in CAN or error queues.",
            15: "Internal SPI communication error with CMUs.",
            276: "Write error for RTC device.",
            304: "Invalid received CAN data frame.",
            306: "CAN RX timeout waiting for frame.",
            400: "Failed to read GPIO input states.",
            401: "Task execution exceeded allowed time.",
            402: "Task did not execute at expected intervals.",
            403: "Software task is dead (not running).",
            600: "General external ADC error.",
            601: "ADC initialization error.",
            610: "Failed to start shunt ADC measurement.",
            611: "Failed to read shunt ADC result.",
            620: "Failed to start HV+ ADC measurement.",
            621: "Failed to read HV+ ADC result.",
            630: "Failed to start Hall sensor ADC measurement.",
            631: "Failed to read Hall sensor ADC result.",
            901: "Internal ADC logic error.",
            902: "Internal FIFO memory sizing issue.",
            903: "ADC conversion did not complete in time.",
            1001: "Comparison failure between sent and received CMU data.",
            1006: "Balancing resistor write operation failed.",
            1008: "LTC reference voltage VREF2 out of range.",
            1100: "Temperature channel 01: No value.",
            1101: "Temperature channel 02: No value.",
            1102: "Temperature channel 03: No value.",
            1103: "Temperature channel 04: No value.",
            1104: "Temperature channel 05: No value.",
            1105: "Temperature channel 06: No value.",
            1106: "Temperature channel 07: No value.",
            1107: "Temperature channel 08: No value.",
            1108: "Temperature channel 09: No value.",
            1109: "Temperature channel 10: No value.",
            1110: "Temperature channel 11: No value.",
            1116: "Temperature channel 01: Shorted (resistance too low).",
            1117: "Temperature channel 02: Shorted (resistance too low).",
            1118: "Temperature channel 03: Shorted (resistance too low).",
            1119: "Temperature channel 04: Shorted (resistance too low).",
            1120: "Temperature channel 05: Shorted (resistance too low).",
            1121: "Temperature channel 06: Shorted (resistance too low).",
            1122: "Temperature channel 07: Shorted (resistance too low).",
            1123: "Temperature channel 08: Shorted (resistance too low).",
            1124: "Temperature channel 09: Shorted (resistance too low).",
            1125: "Temperature channel 10: Shorted (resistance too low).",
            1126: "Temperature channel 11: Shorted (resistance too low).",
            1132: "Temperature channel 01: Open circuit (no sensor or disconnected).",
            1133: "Temperature channel 02: Open circuit (no sensor or disconnected).",
            1134: "Temperature channel 03: Open circuit (no sensor or disconnected).",
            1135: "Temperature channel 04: Open circuit (no sensor or disconnected).",
            1136: "Temperature channel 05: Open circuit (no sensor or disconnected).",
            1137: "Temperature channel 06: Open circuit (no sensor or disconnected).",
            1138: "Temperature channel 07: Open circuit (no sensor or disconnected).",
            1139: "Temperature channel 08: Open circuit (no sensor or disconnected).",
            1140: "Temperature channel 09: Open circuit (no sensor or disconnected).",
            1141: "Temperature channel 10: Open circuit (no sensor or disconnected).",
            1142: "Temperature channel 11: Open circuit (no sensor or disconnected).",
            1148: "Temperature channel 01: Below configured minimum.",
            1149: "Temperature channel 02: Below configured minimum.",
            1150: "Temperature channel 03: Below configured minimum.",
            1151: "Temperature channel 04: Below configured minimum.",
            1152: "Temperature channel 05: Below configured minimum.",
            1153: "Temperature channel 06: Below configured minimum.",
            1154: "Temperature channel 07: Below configured minimum.",
            1155: "Temperature channel 08: Below configured minimum.",
            1156: "Temperature channel 09: Below configured minimum.",
            1157: "Temperature channel 10: Below configured minimum.",
            1158: "Temperature channel 11: Below configured minimum.",
            1164: "Temperature channel 01: Above configured maximum.",
            1165: "Temperature channel 02: Above configured maximum.",
            1166: "Temperature channel 03: Above configured maximum.",
            1167: "Temperature channel 04: Above configured maximum.",
            1168: "Temperature channel 05: Above configured maximum.",
            1169: "Temperature channel 06: Above configured maximum.",
            1170: "Temperature channel 07: Above configured maximum.",
            1171: "Temperature channel 08: Above configured maximum.",
            1172: "Temperature channel 09: Above configured maximum.",
            1173: "Temperature channel 10: Above configured maximum.",
            1174: "Temperature channel 11: Above configured maximum.",
            2000: "One or more cell voltages below minimum configured limit.",
            2001: "One or more cell voltages above maximum configured limit.",
            2004: "Temperature below configured cell temperature minimum.",
            2005: "Temperature above configured cell temperature maximum.",
            2008: "Pack charge current exceeds configured input current limit (DCLI).",
            2009: "Pack discharge current exceeds configured output current limit (DCLO).",
            2010: "I²t current limit exceeded — advanced current protection triggered.",
            2011: "Invalid cell voltage reading — extreme/unrealistic value.",
            2012: "Invalid cell temperature reading — extreme/unrealistic value.",
            2013: "Cell temperature shorted — reading above 120°C.",
            2014: "Cell temperature open — reading below -40°C.",
            2015: "PCB temperature reading invalid — extreme/unrealistic value.",
            2016: "PCB temperature sensor shorted — temperature too high.",
            2017: "PCB temperature sensor open — temperature too low.",
            2018: "Current sensor configuration out of allowed range.",
            2019: "BMS cannot communicate with one or more CMUs.",
            2020: "Mismatch between actual and expected number of CMUs.",
            2021: "Missing feedback for load negative contactor.",
            2022: "Missing feedback for load positive contactor.",
            2023: "Missing feedback for pre-charge contactor.",
            2024: "Missing feedback for charge negative contactor.",
            2025: "Unexpected feedback for load negative contactor — likely welded.",
            2026: "Unexpected feedback for load positive contactor — likely welded.",
            2027: "Unexpected feedback for pre-charge contactor — likely welded.",
            2028: "Unexpected feedback for charge negative contactor — likely welded.",
            2031: "Contactor retry limit exceeded.",
            2032: "LT device on CMU or c-BMS reports internal reference voltage error.",
            2033: "Incorrect LT temp sensor configuration on c-BMS.",
            2036: "SOC calculation failed — likely due to incorrect current input.",
            2038: "Configured GPIO number is out of range.",
            2039: "Error code not used.",
            2040: "Error code not used.",
            2041: "PSU not in diagnostic mode at startup — may require board replacement.",
            2042: "Charge current outside expected deadband range.",
            2043: "Internal circuit fault in isolation test.",
            2044: "Low isolation resistance in load mode.",
            2045: "Low isolation resistance in charge mode.",
            2046: "Low isolation resistance in ready mode.",
            2047: "Too many CAN broadcast errors (overflow).",
            2048: "Open wire in cell voltage monitoring; bitwise check IDs 1119–1150.",
            2049: "Corrupted XML configuration file — watermark alignment error.",
            2055: "Precharge Timeout.",
            2056: "Internal Resistance value error.",
            2060: "Unknown voltage detected — likely open wire (similar to error 2048)."
        }
        return descriptions.get(code, "Description not available.")
    def marvel_error_detect(code: int) -> str:
        # 0th byte (×1000 group)
        byte0_errors = {
            100: "Over Current Charge",
            200: "High imbalance",
            400: "PCB Over Temperature",
            800: "External Temperature error",
            1000: "efuse discharge",
            2000: "efuse charge",
            4000: "Under voltage",
            8000: "Over voltage",
        }

        # 1st byte (×1 group)
        byte1_errors = {
            1: "Over Current Discharge",
            2: "FLASH_WRITE_FAIL",
            4: "EEPROM write fail",
            8: "EEPROM read fail",
            10: "Permanent fail",
            20: "Precharge retry fail",
            40: "EEPROM Corrupted (If the 10 Power Cycles get the EEPROM Write or read Fail then Consider the EEPROM Corrupted)",
            80: "EEPROM_COMM_FAIL",
        }

        # Build full dictionary (single + combined cases)
        descriptions = {}
        descriptions.update(byte0_errors)
        descriptions.update(byte1_errors)

        # Add combined 0th + 1st byte error cases
        for b0_val, b0_desc in byte0_errors.items():
            for b1_val, b1_desc in byte1_errors.items():
                combined_val = b0_val + b1_val
                combined_desc = f"{b0_desc} and {b1_desc}."
                descriptions[combined_val] = combined_desc

        # Return description
        return descriptions.get(code, "Description not available.")
    def marvel_cr_error_detect(code: int) -> str:
        descriptions = {
            40: "Thermal runaway.",
            80: "Short circuit error.",
            20: "Start sanity Fail Error."
        }
        return descriptions.get(code, "Description not available.")
    def marvel_warning_detect(code: int) -> str:
        descriptions = {
            1: "EEPROM Shadow Write Fail.",
            2: "EEPROM Meta Write Fail.",
            4: "EEPROM Shadow Read Fail.",
            8: "EEPROM Meta Read Fail.",
            10: "CCM Fail.",
            20: "CMU Fail.",
            40: "Hard Fault Present.",
            80: "Config update."
        }
        return descriptions.get(code, "Description not available.")


   




    def parse_custom_date(self,date_str, return_format=False):
        if isinstance(date_str, datetime):
            return (date_str, "datetime object") if return_format else date_str
        if not isinstance(date_str, str):
            raise ValueError(f"Invalid input: {date_str}")

        date_str = " ".join(date_str.strip().split())  # Normalize whitespace

        formats = [
            # --- ISO formats ---
            ("%Y-%m-%d %H:%M:%S", "ISO with seconds"),
            ("%Y-%m-%d %H:%M", "ISO without seconds"),
            ("%Y-%m-%d %H:%M:%S.%f", "ISO with ms"),

            # --- European dash ---
            ("%d-%m-%Y %H:%M:%S", "European with seconds"),
            ("%d-%m-%Y %H:%M", "European without seconds"),
            ("%d-%m-%Y %H:%M:%S.%f", "European with ms"),

            # --- US dash ---
            ("%m-%d-%Y %H:%M:%S", "US with seconds"),
            ("%m-%d-%Y %H:%M", "US without seconds"),
            ("%m-%d-%Y %H:%M:%S.%f", "US with ms"),

            # --- European slash ---
            ("%d/%m/%Y %H:%M:%S", "European slash with seconds"),
            ("%d/%m/%Y %H:%M", "European slash without seconds"),
            ("%d/%m/%Y %H:%M:%S.%f", "European slash with ms"),

            # --- US slash ---
            ("%m/%d/%Y %H:%M:%S", "US slash with seconds"),
            ("%m/%d/%Y %H:%M", "US slash without seconds"),
            ("%m/%d/%Y %H:%M:%S.%f", "US slash with ms"),

            # --- Date only ---
            ("%Y-%m-%d", "ISO date only"),
            ("%d-%m-%Y", "European date only"),
            ("%m-%d-%Y", "US date only"),
            ("%d/%m/%Y", "European slash date only"),
            ("%m/%d/%Y", "US slash date only"),

            # --- Time only ---
            ("%H:%M:%S.%f", "Hours:Minutes:Seconds with ms"),
            ("%M:%S.%f", "Minutes:Seconds with ms"),
            ("%H:%M:%S", "Hours:Minutes:Seconds"),
            ("%H:%M", "Hours:Minutes"),
            # Add these specifically for the error you encountered:
            ("%d/%m/%y %H:%M:%S", "European slash 2-digit year"),
            ("%d/%m/%y %H:%M", "European slash 2-digit year no seconds"),
            
            # Just in case it appears as date only
            ("%d/%m/%y", "European slash date only 2-digit")
        ]

        for fmt, label in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return (dt, label) if return_format else dt
            except ValueError:
                continue

        raise ValueError(f"Invalid date format: {date_str}")
    def calculate_imbalance(self,row, cell_cols):
        # print("reached in imbalance function")
        try:
            # # print("battery_pack",battery_pack)
            # if battery_pack == 1:#nbms
            #     if hasattr(row, "index"):  # pandas Series
            #         # pattern = r'^CMU: \d+ Cell: \d+'
            #         pattern = r'CMU:\s*\d+\s*Cell:\s*\d+'
            #         # Filter the index using regex match
            #         cell_cols = [col for col in row.index if re.match(pattern, str(col))]
            #         # cell_cols = [col for col in row.index if col.startswith("CellVoltage_")]
            #         all_vals = [
            #             float(row[col])
            #             for col in cell_cols
            #             if pd.notna(row[col]) and float(row[col]) > 2000
            #         ]
            #     if not all_vals:
            #         return None
            
            # elif battery_pack == 0:#marvel
            #     # Extract blocks for MAX
            #     #Cell1
            #     if hasattr(row, "index"):  # pandas Series
            #         cell_cols = [col for col in row.index if col.startswith("CellVoltage_","CMU")]


            #         all_vals = [
            #             float(row[col])
            #             for col in cell_cols
            #             if pd.notna(row[col]) and float(row[col]) > 2000
            #         ]
            #     if not all_vals:
            #         return None
            all_vals = [
                float(row[col])
                for col in cell_cols
                if col in row and pd.notna(row[col]) and float(row[col]) > 2000
            ]

            if not all_vals:
                print("NO values found")
                return None
            max_v = max(all_vals)
            min_v = min(all_vals)
            # print("max_battery_V",max_v,"\n","min_battery_V",min_v)
            return max_v - min_v
        except (ValueError, TypeError):
            print("reacher to the except section!!")
            return None
    # def calculate_imbalance(self, row, cell_cols):
    #     # This will only print for the very first row to avoid flooding your console
    #     debug_mode = True 
        
    #     try:
    #         all_vals = []
    #         for col in cell_cols:
    #             if col not in row:
    #                 if debug_mode: print(f"DEBUG: Column '{col}' not found in row index!")
    #                 continue
                    
    #             val = row[col]
    #             if pd.isna(val):
    #                 continue # Skip empty cells
                    
    #             try:
    #                 # Convert to float and check the > 2000 threshold
    #                 numeric_val = float(val)
    #                 if numeric_val > 2000:
    #                     all_vals.append(numeric_val)
    #                 else:
    #                     if debug_mode: print(f"DEBUG: Value {numeric_val} is not > 2000")
    #             except ValueError:
    #                 if debug_mode: print(f"DEBUG: Could not convert '{val}' to float")

    #         if not all_vals:
    #             # Only print this if we actually expected values
    #             # print("NO values found in this row")
    #             return None
                
    #         return max(all_vals) - min(all_vals)

    #     except Exception as e:
    #         print(f"Error in imbalance calc: {e}")
    #         return None


    def process_bms_data(self,df_bms, summary, pack_capacity_coeff ,peak_c_rate):
        #---------------------------------------------------------------do change here if any battery changes or vehicle added-----------------------------------------
        
        summary_file = summary
        self.flag_marvel = 0
        self.flag_nbms = 0
        # Load merged data
        data = df_bms.values.tolist()
        #headers = df_bms.columns.tolist()
        sec_row = data[0]
        total = len(sec_row)
        numeric_count = 0
        for val in sec_row:
            if not self._is_running: return
            try:
                if pd.notna(val):
                    float(val)
                    numeric_count += 1
            except:
                pass
        if numeric_count/total < 0.5:
            battery_pack = 0
            print("MARVEL BMS DETECTED!!!!")
            self.flag_marvel = 1
        else:
            battery_pack = 1
            print("NBMS DETECTED!!")
            self.flag_nbms = 1
        if not data:
            self.job_failed.emit(0,"BMS sheet empty!!")
            raise ValueError("bms sheet is empty!")
        if not self._is_running: return
        # Initialize variables
        total_regen_power = total_drive_power = 0
        regen_count = drive_count = 0
        max_average_power = sum_current = count_current = 0
        currents = []
        # Cell imbalance calculations
        total_imbalance = count_imbalance = peak_imbalance = 0
        start_imbalance = end_imbalance = 0
        start_recorded = False
        PACK_C = []
        error_points = []
        PACK_V = []
        PACK_TEMP = []
        SOC_LIST = []
        flag_temp = 0
        if self.flag_marvel == 0 and self.flag_nbms == 0:
            self.job_failed.emit(0,"Unable to identify BMS file type")
        
        # First loop: Power and current calculations
        temp_cols = []
        alarm_cols = []
        cell_cols = []
        if self.flag_nbms == 1:
            # pattern = r'CMU:\s*\d+\s*Cell:\s*\d+'
            pattern = r'CMU\s*:\s*\d+\s*Cell\s*:\s*\d+'
            cell_cols = [
                col for col in df_bms.columns 
                if re.search(pattern, str(col).strip(), re.IGNORECASE)
            ]
            # cell_cols = [col for col in df_bms.columns if re.match(pattern, str(col))]
        else: # Marvel
            cell_cols = [col for col in df_bms.columns if col.startswith(("CellVoltage_", "CMU"))]
        print(f"Found {len(cell_cols)} cell columns.")
        if self.flag_marvel ==1:
            df_bms = df_bms.iloc[2:].reset_index(drop=True)
            for i in range(len(df_bms) - 1):
                curr = df_bms.iloc[i]
                nxt = df_bms.iloc[i + 1]
                if not self._is_running: return
                voltage = float(curr['Pack_Voltage'])
                next_voltage = float(nxt['Pack_Voltage'])
                current = float(curr['Pack_Current'])
                next_current = float(nxt['Pack_Current'])
                SOC = float(curr['SoC'])
                pack_capacity = float(curr['Pack_Capacity'])
                if not (pd.isna(voltage) or pd.isna(current) or pd.isna(next_voltage) or pd.isna(next_current)):
                    power = voltage * current
                    avg_power = (power + next_voltage * next_current) / 2 if i > 1 else 0
                    currents.append(current)
                    PACK_V.append(voltage)
                else:
                    continue
                if not (pd.isna(pack_capacity)):
                    PACK_C.append(pack_capacity)
                else:
                    continue
                
                
                SOC_LIST.append(SOC)
                if hasattr(curr, "index"):  # pandas Series
                    temp_column_m = [col for col in curr.index if col.startswith("ExtTherm_")]
                all_vals = [
                        float(curr[col])
                        for col in temp_column_m
                        if pd.notna(curr[col]) and float(curr[col]) > 0
                    ]
                if flag_temp == 0:
                    if all_vals:
                        battery_start_temp = max(all_vals)
                        battery_start_temp_min = min(all_vals)
                    else:
                        battery_start_temp = battery_start_temp_min = None
                    flag_temp = 1
                PACK_TEMP.extend(all_vals)
                if current >= 0.1 and avg_power != 0:
                    total_regen_power += avg_power
                    regen_count += 1
                    max_average_power = max(max_average_power, avg_power)

                if current <= -2 and avg_power != 0:
                    total_drive_power += avg_power
                    drive_count += 1

                if current <= -2:
                    sum_current += current
                    count_current += 1
                imbalance = self.calculate_imbalance(curr, cell_cols) #edited
                if imbalance is None:
                    continue
                
                if not start_recorded:
                    start_imbalance = imbalance
                    start_recorded = True
                if 97<= SOC <= 100:
                    if imbalance > 200:
                        soc_value = int(float(SOC))
                        error_points.append(soc_value)

                end_imbalance = imbalance
                total_imbalance += imbalance
                count_imbalance += 1
                peak_imbalance = max(peak_imbalance, imbalance)
        elif self.flag_nbms == 1:
            df_bms.columns = df_bms.columns.str.replace(r'\s+', '', regex=True)
            cell_cols = [col.replace(" ", "") for col in cell_cols]
            df_bms = df_bms.iloc[1:].reset_index(drop=True)
            temp_cols = [col for col in df_bms.columns if col.endswith("CellTemperature[C]")]
            alarm_cols = [col for col in df_bms.columns if col.startswith("Alarm Entry")]
            records = df_bms.to_dict('records')
            for i in range(len(records) - 1):
                # curr = df_bms.iloc[i]
                # nxt = df_bms.iloc[i + 1]
                curr = records[i]
                nxt = records[i + 1]
                if not self._is_running: return
                voltage = float(curr['PackVoltage[V]'])
                next_voltage = float(nxt['PackVoltage[V]'])
                current = float(curr['PackCurrent[A]'])
                next_current = float(nxt['PackCurrent[A]'])
                SOC = float(curr['SoC[%]'])
                pack_capacity = float(curr['RemainingBatteryPackCapacity[As]'])
                if not (pd.isna(voltage) or pd.isna(current) or pd.isna(next_voltage) or pd.isna(next_current)):
                    power = voltage * current
                    avg_power = (power + next_voltage * next_current) / 2 if i > 1 else 0
                    currents.append(current)
                    PACK_V.append(voltage)
                else:
                    continue
                if not (pd.isna(pack_capacity)):
                    PACK_C.append(pack_capacity)
                else:
                    continue
                
                
                SOC_LIST.append(SOC)
                # if hasattr(curr, "index"):  # pandas Series
                #     temp_column = [col for col in curr.index if col.endswith("CellTemperature[C]")]
                all_vals = [
                        float(curr[col])
                        for col in temp_cols
                        if pd.notna(curr[col]) and float(curr[col]) > 0
                    ]
                if flag_temp == 0:
                    if all_vals:
                        battery_start_temp = max(all_vals)
                        battery_start_temp_min = min(all_vals)
                    else:
                        battery_start_temp = battery_start_temp_min = None
                    flag_temp = 1
                PACK_TEMP.extend(all_vals)
                if current >= 0.1 and avg_power != 0:
                    total_regen_power += avg_power
                    regen_count += 1
                    max_average_power = max(max_average_power, avg_power)

                if current <= -2 and avg_power != 0:
                    total_drive_power += avg_power
                    drive_count += 1

                if current <= -2:
                    sum_current += current
                    count_current += 1
                imbalance = self.calculate_imbalance(curr, cell_cols) #edited
            
                if imbalance is None:
                    print("CAnt find any imbalance")
                    continue
                
                if not start_recorded:
                    start_imbalance = imbalance
                    start_recorded = True
                if 97<= SOC <= 100:
                    if imbalance > 200:
                        soc_value = int(float(SOC))
                        error_points.append(soc_value)

                end_imbalance = imbalance
                total_imbalance += imbalance
                count_imbalance += 1
                peak_imbalance = max(peak_imbalance, imbalance)
        else:
            print("Neither one detected")

        # Average current
        avg_battery_current = abs(sum_current / count_current) if count_current else 0

        # Peak current
        
        
        batterypeak_current = abs(min(currents)) if currents else 0
        peak_crate = batterypeak_current / peak_c_rate
        # print(f"regen_count: {regen_count}")
        # print(f"total_regen_power: {total_regen_power}")
        regen_energy_wh = total_regen_power / 3600 if regen_count else 0
        drive_energy_wh = abs(total_drive_power) / 3600 if drive_count else 0
        regen_percent_recovery = (regen_energy_wh / drive_energy_wh) * 100 if drive_energy_wh else 0
        avg_average_power = total_regen_power / regen_count if regen_count else 0
        regen_percent_recovery = round(regen_percent_recovery, 2)
        
    
        avg_imbalance = total_imbalance / count_imbalance if count_imbalance else 0
        if not self._is_running: return
        # Battery capacity and voltage
        try:
            
            battery_v_start = PACK_V[0]
            battery_v_end = PACK_V[-1]
        
            if self.flag_marvel == 1:
                initial_capacity_asec = PACK_C[0]*3600 
                final_capacity_asec = PACK_C[-1]*3600
            else:
                initial_capacity_asec = PACK_C[0]
                final_capacity_asec = PACK_C[-1]

        except (ValueError, IndexError):
            raise ValueError("Battery data missing or corrupted")

        initial_capacity_ah = initial_capacity_asec / 3600
        final_capacity_ah = final_capacity_asec / 3600
        capacity_used_ah = initial_capacity_ah - final_capacity_ah
        pack_capacity_used_wh = capacity_used_ah * pack_capacity_coeff
        energy_consumed_wh = (battery_v_start * initial_capacity_ah) - (battery_v_end * final_capacity_ah)

        # Temperature
        # if vehicle == 12:
        #     get_data = battery_cell_temp_mbms(data[1])#3rd row
        #     battery_start_temp = get_data[0]
        #     battery_start_temp_min = get_data[1]
        # else:
        #     battery_start_temp = float(data[0][9])
        #     battery_start_temp_min = float(data[0][10])
        # temp_col_j = []
        # for row in data[1:]:
        #     try:
        #         temp_col_j.append(float(row[9]))
        #     except (ValueError, IndexError, TypeError):
        #         continue
        # peak_cell_temp = max(temp_col_j) if temp_col_j else 0
        min_cell_temp = 0
        average_cell_temp = 0
        avg = []

        
        peak_cell_temp = max(PACK_TEMP) if PACK_TEMP else 0
        min_cell_temp = min(PACK_TEMP) if PACK_TEMP else 0
        average_cell_temp = sum(PACK_TEMP)/len(PACK_TEMP) if PACK_TEMP else 0

        
        time = []
        for i in range(len(data)):
            if pd.notna(data[i][0]):
                time.append(data[i][0])
        # Time and duration
        if self.flag_marvel == 1:
            start_str = time[3]
        else:
            start_str = time[1]
        
        end_str = time[-1]
        start_time = self.parse_custom_date(start_str)
        end_time = self.parse_custom_date(end_str)
        duration_minutes = (end_time - start_time).total_seconds() / 60

        start_time_only = start_time.strftime("%H:%M:%S")
        end_time_only = end_time.strftime("%H:%M:%S")
        start_date_only = start_time.strftime("%d/%m/%Y")
        #Indentifying errors and calling them out
        error_dict = {}   # {errorCode: count}
        status_dict = {}  # {errorCode: {status: count}}
        soc_dict = {}
        soc_list = []
        original_list = []
        soc_value = None
    #25-04-26------------------------------------------------<<<<<
        # iterate rows
        if self.flag_nbms ==1:
            original_list = [x for x in SOC_LIST if str(x) != 'nan' and not math.isnan(x)]
            df_bms = df_bms.iloc[1:].reset_index(drop=True)
            for i in range(len(df_bms) - 1):
                curr = df_bms.iloc[i]
                status_text = str(curr["Status"]).strip().upper()  # column C
                if status_text != "ERROR":   # ✅ only process rows with ERROR in column C
                    continue
                if not self._is_running: return
                try:
                    soc_value = int(float(curr["SoC[%]"]))  # column E = index 4
                except:
                    pass
                # 🚫 Skip if SOC is exactly 0
                if soc_value is not None and soc_value == 0.0:
                    continue
                # if hasattr(curr, "index"):  # pandas Series
                #     temp_column = [col for col in curr.index if col.startswith("Alarm Entry")]#startswith
                all_vals = [
                        float(curr[col])
                        for col in alarm_cols
                        if pd.notna(curr[col]) and float(curr[col]) > 0
                    ]
                for i in range(0,len(all_vals)-1):
                    full_text = str(all_vals[i]).strip()

                    if not full_text or full_text.lower() == "nan":
                        continue

                    error_code = None
                    if "-" in full_text:
                        prefix = full_text.split("-")[0].strip()
                        if prefix.isdigit():
                            error_code = int(prefix)
                    elif full_text.isdigit():
                        error_code = int(full_text)

                    if error_code is None:
                        continue
                
                    if error_code == 2005:#-------------------------temperatue error condition-----------------------------------
                        j_value = float(curr["Max.CellTemperature[C]"])  # Jth column = index 9 (0-based)
                        if j_value <= 55:             # only count if > 55
                            continue
                    #Soc = float(row.iloc)

                    # count instances
                    error_dict[error_code] = error_dict.get(error_code, 0) + 1

                    # track status
                    if error_code not in status_dict:
                        status_dict[error_code] = {}
                    status_dict[error_code][status_text] = status_dict[error_code].get(status_text, 0) + 1

                    # track SOC values
                    if error_code not in soc_dict:
                        soc_dict[error_code] = []
                    if soc_value is not None:
                        soc_dict[error_code].append(soc_value)
            # --- Build Summary Table ---
            error_summary = []
            for code, count in error_dict.items():
                statuses = status_dict.get(code, {})
                status_summary = ", ".join([f"{s} ({c})" for s, c in statuses.items()])
                if not self._is_running: return
                # SOC values (deduplicated while preserving order)
                socs = soc_dict.get(code, [])
                seen = set()
                socs_unique = [s for s in socs if not (s in seen or seen.add(s))]
                # 🚫 Skip this error entirely if all SOCs are 0 or empty
                if not socs_unique or all(s == 0.0 for s in socs_unique):
                    continue 
                
                soc_str = f"Errors at SOC : {', '.join(map(str, socs_unique))}"

                error_summary.append({
                    "Error Code": code,
                    "Instances": count,
                    "Description": get_bms_error_description(code),
                    "Status During Error": status_summary,
                    "SOC Values": soc_str
                })
        else:
            original_list.extend(SOC_LIST)#marvel
        soc_list = pd.Series(original_list).dropna().tolist()
        soc_last = float(soc_list[-1])
        soc_start = float(soc_list[0])
        threshold = 5  # you can adjust this (e.g. detect jumps >5%)

        # Detect sudden jumps
        recovery_threshold = 3  # how close it should come back to previous value

        sudden_jumps = []
        # Detect sudden jumps
        for i in range(1, len(soc_list)):
            drop = float(soc_list[i-1]) - float(soc_list[i])
            if not self._is_running: return
            # detect drop
            if drop > threshold:
                # check if it recovers within next few points (say next 3 samples)
                recovered = False
                for j in range(i+1, min(i+4, len(soc_list))):
                    if abs(float(soc_list[j]) - float(soc_list[i-1])) <= recovery_threshold:
                        recovered = True
                        break

                if not recovered:
                    sudden_jumps.append((soc_list[i-1], soc_list[i]))


        # put into summary dict (so it can be written elsewhere, e.g. Excel or Google Sheets)
        # summary["bms_error_summary"] = {
        #     "vehicle": vehicle,
        #     "errors": error_summary
        # }
        # --- Prepare error descriptions for Excel BR column ---
        error_details = []
        if self.flag_nbms == 1:
            if error_summary:
                error_details.extend([
                    f"{err['Error Code']} - {err['Description']} (x{err['Instances']}) | {err['SOC Values']}"
                    for err in error_summary
                ])
        if error_points:  # only if errors found
            imbalance_str = f"Imbalance >200mV between 97–100% SOC at {sorted(set(error_points))}"
            error_details.append(imbalance_str)
        error_details_str = "; ".join(error_details) if error_details else ""
        
        
        # If the file exists, load it; otherwise, create a new workbook
        if os.path.exists(summary_file):
            wb = openpyxl.load_workbook(summary_file)
            ws = wb.active
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
        # Find the next empty row
        next_row = ws.max_row + 1 if ws.max_row > 1 or ws.cell(1, 1).value else 2
        row_data = {
            "Start Date": ("A", start_date_only),
            "Start Time": ("B", start_time_only),
            "End Time": ("P", end_time_only),
            "Duration (min)": ("Q", duration_minutes),
            "Battery V Start": ("V", battery_v_start),
            "Battery V End": ("W", battery_v_end),
            "Battery Start Temp": ("X", battery_start_temp),
            "Battery Start Temp Min": ("Y", battery_start_temp_min),
            "Peak Cell Temp": ("Z", peak_cell_temp),
            "Avg Imbalance": ("AA", avg_imbalance),
            "Start Imbalance": ("AB", start_imbalance),
            "End Imbalance": ("AC", end_imbalance),
            "Peak Imbalance": ("AD", peak_imbalance),
            "Initial Capacity (AsEc)": ("AE", initial_capacity_asec),
            "Final Capacity (AsEc)": ("AF", final_capacity_asec),
            "Initial Capacity (Ah)": ("AG", initial_capacity_ah),
            "Final Capacity (Ah)": ("AH", final_capacity_ah),
            "Capacity Used (Ah)": ("AI", capacity_used_ah),
            "Energy Consumed (Wh)": ("AJ", energy_consumed_wh),
            "Avg Battery Current": ("AL", avg_battery_current),
            "Battery Peak Current": ("AM", batterypeak_current),
            "Peak C-Rate": ("AN", peak_crate),
            "Regen Energy (Wh)": ("AO", regen_energy_wh),
            "Peak Regen Power Recovered (W)": ("AP", max_average_power),
            "Drive Energy (Wh)": ("AQ", drive_energy_wh),
            "Regen Percent Recovery": ("AR", f"{regen_percent_recovery}%"),
            "Pack Capacity Used (Wh)": ("AV", pack_capacity_used_wh),
            "BMS Errors": ("BR", error_details_str),
            "min cell temp": ("BW",min_cell_temp),
            "average cell temp": ("BX",average_cell_temp),
        }

        for header, (col, _) in row_data.items():
            if ws[f"{col}1"].value is None:
                ws[f"{col}1"] = header
        # Write data to the correct columns
        for _, (col, value) in row_data.items():
            ws[f"{col}{next_row}"] = value
        if round(soc_last) != 0:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            soc_nc = f"SOC incomplete in BMS only till {soc_last}%"
            if existing_value:
                ws.cell(row=row, column=col, value=f"{existing_value} + {soc_nc}")
            else:
                ws.cell(row=row, column=col, value = soc_nc)
        if soc_start <= 98:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            soc_nc = f"SOC starts from {soc_start}% in BMS"
            if existing_value:
                ws.cell(row=row, column=col, value=f"{existing_value} + {soc_nc}")
            else:
                ws.cell(row=row, column=col, value = soc_nc)
        if sudden_jumps:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            #print(f"{len(sudden_jumps)} sudden jumps detected:")
            for start_val, end_val in sudden_jumps:
                soc_jump = f"SOC data missing from {start_val}% to {end_val}% in BMS"
                if existing_value:
                    ws.cell(row=row, column=col, value=f"{existing_value} + {soc_jump}")
                else:
                    ws.cell(row=row, column=col, value = soc_jump)
        # Save workbook
        wb.save(summary_file)
        print("✅ Final_summary.xlsx updated successfully.")
        return energy_consumed_wh, start_date_only

    def torque_and_rpm(self,vehicle_var,vehicle_name,MODE):
        dict_vehicle = {
            "V1": (420,("ECO",65,5032),("THUNDER",130,6709)), 
            "V2":(120,("ECO",100,5087),("THUNDER",125,7122)), 
            "V3":(420,("ECO",100,4578),("THUNDER",145,7122),("RHINO",145,3561)),
            "1250":(420,("ECO",100,5318),("THUNDER",125,7446),("RHINO",145,3723)), 
            "1750":(270,("ECO",120,6198),("THUNDER",180,8677),("RHINO",210,4339)), 
            # "LR200":(420,("ECO",65,5032),("THUNDER",130,6709),("RHINO",130,6709))
        }
        torque_max = 140
        rpm_max = 6000
        vehicle_ARMS = 420 
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
        print(f"inside torque and rpm function: {vehicle_ARMS},{torque_max},{rpm_max}")
        return vehicle_ARMS,torque_max,rpm_max
                    
    def process_pcan_data(self,df_pcan, summary, ECWh, DRRn, g_ratio):
        file_summary = summary
        energy_consumed_wh = ECWh
        # Load merged data
        data = df_pcan.values.tolist()
    #---------------------------------------------------------------edit here for vehicle changes----------------------------------------------------
        if not data:
            self.job_failed.emit(1,"Empty pcan file!!")
            raise ValueError("pcan sheet is empty!")
        
        conversion_factor = float((g_ratio*1000000)/(2*math.pi*DRRn*60))  
        gear_ratio = g_ratio
        drr = DRRn*0.001
    
        inputPowerMax = 0.0
        outputPowerMax = 0.0
        speedSum = 0.0
        speedCount = 0
        maxSpeed = 0.0

        controllerStartTemp = None
        controllerPeakTemp = -math.inf
        controllerPeakCurrent = -math.inf

        motorInitialTemp = None
        motorPeakTemp = -math.inf

        peakTorque = -math.inf
        peakRegenTorque = math.inf

        outputPowerTotal = 0.0
        outputPowerCount = 0
        inputPowerTotal = 0.0
        inputPowerCount = 0
        soc_exist = []
        error_ranges = []#stores all the error
        in_error = False#this is flag
        last_valid_soc = None
        start_soc = None
        marvel_error = []
        marvel_critical_error = []
        marvel_warning = []    
        mar_w = 0
        odometerlist = []
        date = []
        rhino = []#this is to count the actual case for rhino cuz their are cases where gear mode is H and yet it is error
        # ECO + Neutral %
        # (Your Apps Script loop over colGearMode looked buggy; here we compute correctly)
        rows = df_pcan
        for i, row in rows.iterrows():
            gearMode         = row["controller_vehicle_status"]
            torque           = row["TORQUE"]
            if self.Variant == "1750":
                if gearMode not in ["R", "N", "Z"] and not (gearMode == "H" and torque not in range(-130,220)):
                    if gearMode == "H":
                            rhino.append(gearMode)
            else:
                if gearMode not in ["R", "N", "Z"] and not (gearMode == "H" and torque not in range(-130,150)):
                    if gearMode == "H":
                            rhino.append(gearMode)
        total_modes = rows["controller_vehicle_status"].notna().sum()
        Reverse_neutral = rows["controller_vehicle_status"].isin(["R", "N"]).sum()
        Eco = rows["controller_vehicle_status"].isin(["E"]).sum()
        Thunder = rows["controller_vehicle_status"].isin(["S"]).sum()
        Rhino = len(rhino)
        Total = Eco + Thunder + Rhino
    #we are comparing the percentage removing neutral and reverse
        eco_percentage = (Eco / Total * 100) if Total else 0
        rhino_percentage = (Rhino / Total * 100) if Total else 0
        Thunder_percentage = (Thunder / Total * 100) if Total else 0
        MODE = "NIL"
        if eco_percentage >= 95:
            MODE = "ECO"
        elif rhino_percentage >= 95:
            MODE = "RHINO"
        elif Thunder_percentage >= 95:
            MODE = "THUNDER"
        else:
            MODE = "NOT-DEFINED"
        mode = max(
            ("ECO", eco_percentage),
            ("RHINO", rhino_percentage),
            ("THUNDER", Thunder_percentage),
            key=lambda x: x[1]
        )[0]
        torque_max = 140 #default
        rpm_max = 6000 #default
        ARMS_max = 420
        print(f"vehicle info {self.Variant},{self.V_name},{mode}")
        ARMS_max,torque_max,rpm_max = self.torque_and_rpm(self.Variant,self.V_name,mode)
        
        real_speed = []
        actualodo = []
        # Add "Kmph" column to the dataframe (like you did to the sheet)
        #df_pcan["Kmph"] = df_pcan["speed"] / conversion_factor
        def clean(val, default=None):  # Change default to None
            return default if pd.isna(val) or val == "" else val
        # Iterate like in Apps Script: only process gear_mode === "E"
        for i, row in rows.iterrows():
            gearMode         = row["controller_vehicle_status"]
            # acVoltage        = row["AC_voltage"]
            # torque           = row["TORQUE"]
            # rpm              = row["RPM"]
            # dcCurrent        = row["PackCurrent"]
            # dcVoltage        = row["Voltage"]
            # controllerTemp   = row["controller_temperature"]
            # controllerCurrent= row["AC_effective_current"]
            # motorTemp        = row["motor_temperature"]
            # # real_speed        = row["real speed"]
            # SOC              = row["SOC"]
            # # if self.flag_marvel == 1:
            # #     mar_e            = row["Marvel error"]
            # #     mar_ce           = row["Marvel critical error"]
            # #     mar_w_raw        = row["Marvel warning"]
            # # else:
            # #     mar_e = 0
            # #     mar_ce = 0
            # #     mar_w_raw = 0
            # ODO              = row["ODO"]
            acVoltage         = clean(row["AC_voltage"])
            torque            = clean(row["TORQUE"])
            rpm               = clean(row["RPM"])
            dcCurrent         = clean(row["DC_current"])
            dcVoltage         = clean(row["Voltage"])
            controllerTemp    = clean(row["controller_temperature"])
            controllerCurrent = clean(row["AC_effective_current"])
            motorTemp         = clean(row["motor_temperature"])
            SOC               = clean(row["SOC"])
            ODO               = clean(row["ODO"])
            DATE             = row["Date"]
            TIME             = row["Time"]
            if acVoltage is None or dcVoltage is None or dcCurrent is None or torque is None or SOC is None or rpm is None or controllerTemp is None or controllerCurrent is None or motorTemp is None or ODO is None:
                continue
            # if mar_w_raw and isinstance(mar_w_raw, str):
            #     mar_w = int(mar_w_raw.strip("{}' "))
            if not self._is_running: return
            if gearMode not in ["R", "N", "Z"] and 0 < controllerCurrent<= ARMS_max and torque in range(-130,torque_max) and not (gearMode == "H" and torque not in range(-130,torque_max)):
                # input power
                inputPower = dcCurrent * dcVoltage
                if inputPower > inputPowerMax:
                    inputPowerMax = inputPower
                inputPowerTotal += inputPower
                inputPowerCount += 1
                #Date and time
                if pd.notna(DATE) and pd.notna(TIME):
                    
                    if DATE and DATE != "00/00/2000  00:00:00":
                        date.append(f"{DATE} {TIME}")
                # output power
                # (2*pi*rpm*torque)/60
                outputPower = (2 * math.pi * rpm * torque) / 60.0
                outputPowerTotal += outputPower
                outputPowerCount += 1
                if outputPower > outputPowerMax:
                    outputPowerMax = outputPower
                real_speed.append(np.round(((((rpm/gear_ratio)*2*np.pi) /60)*drr)*3.6, 2))
                # controller start temp
                if acVoltage != 0 and controllerStartTemp is None:
                    controllerStartTemp = controllerTemp
                if acVoltage != 0:
                    controllerPeakTemp = max(controllerPeakTemp, controllerTemp)
                controllerPeakCurrent = max(controllerPeakCurrent, controllerCurrent)

                if motorInitialTemp is None and acVoltage != 0:
                    motorInitialTemp = motorTemp
                if acVoltage !=0:
                    motorPeakTemp = max(motorPeakTemp, motorTemp)

                peakTorque = max(peakTorque, torque)
                peakRegenTorque = min(peakRegenTorque, torque)
                speed = real_speed[-1]
                if speed >= 5:
                    speedSum += speed
                    speedCount += 1
                    maxSpeed = max(maxSpeed, speed)
                
                # if mar_e != 0:
                #     marvel_error.append((mar_e,abs(SOC)))
                # if mar_ce != 0:
                #     marvel_critical_error.append((mar_ce,abs(SOC)))
                # if mar_w_raw != 0:
                #     marvel_warning.append((mar_w_raw,abs(SOC)))
                odometerlist.append(ODO)
                if len(odometerlist)==1:
                    actualodo.append(odometerlist[-1])
                if len(odometerlist)>1:
                    if odometerlist[-1]>=actualodo[-1]:
                        actualodo.append(odometerlist[-1])
                    
        
            if gearMode != "Z" and -130<=torque<torque_max:
                soc_exist.append(SOC)
                if in_error:
                    end_soc = SOC
                    error_ranges.append((start_soc, end_soc))
                    in_error = False
                last_valid_soc = SOC
            if (gearMode == "Z") or (gearMode == "H" and torque not in range(-130,torque_max)):
                if not in_error and last_valid_soc is not None:
                    start_soc = last_valid_soc
                    in_error = True

        odometer_first = min(actualodo)
        odometer_last = max(actualodo)
        if in_error:
            error_ranges.append((start_soc, 0))
        print("odometery first", odometer_first)
        print("odometery last", odometer_last)
        packCapacityStart = (odometer_first / 3600.0) * 96.0 # NOTE: the odometery is taken from soc not pcan
        packCapacityEnd   = (odometer_last  / 3600.0) * 96.0 # NOTE: the odometery is taken from soc not pcan
        packCapacityUsed  = packCapacityStart - packCapacityEnd
        odometerTripRange = odometer_last - odometer_first
        soc_start = soc_exist[0]
        soc_end = soc_exist[-1]
        start_str = date[0]
        end_str = date[-1]
        start_time = self.parse_custom_date(start_str)
        end_time = self.parse_custom_date(end_str)
        duration_minutes = (end_time - start_time).total_seconds() / 60
        start_time_only = start_time.strftime("%H:%M:%S")
        end_time_only = end_time.strftime("%H:%M:%S")
        start_date_only = start_time.strftime("%d/%m/%Y")

        threshold = 5  # you can adjust this (e.g. detect jumps >5%)
        recovery_threshold = 3  # how close it should come back to previous value

        sudden_jumps = []
        # Detect sudden jumps
        for i in range(1, len(soc_exist)):
            drop = float(soc_exist[i-1]) - float(soc_exist[i])

            # detect drop
            if drop > threshold:
                # check if it recovers within next few points (say next 3 samples)
                recovered = False
                for j in range(i+1, min(i+4, len(soc_exist))):
                    if abs(float(soc_exist[j]) - float(soc_exist[i-1])) <= recovery_threshold:
                        recovered = True
                        break

                if not recovered:
                    sudden_jumps.append((soc_exist[i-1], soc_exist[i]))
        def find_soc_ranges(soc_list):
            soc_list = sorted(set(soc_list), reverse=True)  # sort high → low and remove duplicates
            ranges = []
            if not soc_list:
                return ranges

            start = soc_list[0]
            prev = soc_list[0]

            for soc in soc_list[1:]:
                # If continuous (difference = 1) continue range
                if prev - soc == 1:
                    prev = soc
                else:
                    ranges.append((start, prev))
                    start = soc
                    prev = soc
            ranges.append((start, prev))
            return ranges
        # marvel_error_summary = []
        # marvel_cr_error_summary = []
        # marvel_warning_summary = []
        # if len(marvel_error) > 1:
        #     error_summary = defaultdict(list)
        #     for mar_e,soc in marvel_error:
        #         error_summary[mar_e].append(soc)
        #     for code, soc_list in error_summary.items():
        #         soc_list = sorted(set(soc_list), reverse=True)
        #         soc_ranges = find_soc_ranges(soc_list)
        #         marvel_error_summary.append((code, len(soc_list), soc_ranges))
        # #marvel_error_summary = [(code,len(set(soc_list)), list(set(soc_list))) for code,soc_list in error_summary.items()]
        # if len(marvel_critical_error)>1:
        #     cr_error_summary = defaultdict(list)
        #     for mar_ce,soc in marvel_critical_error:
        #         cr_error_summary[mar_ce].append(soc)
        #     for code, soc_list in cr_error_summary.items():
        #         soc_list = sorted(set(soc_list), reverse=True)
        #         soc_ranges = find_soc_ranges(soc_list)
        #         marvel_cr_error_summary.append((code, len(soc_list), soc_ranges))
        # #marvel_cr_error_summary = [(code,len(set(soc_list)), list(set(soc_list))) for code,soc_list in cr_error_summary.items()]
        # if len(marvel_warning)>1:
        #     warning_summary = defaultdict(list)
        #     for mar_we,soc in marvel_warning:
        #         warning_summary[mar_we].append(soc)
        #     for code, soc_list in warning_summary.items():
        #         soc_list = sorted(set(soc_list), reverse=True)
        #         soc_ranges = find_soc_ranges(soc_list)
        #         marvel_warning_summary.append((code, len(soc_list), soc_ranges))
        # #marvel_warning_summary = [(code,len(set(soc_list)), list(set(soc_list))) for code,soc_list in warning_summary.items()]

        print(f"INput power: {inputPowerTotal} \n Output power: {outputPowerTotal}")


        
        avgSpeed = (speedSum / speedCount) if speedCount else 0
        avgMotorRPM = avgSpeed * conversion_factor
        motorPeakRPM = maxSpeed * conversion_factor
        rateOfMotorTemp = (motorPeakTemp - motorInitialTemp) if (motorInitialTemp is not None and motorPeakTemp != -math.inf) else 0
        avgOutputPower = (outputPowerTotal / outputPowerCount) if outputPowerCount > 0 else 0
        avgInputPower  = (inputPowerTotal  / inputPowerCount ) if inputPowerCount  > 0 else 0
        motorEfficiency = ((avgOutputPower / avgInputPower) * 100) if avgInputPower != 0 else 0

        wh_per_km = (energy_consumed_wh / odometerTripRange) if odometerTripRange != 0 else 0
        if os.path.exists(file_summary):
            wb = openpyxl.load_workbook(file_summary)
            ws = wb.active
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
        #next_row = ws.max_row + 1 if ws.max_row > 1 or ws.cell(1, 1).value else 2
        

        row_data = {
            "Drive mode": ("D", MODE),
            "Peak Drive input power (W)": ("AS", inputPowerMax),
            "Peak Drive output Power (W)": ("AT", outputPowerMax),
            "Peak System Efficiency": ("AU", motorEfficiency), #this efficiency is calculated taking the avg input and avg output power
            "Controller Mode": ("AW", "Torque"),
            "Controller Start Temp": ("AX", controllerStartTemp),#celcius
            "Controller Peak Temp": ("AY", controllerPeakTemp),
            "Controller Peak I Amps(rms)": ("AZ", controllerPeakCurrent),#amph
            "Peak Torque (Nm)": ("BA", torque_max),
            "Motor Peak Torque(Nm)": ("BB", peakTorque),
            "Peak Regen Torque (Nm)": ("BC", abs(peakRegenTorque)),
            "Motor Initial Temp": ("BD", motorInitialTemp),
            "Motor Peak temp (Max operating Temp: 145'C)": ("BE", min(motorPeakTemp, 145) if motorPeakTemp != -math.inf else None),
            "Rate Of Motor Temp": ("BF", rateOfMotorTemp),
            "Avg Speed (>= 5Kmph)": ("BG", avgSpeed),
            "Avg. Motor RPM": ("BH", avgMotorRPM),
            "Motor Peak RPM": ("BI", motorPeakRPM),
            "Motor Max RPM Settings": ("BJ", rpm_max),
            "Max speed": ("BK", maxSpeed),
        }

        # -------- write to Final_summary.xlsx --------
        for header, (col, _) in row_data.items():
            if ws[f"{col}1"].value is None:
                ws[f"{col}1"] = header
        # Write data to the correct columns
        for _, (col, value) in row_data.items():
            ws[f"{col}2"] = value
            
    
        # C{row} -> odometerTripRange
        ws[f"C1"] = "Odometer Trip Range( )"
        ws[f"C2"] = odometerTripRange
        # AK{row} -> Wh/Km  (AK is column 37 -> check: A=1, Z=26, AA=27,... AK=37)
        ws[f"AK1"] = "Wh/KM"
        ws[f"AK2"] = wh_per_km
        ws[f"BU1"] = "odometery start"
        ws[f"BU2"] = odometer_first
        ws[f"BV1"] = "odometery end"
        ws[f"BV2"] = odometer_last

        # Write the remark if percentage < 95 like your Apps Script
        # if percentage < 95:
        #     # Put remark in the first free column on that row:
        #     last_col = ws.max_column + 7
        #     row = 2
        #     ws.cell(row=row, column=last_col, value=f"ECO + NEUTRAL usage below 95% ({percentage:.2f}%)")

        # wb.save(file_summary)
        percentages = {
        "ECO": eco_percentage,
        "RHINO": rhino_percentage,
        "THUNDER": Thunder_percentage
        }

        max_mode_among = max(percentages, key=percentages.get)
        MODE_PERCENT = percentages[max_mode_among]
        
        if  MODE_PERCENT < 95:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)

            existing_value = ws.cell(row=row, column=col).value
            new_remark = f"{max_mode_among} usage below 95% ({MODE_PERCENT:.2f}%)"

            if existing_value:  # if something already there
                ws.cell(row=row, column=col, value=f"{existing_value} + {new_remark}")
            else:  # empty cell
                ws.cell(row=row, column=col, value=new_remark)
    #--------------------------------------------------------------SOC error detection in pcan-------------------------------------------------------- 
        if round(soc_end) != 0:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            soc_nc = f"SOC incomplete in PCAN only till {soc_end}%"
            if existing_value:
                ws.cell(row=row, column=col, value=f"{existing_value} + {soc_nc}")
            else:
                ws.cell(row=row, column=col, value = soc_nc)
        if soc_start <= 98:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            soc_nc = f"SOC starts from {soc_start}% in PCAN"
            if existing_value:
                ws.cell(row=row, column=col, value=f"{existing_value} + {soc_nc}")
            else:
                ws.cell(row=row, column=col, value = soc_nc)
        if sudden_jumps:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            #print(f"{len(sudden_jumps)} sudden jumps detected:")
            for start_val, end_val in sudden_jumps:
                soc_jump = f"SOC data missing from {start_val}% to {end_val}% in PCAN"
                if existing_value:
                    ws.cell(row=row, column=col, value=f"{existing_value} + {soc_jump}")
                else:
                    ws.cell(row=row, column=col, value = soc_jump)
                #print(f"  ⚠️ {start_val}% → {end_val}%")
        if error_ranges:
            row = 2
            col = 70  # BR column index (since A=1, BR=70)
            existing_value = ws.cell(row=row, column=col).value
            #print(f"{len(sudden_jumps)} sudden jumps detected:")
            for start_val, end_val in error_ranges:
                if start_val == end_val:
                    soc_jump = f"GARBAGE data at {start_val}% of soc in PCAN"
                else:
                    soc_jump = f"GARBAGE data from {start_val}% to {end_val}% of soc in PCAN"
                if existing_value:
                    ws.cell(row=row, column=col, value=f"{existing_value} + {soc_jump}")
                else:
                    ws.cell(row=row, column=col, value = soc_jump)
        # if marvel_error_summary:
        #     row = 2
        #     col = 70  # BR column index (since A=1, BR=70)
        #     existing_value = ws.cell(row=row, column=col).value
        #     #print(f"{len(sudden_jumps)} sudden jumps detected:")
        #     for code, count, soc_ranges in marvel_error_summary:
        #         range_strs = [f"{start}-{end}" if start != end else f"{start}" for start, end in soc_ranges]
        #         statement = f"marvel error {code} (x{count}) - {marvel_error_detect(code)} at {range_strs}% SOC "
        #         if existing_value:
        #             ws.cell(row=row, column=col, value=f"{existing_value} + {statement}")
        #         else:
        #             ws.cell(row=row, column=col, value = statement)
        # if  marvel_cr_error_summary:
        #     row = 2
        #     col = 70  # BR column index (since A=1, BR=70)
        #     existing_value = ws.cell(row=row, column=col).value
        #     #print(f"{len(sudden_jumps)} sudden jumps detected:")
        #     for code, count, soc_ranges in  marvel_cr_error_summary:
        #         range_strs = [f"{start}-{end}" if start != end else f"{start}" for start, end in soc_ranges]
        #         statement = f"marvel critical error {code} (x{count}) - {marvel_cr_error_detect(code)} at {range_strs}% SOC "
        #         if existing_value:
        #             ws.cell(row=row, column=col, value=f"{existing_value} + {statement}")
        #         else:
        #             ws.cell(row=row, column=col, value = statement)
        # if marvel_warning_summary:
        #     row = 2
        #     col = 70  # BR column index (since A=1, BR=70)
        #     existing_value = ws.cell(row=row, column=col).value
        #     #print(f"{len(sudden_jumps)} sudden jumps detected:")
        #     for code, count, soc_ranges in marvel_warning_summary:
        #         range_strs = [f"{start}-{end}" if start != end else f"{start}" for start, end in soc_ranges]
        #         statement = f"marvel warning {code} (x{count}) - {marvel_warning_detect(code)} at {range_strs}% SOC "
        #         if existing_value:
        #             ws.cell(row=row, column=col, value=f"{existing_value} + {statement}")
        #         else:
        #             ws.cell(row=row, column=col, value = statement)
        row = 2
        col_date = 1
        col_start_time = 2
        col_end_time = 16
        existing_value_date = ws.cell(row=row, column=col_date).value
        if existing_value_date in ["","01-01-1900","01/01/1900","01:01:1900"]:
            ws.cell(row=2, column=col_date, value=start_date_only)
            ws.cell(row=2, column=col_start_time, value=start_time_only)
            ws.cell(row=2, column=col_end_time, value=end_time_only)
            ws.cell(row=2, column=col_end_time+1,value=duration_minutes)
        wb.save(file_summary)
        print(f"✅ PCAN metrics written to Final_summary.xlsx and pcan mode: {mode}")
        return torque_max, rpm_max,mode

    

    def convert_xlsx_to_csv(self,xlsx_location):
        xlsx_file = xlsx_location
        folder = os.path.dirname(xlsx_location)
        csv_location = os.path.normpath(os.path.join(folder,"Final_summary.csv"))
        
        
        if os.path.exists(xlsx_file):
            df = pd.read_excel(xlsx_file)
            df.to_csv(csv_location, index=False)
            print(f"✅ Converted Final_summary.xlsx to Final_summary.csv")
            os.remove(xlsx_file)
            print(f"🗑️ Deleted Final_summary.xlsx")
            return True
        else:
            print("❌ Final_summary.xlsx not found!")
            self.job_failed.emit(2,"Unable to convert excel to csv")
            