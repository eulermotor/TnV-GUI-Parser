import os
import pandas as pd
import logging
import glob
import csv
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
from datetime import datetime, date, time as dt_time
# Setup logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ProcessingWorkersummary_3W(QThread):
    job_starting = Signal(int)
    job_completed = Signal(int)
    job_failed = Signal(int,str)
    
    def __init__(self,vehicle_name,trc_files,dbc_new_location,Tyre_size_name,DRR,Battery_name,Battery_Model,Battery_Voltage,Battery_capacity,gear_ratio,vehicle_variant):
        super().__init__()
        # self.trc_list_location = trc_list
        # self.dbc_location = dbc_loc
        self.V_name = vehicle_name
        self.trc_list = os.path.dirname(trc_files[0])
        self.dbc = dbc_new_location
        self.tyresize = Tyre_size_name
        self.DRRn = DRR
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
        dbc_name = os.path.basename(dbc_new_location)
        self.mark_flag = 0
        if dbc_name == "Gtake+marvel+Mark Updated.dbc":
            self.mark_flag = 1
    def stop(self):
        self._is_running = False
        
    def run(self):
        # logging.info(f"📂 Processing folder: {os.path.basename(self.trc_list)}")
        print(f"📂 Processing folder: {os.path.basename(self.trc_list)}")
        print(f"before making final_summary.xlsx {self.trc_list}")
        self.summary_file = os.path.normpath(os.path.join(self.trc_list, "Final_summary.xlsx"))
        # --- STEP 0: Fetching ---
        time.sleep(1)

        if not self._is_running: return
        self.job_starting.emit(0)
        print(f"just before pcan error{self.trc_list}")
        pcan_path = os.path.normpath(os.path.join(self.trc_list, "pcan.csv"))
        print(f"pcan_path detected {pcan_path}")
        if not os.path.exists(pcan_path):
            print("pcan.csv doesnt exist in the current folder")
            self.job_failed.emit(0,"Unable to find pcan.csv")
            return 
        time.sleep(2)
        df_pcan = pd.read_csv(pcan_path)
        pcan_result = self.process_pcan_data(df_pcan, self.summary_file, self.bat_volt,self.bat_cap, self.DRRn, self.g_ratio)
        ARMS_max, rpm_max, mode = pcan_result
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
        raise ValueError(f"Invalid date format encountered: {date_str}")
        
    def parse_custom_time(self, date_str, return_format=False):
        if isinstance(date_str, dt_time):
            return (date_str, "time object") if return_format else date_str

        if not isinstance(date_str, str):
            raise ValueError(f"Invalid input: {date_str}")

        date_str = " ".join(date_str.strip().split())

        formats = [
            ("%H:%M:%S.%f", "with ms"),
            ("%H:%M:%S", "HH:MM:SS"),
            ("%H:%M", "HH:MM"),
        ]

        for fmt, label in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # 🔥 FIX: Use built-in .time() instead of .dt_time()
                return (dt.time(), label) if return_format else dt.time()
            except ValueError:
                continue

        raise ValueError(f"Invalid time format: {date_str}")


    def calculate_imbalance(self,row, cell_cols):
        # print("reached in imbalance function")
        try:
            
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
            
   
                    
    def process_pcan_data(self,df_pcan, summary,pack_capacity_coeff ,peak_c_rate, DRRn, g_ratio):
        file_summary = summary
        # energy_consumed_wh = ECWh
        # Load merged data
        data = df_pcan.values.tolist()
    #---------------------------------------------------------------edit here for vehicle changes----------------------------------------------------
        if not data:
            self.job_failed.emit(1,"Empty pcan file!!")
            raise ValueError("pcan sheet is empty!")
        marvel = 1
        # sec_row = data[0]
        # total = len(sec_row)
        # numeric_count = 0
        # for val in sec_row:
        #     try:
        #         if pd.notna(val):
        #             float(val)
        #             numeric_count += 1
        #     except:
        #         pass
        # if numeric_count/total < 0.5:
        #     marvel = 1
        #     battery_pack = 1
        #     print("FILE DETECTED!!!!")
        # else:
        #     print("FILE NOT DETECTED!!")
        if not data:
            raise ValueError("bms sheet is empty!")
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
        
        odometerlist = []
        date = []

        # ECO + Neutral %
        # (Your Apps Script loop over colGearMode looked buggy; here we compute correctly)
        rows = df_pcan
        rpm_valid = rows[(rows["Vehicle_mode"].isin(["Eco", "Thunder"])) & (rows["RPM"] > 0)]["RPM"]

        total_rpm_points = len(rpm_valid)

        def rpm_pct(cond):
            return round((cond.sum() / total_rpm_points * 100), 2) if total_rpm_points else 0

        rpm_100_2000_pct = rpm_pct((rpm_valid >= 100) & (rpm_valid < 2000))
        rpm_2000_3000_pct = rpm_pct((rpm_valid >= 2000) & (rpm_valid < 3000))
        rpm_3000_4000_pct = rpm_pct((rpm_valid >= 3000) & (rpm_valid < 4000))
        rpm_4000_5000_pct = rpm_pct((rpm_valid >= 4000) & (rpm_valid < 5000))
        rpm_5000_6000_pct = rpm_pct((rpm_valid >= 5000) & (rpm_valid < 6000))
        rpm_6000_plus_pct = rpm_pct(rpm_valid >= 6000)

        total_modes = rows["Vehicle_mode"].notna().sum()
        Reverse_neutral = rows["Vehicle_mode"].isin(["Reverse", "Neutral"]).sum()
        Eco = rows["Vehicle_mode"].isin(["Eco"]).sum()
        Thunder = rows["Vehicle_mode"].isin(["Thunder"]).sum()
    
        Total = Eco + Thunder
    #we are comparing the percentage removing neutral and reverse
        eco_percentage = (Eco / Total * 100) if Total else 0
        Thunder_percentage = (Thunder / Total * 100) if Total else 0
        MODE = "NIL"
        if eco_percentage >= 95:
            MODE = "ECO"
        elif Thunder_percentage >= 95:
            MODE = "THUNDER"
        else:
            MODE = "NOT-DEFINED"
        mode = max(
            ("ECO", eco_percentage),
            ("THUNDER", Thunder_percentage),
            key=lambda x: x[1]
        )[0]
        m = None
        if mode == "ECO":
            m = "Eco"
        elif mode == "THUNDER":
            m = "Thunder"
        rpm_max = 6500 #default
        ARMS_max = 400
        print(f"vehicle info {self.Variant},{self.V_name},{mode}")
        if self.Variant == "XR_NEO":
            ARMS_max = 250
            rpm_max = 6000
        elif self.Variant == "SR_HR":
            ARMS_max = 300
            rpm_max = 7000
        elif self.Variant == "XR_HR":
            ARMS_max = 325
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
        PACK_TEMP_MAX = []
        PACK_TEMP_MIN = []
        PACK_TEMP_SUM = []
        SOC_LIST = []
        real_speed = []
        controllerARMS = []
        flag_temp = 0
        PACK_TEMP = []
        
        real_speed = []
        actualodo = []
        
        # Add "Kmph" column to the dataframe (like you did to the sheet)
        #df_pcan["Kmph"] = df_pcan["speed"] / conversion_factor
        def clean(val, default=None):  # Change default to None
            return default if pd.isna(val) or val == "" else val
       
        if marvel == 1:     
            cell_cols = []
            cell_cols = [col for col in df_pcan.columns if col.startswith(("CellVoltage_", "CMU_","Cell_Voltage"))]
            df_pcan = df_pcan.iloc[1:].reset_index(drop=True)
            has_ext_temp = "Ext_Temp_Max" in df_pcan.columns and "Ext_Temp_Min" in df_pcan.columns
            # Pre-find thermistor columns once to save CPU cycles
            thermistor_cols = [col for col in df_pcan.columns if col.startswith("Thermistor_")]
            print(f"Found {len(cell_cols)} cell columns.")
            
            for i in range(len(df_pcan) - 1):
                curr = df_pcan.iloc[i]
                nxt = df_pcan.iloc[i + 1]

                voltage          = clean(curr['Pack_Voltage'])
                next_voltage     = clean(nxt['Pack_Voltage'])
                current          = clean(curr['Pack_Current'])
                next_current     = clean(nxt['Pack_Current'])
                SOC              = clean(curr['BMS_SoC'])
                pack_capacity    = clean(curr['Pack_Capacity'])
                gearMode         = curr["Vehicle_mode"]
                acVoltage        = clean(curr["VRMS"])
                rpm              = clean(curr["RPM"])
                controllerTemp   = clean(curr["MCU_Temperature"])
                controllerCurrent= clean(curr["ARMS"])
                motorTemp        = clean(curr["Motor_Temperature"])
                ODO              = clean(curr["Odometer"])#Odometer
                # max_temp         = float(clean(curr["Ext_Temp_Max"]))
                # min_temp         = float(clean(curr["Ext_Temp_Min"]))
                # if self.mark_flag == 0:
                #     DATE             = curr["Date"]
                #     TIME             = curr["Time"]
                if voltage is None or next_voltage is None or current is None or next_current is None or SOC is None or pack_capacity is None or acVoltage is None or rpm is None or controllerTemp is None or controllerCurrent is None or motorTemp is None or ODO is None:
                    continue
                if not self._is_running: return
                voltage           = float(voltage)
                next_voltage      = float(next_voltage)
                current           = float(current)
                next_current      = float(next_current)
                SOC               = float(SOC)
                pack_capacity     = float(pack_capacity)
                acVoltage         = float(acVoltage)
                rpm               = float(rpm)
                controllerTemp    = float(controllerTemp)
                controllerCurrent = float(controllerCurrent)
                motorTemp         = float(motorTemp)
                ODO               = float(ODO)
                if gearMode == m:
                    power = voltage * current
                    avg_power = (power + next_voltage * next_current) / 2 if i > 1 else 0
                    currents.append(current)
                    PACK_C.append(pack_capacity)
                    PACK_V.append(voltage)
                    SOC_LIST.append(SOC)
                    max_temp = None
                    min_temp = None
                    odometerlist.append(ODO)
                    if len(odometerlist)==1:
                        actualodo.append(odometerlist[-1])
                    if len(odometerlist)>1:
                        if odometerlist[-1]>=actualodo[-1]:
                            actualodo.append(odometerlist[-1])
                    if has_ext_temp:
                        try:
                            # Using clean() assuming it handles empty strings/NaN gracefully
                            raw_max = clean(curr["Ext_Temp_Max"])
                            raw_min = clean(curr["Ext_Temp_Min"])
                            if raw_max is None or raw_min is None:
                                continue
                            if pd.notna(raw_max) and raw_max != "":
                                max_temp = float(raw_max)
                            if pd.notna(raw_min) and raw_min != "":
                                min_temp = float(raw_min)
                        except (ValueError, TypeError):
                            self.job_failed.emit(0,"failed to process temperature data")
                            pass # Fallback if parsing fails

                    # 3. Use explicit "is None" checks to avoid the 0°C bug
                    if max_temp is None or min_temp is None:
                        # Fallback to Thermistor columns
                        all_vals = [
                            float(curr[col])
                            for col in thermistor_cols
                            if pd.notna(curr[col]) and str(curr[col]).strip() != "" and float(curr[col]) > 0
                        ]
                        
                        if flag_temp == 0:
                            if all_vals:
                                battery_start_temp = max(all_vals)
                                battery_start_temp_min = min(all_vals)
                            else:
                                battery_start_temp = battery_start_temp_min = None
                            flag_temp = 1
                        PACK_TEMP.extend(all_vals)
                        
                    else:
                        # Standard External Temp logic
                        if flag_temp == 0:
                            battery_start_temp = max_temp
                            battery_start_temp_min = min_temp
                            flag_temp = 1
                        
                        temp_sum = (max_temp + min_temp)/2
                        PACK_TEMP_SUM.append(temp_sum)
                        PACK_TEMP_MAX.append(max_temp)
                        PACK_TEMP_MIN.append(min_temp)
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
                            error_points.append(SOC)

                    end_imbalance = imbalance
                    total_imbalance += imbalance
                    count_imbalance += 1
                    peak_imbalance = max(peak_imbalance, imbalance)
                    # input power
                    inputPower = current * voltage
                    if inputPower > inputPowerMax:
                        inputPowerMax = inputPower
                    inputPowerTotal += inputPower
                    inputPowerCount += 1
                    #Date and time
                    # if pd.notna(DATE) and pd.notna(TIME):
                        
                    #     if DATE and DATE != "00/00/2000  00:00:00":
                    #         date.append(f"{DATE} {TIME}")
                    # output power
                    # (2*pi*rpm*torque)/60
                    # outputPower = (2 * math.pi * rpm * torque) / 60.0
                    # outputPowerTotal += outputPower
                    # outputPowerCount += 1
                    # if outputPower > outputPowerMax:
                    #     outputPowerMax = outputPower
                    real_speed.append(np.round(((((rpm/gear_ratio)*2*np.pi) /60)*drr)*3.6, 2))
                    # controller start temp
                    if acVoltage != 0 and controllerStartTemp is None:
                        controllerStartTemp = controllerTemp
                    if acVoltage != 0:
                        controllerPeakTemp = max(controllerPeakTemp, controllerTemp)
                    controllerPeakCurrent = max(controllerPeakCurrent, controllerCurrent)
                    controllerARMS.append(float(controllerCurrent))
                    if motorInitialTemp is None and acVoltage != 0:
                        motorInitialTemp = motorTemp
                    if acVoltage !=0:
                        motorPeakTemp = max(motorPeakTemp, motorTemp)

                    # peakTorque = max(peakTorque, torque)
                    # peakRegenTorque = min(peakRegenTorque, torque)
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
                
        else:
            print("FAILED TO PROCESS DATA!!")
            self.job_failed.emit(0,"failed to process data")
                    
            
               
        if actualodo:
            print(f"length of odo:{len(actualodo)}")
            odometer_first = min(actualodo)
            odometer_last = max(actualodo)
        #--------------------------------------------------------------------------------<<<<<<<<<<<<<<<<  BMS PROCESSING >>>>>>>>>>>>>>>>------------------------------------------------
        # Average current
        avg_battery_current = abs(sum_current / count_current) if count_current else 0
        batterypeak_current = abs(min(currents)) if currents else 0
        peak_crate = batterypeak_current / peak_c_rate

        regen_energy_wh = total_regen_power / 3600 if regen_count else 0
        drive_energy_wh = abs(total_drive_power) / 3600 if drive_count else 0
        regen_percent_recovery = (regen_energy_wh / drive_energy_wh) * 100 if drive_energy_wh else 0
        avg_average_power = total_regen_power / regen_count if regen_count else 0
        regen_percent_recovery = round(regen_percent_recovery, 2)
        avg_imbalance = total_imbalance / count_imbalance if count_imbalance else 0
        min_cell_temp = 0
        average_cell_temp = 0
        # Battery capacity and voltage
        try:
            if marvel == 1:
                battery_v_start = PACK_V[0]
                battery_v_end = PACK_V[-1]
                initial_capacity_asec = PACK_C[0]*3600 
                final_capacity_asec = PACK_C[-1]*3600
                if len(PACK_TEMP)<1:
                    peak_cell_temp = max(PACK_TEMP_MAX) if PACK_TEMP_MAX else 0
                    min_cell_temp = min(PACK_TEMP_MIN) if PACK_TEMP_MIN else 0
                    average_cell_temp = sum(PACK_TEMP_SUM)/len(PACK_TEMP_SUM) if PACK_TEMP_SUM else 0
                else:
                    peak_cell_temp = max(PACK_TEMP) if PACK_TEMP else 0
                    min_cell_temp = min(PACK_TEMP) if PACK_TEMP else 0
                    average_cell_temp = sum(PACK_TEMP)/len(PACK_TEMP) if PACK_TEMP else 0
        except (ValueError, IndexError):
            raise ValueError("Battery data missing or corrupted")
            self.job_failed.emit(0,"Battery data missing or corrupted")

        initial_capacity_ah = initial_capacity_asec / 3600
        final_capacity_ah = final_capacity_asec / 3600
        capacity_used_ah = initial_capacity_ah - final_capacity_ah
        pack_capacity_used_wh = capacity_used_ah * pack_capacity_coeff
        energy_consumed_wh = (battery_v_start * initial_capacity_ah) - (battery_v_end * final_capacity_ah)
        print(f"sum controller ARMS {sum(controllerARMS)} \n length controller ARMS {len(controllerARMS)}\n")
        controllerAvgCurrent = sum(controllerARMS)/len(controllerARMS)
        print("odometery last", odometer_last)
        print("odometery first", odometer_first)
        print("odometery last", odometer_last)

        odometerTripRange = odometer_last - odometer_first
        self.job_completed.emit(0)
        time.sleep(2)
        self.job_starting.emit(1)
        soc_list = []
        soc_value = None
        # Time and duration
        duration_minutes = "nill"
        start_time_only = "H:M:S"
        end_time_only = "H:M:S"
        start_date_only = "d/m/Y"
        soc_list.extend(SOC_LIST)
        if self.mark_flag == 0:
            date_str = data[2][0]
            date_end_str = data[-1][0]
            start_str = data[2][1]
            end_str = data[-1][1]
            date_str_new = self.parse_custom_date(date_str)
            date_end_new = self.parse_custom_date(date_end_str)
            end_time = self.parse_custom_time(end_str)
            start_time = self.parse_custom_time(start_str)
            start_dt = datetime.combine(date_str_new, start_time)
            end_dt = datetime.combine(date_end_new, end_time)

            duration_minutes = (end_dt - start_dt).total_seconds() / 60
            start_time_only = start_time.strftime("%H:%M:%S")
            end_time_only = end_time.strftime("%H:%M:%S")
            start_date_only = date_str_new.strftime("%d/%m/%Y")
        
        #Indentifying errors and calling them out
        

        # iterate rows
        soc_last = float(soc_list[-1])
        soc_start = float(soc_list[0])
        threshold = 5  # you can adjust this (e.g. detect jumps >5%)

        # Detect sudden jumps
        recovery_threshold = 3  # how close it should come back to previous value

        sudden_jumps = []
        # Detect sudden jumps
        for i in range(1, len(soc_list)):
            drop = float(soc_list[i-1]) - float(soc_list[i])

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


    
        # --- Prepare error descriptions for Excel BR column ---
        error_details = []
        if error_points:  # only if errors found
            imbalance_str = f"Imbalance >200mV between 97–100% SOC at {sorted(set(error_points))}"
            error_details.append(imbalance_str)
        error_details_str = "; ".join(error_details) if error_details else ""
        avgSpeed = (speedSum / speedCount) if speedCount else 0
        avgMotorRPM = avgSpeed * conversion_factor
        motorPeakRPM = maxSpeed * conversion_factor
        rateOfMotorTemp = (motorPeakTemp - motorInitialTemp) if (motorInitialTemp is not None and motorPeakTemp != -math.inf) else 0
        # avgOutputPower = (outputPowerTotal / outputPowerCount) if outputPowerCount > 0 else 0
        avgInputPower  = (inputPowerTotal  / inputPowerCount ) if inputPowerCount  > 0 else 0
        # motorEfficiency = ((avgOutputPower / avgInputPower) * 100) if avgInputPower != 0 else 0

        wh_per_km = (energy_consumed_wh / odometerTripRange) if odometerTripRange != 0 else 0
        # If the file exists, load it; otherwise, create a new workbook
        if os.path.exists(summary):
            wb = openpyxl.load_workbook(summary)
            ws = wb.active
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
        # Find the next empty row
        next_row = ws.max_row + 1 if ws.max_row > 1 or ws.cell(1, 1).value else 2
        row_data = {
            "Start Date": ("A", start_date_only),
            "Start Time": ("B", start_time_only),
            "Drive mode": ("D", MODE),
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
            "Peak Drive input power (W)": ("AS", inputPowerMax),
            "Pack Capacity Used (Wh)": ("AT", pack_capacity_used_wh),
            "Controller Mode": ("AU", "Torque"),
            "Controller Start Temp": ("AV", controllerStartTemp),#celcius
            "Controller Peak Temp": ("AW", controllerPeakTemp),
            "Controller Peak ARMS": ("AX", controllerPeakCurrent),#amph
            "Controller Avg ARMS": ("AY", controllerAvgCurrent),#<--------------------------------not coming?
            "Motor Initial Temp": ("AZ", motorInitialTemp),
            "Motor Peak temp (Max operating Temp: 145'C)": ("BA", min(motorPeakTemp, 145) if motorPeakTemp != -math.inf else None),
            "Rate Of Motor Temp": ("BB", rateOfMotorTemp),
            "Avg Speed (>= 5Kmph)": ("BC", avgSpeed),
            "Avg. Motor RPM": ("BD", avgMotorRPM),
            "Motor Peak RPM": ("BE", motorPeakRPM),
            "Max speed": ("BF", maxSpeed),
            "min cell temp": ("BG",min_cell_temp),
            "average cell temp": ("BH",average_cell_temp),
            "BMS Errors": ("BN", error_details_str),
            "RPM 100-2000 %": ("BQ",rpm_100_2000_pct),
            "RPM 2000-3000 %": ("BR",rpm_2000_3000_pct),
            "RPM 3000-4000 %": ("BS",rpm_3000_4000_pct),
            "RPM 4000-5000 %": ("BT",rpm_4000_5000_pct),
            "RPM 5000-6000 %": ("BU",rpm_5000_6000_pct),
            "RPM 6000+ %": ("BV",rpm_6000_plus_pct),
            "Eco percentage (%)":("BW",eco_percentage),
            "Thunder percentage (%)":("BX",Thunder_percentage)
        }

        for header, (col, _) in row_data.items():
            if ws[f"{col}1"].value is None:
                ws[f"{col}1"] = header
        # Write data to the correct columns
        for _, (col, value) in row_data.items():
            ws[f"{col}{next_row}"] = value
        # C{row} -> odometerTripRange
        ws[f"C1"] = "Odometer Trip Range( )"
        ws[f"C2"] = odometerTripRange
        # AK{row} -> Wh/Km  (AK is column 37 -> check: A=1, Z=26, AA=27,... AK=37)
        ws[f"AK1"] = "Wh/KM"
        ws[f"AK2"] = wh_per_km
        ws[f"BO1"] = "odometery start"
        ws[f"BO2"] = odometer_first
        ws[f"BP1"] = "odometery end"
        ws[f"BP2"] = odometer_last
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
        wb.save(summary)
        print("✅ Final_summary.xlsx updated successfully.")
        return ARMS_max,rpm_max,mode

    

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
            