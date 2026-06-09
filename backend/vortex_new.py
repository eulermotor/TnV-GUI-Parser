import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np
import csv
import sys
import math
import sys
import os
import time
import cantools
import mplcursors
import re
from datetime import datetime, timedelta
from matplotlib import cm
# from PyQt5.QtWidgets import (
#     QApplication, QDialog, QVBoxLayout, QCheckBox, QPushButton, QFileDialog,
#     QScrollArea, QWidget, QLabel, QTabWidget, QHBoxLayout, QToolButton, QSizePolicy
# )
# from PyQt5.QtCore import Qt
import glob
from sklearn.cluster import DBSCAN
from collections import Counter, defaultdict
from PySide6.QtCore import QThread, Signal
def select_trc_files():
    app = QApplication(sys.argv)
    files, _ = QFileDialog.getOpenFileNames(None, "Select TRC Files", "", "TRC Files (*.trc)")
    return files

def select_dbc_file():
    app = QApplication(sys.argv)
    file, _ = QFileDialog.getOpenFileName(None, "Select DBC File", "", "DBC Files (*.dbc)")
    return file
def date_and_time(decoded):
    names = []
    values = []
    for name, value in decoded.items():
        names.append(name)
        values.append(value)
    time = f"{values[0]}:{values[1]}:{values[2]}"
    date = f"{values[3]}/{values[4]}/{values[5]}"
    return date, time

def find_reference_signal(signal_store, eps=100, min_samples=10):
    """
    Finds dominant frequency cluster and selects reference signal
    (minimum length within that cluster).
    """
    clusters = {}
    # Step 1: Keep mapping (name, length)
    signal_lengths = [(name, len(values)) for name, values in signal_store.items() if len(values) > 0]

    if not signal_lengths:
        print(ValueError("signal_store is empty"))
        return None

    # Separate names and lengths
    names = [x[0] for x in signal_lengths]
    lengths = np.array([x[1] for x in signal_lengths]).reshape(-1, 1)

    # Step 2: DBSCAN
    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(lengths)

    # Step 3: Build clusters with names
    
    for name, val, label in zip(names, lengths.flatten(), labels):
        if label == -1:
            continue
        clusters.setdefault(label, []).append((name, val))

    if not clusters:
        return {
            "reference_signal": None,
            "reference_length": None,
            "cluster_range": None,
            "outliers": signal_lengths,
            "all_clusters":{}
        }

    # Step 4: Find dominant cluster
    dominant_label = max(clusters, key=lambda k: len(clusters[k]))
    dominant_cluster = clusters[dominant_label]

    # Step 5: Find minimum length signal in cluster
    reference_signal, reference_length = min(dominant_cluster, key=lambda x: x[1])

    # Step 6: Cluster stats
    cluster_values = [val for _, val in dominant_cluster]
    cluster_min = min(cluster_values)
    cluster_max = max(cluster_values)

    # Step 7: Outliers
    outliers = [(name, val) for name, val, label in zip(names, lengths.flatten(), labels) if label == -1]

    return {
        "reference_signal": reference_signal,
        "reference_length": reference_length,
        "cluster_range": (cluster_min, cluster_max),
        "cluster_signals": dominant_cluster,
        "outliers": outliers,
        "all_clusters": clusters
    }


def extract_start_time(lines):
    for line in lines:
        start_time_str = None
        if line.startswith(';   Start time:'):
            start_time_str = line.split(':', 1)[1].strip()
            formats = [
        # --- ISO formats ---
                "%Y-%m-%d %H:%M:%S", 
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H:%M:%S.%f",

                # --- European dash ---
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y %H:%M", 
                "%d-%m-%Y %H:%M:%S.%f", 
                "%d-%m-%Y %H:%M:%S.%f.0",
                "%m/%d/%Y %H:%M:%S.%f.0",
                "%Y/%m/%d %H:%M:%S.%f.0",
                "%Y-%m-%d %H:%M:%S.%f.0",
            ]
            for fmt in formats:
                if start_time_str is not None:
                    try:
                        dt = datetime.strptime(start_time_str, fmt)
                        return dt
                    except ValueError:
                        continue
                else:
                    print("cant identify start time in trc.")
                    return None
    return None





reference_length = 0

def alignment(src, reference_length):
    # new_variable.clear()
    n = len(src)
    target = reference_length

    # if n == target:
    #     new_variable.extend(src)
    #     return
    if n == 0:
        src.extend([None] * target)
        return
    if n >= target:
        del src[target:]
        return
    inserts_needed = target - n
    gap = n / inserts_needed  # fractional gap allowed!
    # block = inserts_needed / n
    new_variable = []
    # if gap <= 1:
    #     y = round(block) + 1
    #     for i in range(0,n,1):
    #         new_variable.extend([src[i]]*y)
    #     src.clear()
    #     src.extend(new_variable)
    #     new_variable.clear()
    pos = 0.0
    inserted = 0

    for i, val in enumerate(src):
        new_variable.append(val)

        while inserted < inserts_needed and pos <= i:
            # Insert duplicate
            new_variable.append(val)
            inserted += 1
            pos += gap      
    src.clear()
    src.extend(new_variable)
    new_variable.clear()



def extract_number(fname):
    match = re.search(r'(\d+)', fname)  # find first number
    return int(match.group(1)) if match else 0
def decode_trc_file(self,trc_path, dbc, dbc_signal_order):
    with open(trc_path, 'r', errors='ignore') as f:
        lines = f.readlines()
    remarks = []
    trc_name = os.path.basename(trc_path)
    # -------------------------------------------------
    # Detect file version
    # -------------------------------------------------
    file_version = None
    for l in lines:
        if l.startswith(';$FILEVERSION'):
            file_version = l.split('=')[1].strip()
            break

    if file_version is None:
        # if self.parsing == "csv file only":
        #     self.job_failed.emit(1,"TRC FILEVERSION not found")
        # else:
        #     self.job_failed.emit(0,"TRC FILEVERSION not found")
        remarks.append(f"TRC FILEVERSION not found in {trc_name}")
        print(RuntimeError("TRC FILEVERSION not found"))
        return False, remarks

    print(f"Detected TRC version: {file_version}")

    # -------------------------------------------------
    # Start time (your existing logic)
    # -------------------------------------------------
    start_time = extract_start_time(lines)
    print(f"Start time: {start_time}")
    if not start_time:
        start_time = 0
        print("Unable to find start time!")

    # decoded_rows = []
    signal_set = set()
    signal_store = {}
    signal_store["Date"] = []
    signal_store["Time"] = []
    # signal_length = {}
    for msg in dbc.messages:
        for sig in msg.signals:
            signal_store[sig.name] = []
            # signal_length[sig.name] = []
    flag_start_time = 0
    start_time_ms = 0
    time_offset_ms = 0
    IDs = []
    # -------------------------------------------------
    # Parse data lines
    # -------------------------------------------------
    for line in lines:
        line = line.strip()

        # Skip comments / headers
        if not line or line.startswith(';') or line.startswith('---'):
            continue

        # Data lines always start with a digit
        if not re.match(r'^\d', line):
            continue

        try:
            parts = re.split(r'\s+', line)

            if file_version == '2.0':
                # 1 139025.800 DT 00000801 Rx 8 00 00 ...
                if parts[4] != 'Rx':
                    continue
                time_offset_ms = float(parts[1])
                if flag_start_time == 0:
                    start_time_ms = time_offset_ms
                    flag_start_time = 1
                can_id = int(parts[3], 16)
                dlc = int(parts[5])
                if can_id == 1029:
                    data = bytes(int(b) for b in parts[6:6 + dlc])
                else:
                    data = bytes(int(b,16) for b in parts[6:6 + dlc])
                


            elif file_version == '1.1':
                # 1) 6.5 Rx 00000801 8 00 00 ...
                if parts[2] != 'Rx':
                    continue

                time_offset_ms = float(parts[1])
                if flag_start_time == 0:
                    start_time_ms = time_offset_ms
                    flag_start_time = 1
                can_id = int(parts[3], 16)
                dlc = int(parts[4])
                if can_id == 1029:
                    data = bytes(int(b) for b in parts[5:5 + dlc])
                else:
                    data = bytes(int(b, 16) for b in parts[5:5 + dlc])
                

            else:
                # if self.parsing == "csv file only":
                #     self.job_failed.emit(1,f"Unsupported TRC version {file_version}")
                # else:
                #     self.job_failed.emit(0,f"Unsupported TRC version {file_version}")
                remarks.append(f"Unsupported TRC version {file_version} in {trc_name}")
                return False, remarks
            target_ID = [600,601,608,1954,1953,1830]
            if start_time != 0:
                timestamp = start_time + timedelta(milliseconds=time_offset_ms)
            
            try:
                msg = dbc.get_message_by_frame_id(can_id)
                IDs.append(can_id)
            except KeyError:
                # CAN ID not present in DBC — skip frame
                continue
            
            decoded = msg.decode(data)
            if can_id == 1029:
                date, time = date_and_time(decoded)
                signal_store["Date"].append(date)
                signal_store["Time"].append(time)
            else:
                for name, value in decoded.items():
                    if can_id in target_ID:
                        # Convert to Hex, uppercase, no '0x'
                        # Use :02X if you want to force 2 digits (e.g., '0A' instead of 'A')
                        hex_val = f"{int(value):X}" 
                        signal_store[name].append(hex_val)
                    else:
                        # Store normally (float/int)
                        signal_store[name].append(value)

        except Exception as e:
            print("Failed to parse line:")
            print(line)
            remarks.append(f"Failed to parse line: {line} in {trc_name}")
            continue
    # Step 1: count occurrences
    # ids = [row[1] for row in lines]   # adjust index if needed
    counts = Counter(IDs)

    # Step 2: group IDs by same count
    grouped = defaultdict(list)
    for can, cnt in counts.items():
        grouped[cnt].append(can)
    for cnt, IDs in grouped.items():
        print(cnt, "->", [hex(i) for i in IDs])
    if grouped:
        most_common_cnt = max(grouped, key=lambda k: len(grouped[k]))
    else:
        print("No cluster/group is formed!")
        remarks.append(f"No cluster/group is formed in {trc_name}")
    #checking the variable closest to the 100ms
    DBS_reference = find_reference_signal(signal_store, eps=100, min_samples=10)
    if DBS_reference == None:
        remarks.append(f"TRC file {trc_name} empty/corrupted")
        return False, remarks
    else:
        ref_len = DBS_reference.get("reference_length")
        clusters = DBS_reference.get("all_clusters")
    Ultimate_ref = 0
    if ref_len is None:
        print("⚠️ DBSCAN failed → falling back to ID count method")
        remarks.append(f"DBSCAN failed → falling back to ID count method in {trc_name}")
        Ultimate_ref = most_common_cnt
    else:
        Ultimate_ref = ref_len
    mul = Ultimate_ref*2.5#--------------------------> here most IDs which occured at a same length is getting multiplied by 2.5 
    # Step: filter valid candidates (at least 3 IDs)
    # valid_cnts = [cnt for cnt, ids in grouped.items() if len(ids) >= 3]

    # if not valid_cnts:
    #     raise ValueError("No grouped count has at least 3 IDs")
    best_label = None
    best_distance = float('inf')
    #finding cluster closest to the mul
    if clusters:
        for label, items in clusters.items():
            for name, val in items:
                distance = abs(val - mul)
                
                if distance < best_distance:
                    best_distance = distance
                    best_label = label
        # selected_cluster = clusters[best_label]
        if best_label is None:
            print("⚠️ No suitable cluster found → fallback")
            remarks.append(f"No suitable cluster found → fallback, in {trc_name}")
            # if self.parsing == "csv file only":
            #     self.job_failed.emit(1,"No suitable cluster found → fallback")
            # else:
            #     self.job_failed.emit(0,"No suitable cluster found → fallback")
        else:
            selected_cluster = clusters[best_label]

        # Find max length inside that cluster
        max_name, max_val = max(selected_cluster, key=lambda x: x[1])

        print("Selected cluster:", best_label)
        print("Closest match distance:", best_distance)
        print("Max signal in cluster:", max_name, max_val)
    else:
        max_name, max_vals = max(signal_store.items(), key=lambda kv: len(kv[1]))
        max_val = len(max_vals)
    # Step: find closest to mul
    # closest_cnt = min(valid_cnts, key=lambda x: abs(x - mul))
    # print("Selected count:", closest_cnt)
    # print("Reference_name_DBS: ", DBS_reference["reference_signal"])
    # print("Reference_length:", DBS_reference["reference_length"])
    # for key, value in signal_store.items():
    #     print(key, len(value),"\n")
    # difference_time_ms = time_offset_ms - start_time_ms
    # print(f"Total time in ms {difference_time_ms} ms")
    # print(f"End time in ms {time_offset_ms} ms")
    # expected_samples = difference_time_ms / 100#this divides the total ms time wrt 100ms ======>the code is "time in ms" DEPENDENT<=============
    # print(f"Expected sample length for 100ms: {expected_samples}")
    # master_signal_name, master_signal_values = min(
    #     signal_store.items(),
    #     key=lambda kv: abs(len(kv[1]) - expected_samples)
    # )
    print(f"Reference signal name: {max_name}\nReference signal length: {max_val}")
    reference_length = max_val
    to_remove = set()
    for sig_name, sig_values in signal_store.items():
        per = (len(sig_values) / reference_length) * 100
        if all(x == 0 for x in sig_values):
            to_remove.add(sig_name)
        if per < 10:
            to_remove.add(sig_name)
        elif len(sig_values) != reference_length:
            alignment(sig_values, reference_length)

    # Remove low-percentage signals
    for sig in to_remove:
        if sig in signal_store:
            del signal_store[sig]
    lengths = {k: len(v) for k, v in signal_store.items()}
    min_key = min(lengths, key=lengths.get)
    length_min = lengths[min_key]
    print(f"min length = {lengths[min_key]} (key = {min_key})")
    for sig_name, sig_values in signal_store.items():
        if len(sig_values) > reference_length:
            del sig_values[reference_length:]
        else:
            del sig_values[length_min:]
    #sanity check
    lengths = {k: len(v) for k, v in signal_store.items()}
    if len(set(lengths.values())) != 1:
        # if self.parsing == "csv file only":
        #     self.job_failed.emit(1,f"Alignment failed, lengths mismatch: {lengths}")
        # else:
        #     self.job_failed.emit(0,f"Alignment failed, lengths mismatch: {lengths}")
        remarks.append(f"Alignment method failed, lengths mismatch: {lengths} in {trc_name}")
        # raise RuntimeError(f"Alignment failed, lengths mismatch: {lengths}")
    min_key = min(lengths, key=lengths.get)
    
    print(f"min length after = {lengths[min_key]} (key = {min_key})")
    # -------------------------------------------------
    # Final DataFrame
    # -------------------------------------------------
    df = pd.DataFrame(signal_store)
    final_columns = [col for col in dbc_signal_order if col in signal_store]
    df = df.reindex(columns=final_columns)
    df = df.fillna(0)
    df = df.infer_objects(copy=False)
    if df.empty:
        remarks.append(f"Decoded DataFrame is empty — TRC {trc_name} parsing failed")
        return False, remarks
    output_csv = trc_path.replace(".trc", "_pcan.csv")
    df.to_csv(output_csv, index=False)
    return True, remarks
    clusters.clear()
    
# ---------- Main ----------
def fetching_trc_dbc(self,trc_loc,dbc_loc):
    
    def extract_part_number(filename):
    # Find all matches like 'part 10', 'PART10', etc.
        matches = re.findall(r'part\s*(\d+)', filename, re.IGNORECASE)
        if matches:
            return int(matches[-1])  # Use the last occurrence
        return float('inf')  # Push unmatched files to the end
    
    # Get all .trc files
    trc_files = [f for f in trc_loc if f.lower().endswith('.trc')]
    trc_files.sort(key=extract_part_number)
    if not trc_files:
        print("No TRC files selected.")
        # self.job_failed.emit(0, "Failed to pick trc files")
        return False, None, None, None, "Failed to pick trc files"
    # dbc_file = [f for f in os.listdir('.') if f.lower().endswith('.dbc')]
    # dbc_file = next((f for f in os.listdir('.') if f.lower().endswith('.dbc')), None)
    dbc_file = dbc_loc
    if not dbc_file:
        print("No DBC file selected.")
        # self.job_failed.emit(0,"Failed to pick DBC file")
        return False, None, None, None, "Failed to pick DBC file"
    # Sort files by extracted part number
    

    # trc_dir = os.path.dirname(trc_files[0])

    trc_dir = os.path.abspath(os.path.dirname(trc_files[-1]))
    dbc = cantools.database.load_file(dbc_file)
    # all_dfs = []
    # full_signal_set = set()
    dbc_signal_order = []
    dbc_signal_order.append("Date")
    dbc_signal_order.append("Time")
    for msg in dbc.messages:
        for sig in msg.signals:
            dbc_signal_order.append(sig.name)
    return True, trc_files, dbc, dbc_signal_order, trc_dir
def creating_csv(self,trc_files,dbc,dbc_signal_order):  
    remarks = []
    count = 0
    for trc in trc_files:
        if not self._is_running: return
        # clusters.clear()
        signal = decode_trc_file(self,trc, dbc, dbc_signal_order)
        success, re = signal
        if success == False:
            count += count
        remarks.extend(re)
    if len(trc_files) == count:
        remarks.clear()
        remarks.append("All trc files are either corrupt/not ideal for dbc.")
        return False, remarks
    return True, remarks
    # --- helper to extract numbers from filenames ---



    # for filename in os.listdir():
    #     if filename.lower().endswith("bmslog.csv") and filename != "bmslog.csv":
    #         os.rename(filename, "bmslog.csv")
    #         break 
def merging_trc(self,trc_dir):
    for filename in os.listdir(trc_dir):
        if filename.lower().endswith("bmslog.csv") and filename != "bmslog.csv":
            os.rename(
                os.path.join(trc_dir, filename),
                os.path.join(trc_dir, "bmslog.csv")
            )
            break

    # file_list = [f for f in glob.glob("*.csv") 
    # if os.path.basename(f).lower() not in ["bmslog.csv", "pcan.csv"]]
    # full_files    = [f for f in file_list if f.endswith("_pcan.csv")]
    # full_files.sort(key=extract_number)


    # if full_files:
    #     csv_merged_full = pd.concat([pd.read_csv(f) for f in full_files])
    #     csv_merged_full.to_csv("pcan.csv", index=False)

    file_list = [
        f for f in glob.glob(os.path.normpath(os.path.join(trc_dir, "*.csv")))
        if os.path.basename(f).lower() not in ["bmslog.csv", "pcan.csv"]
    ]
    full_files = [f for f in file_list if f.endswith("_pcan.csv")]
    full_files.sort(key=lambda x: extract_number(os.path.basename(x)))
    if not full_files:
        # if self.parsing == "csv file only":
        #     self.job_failed(2,"Failed to sort merge csv files")
        # else:
        #     self.job_failed(1,"Failed to sort merge csv files")
        return False, None
    return True, full_files
def creating_pcan(self,trc_dir,full_files):
    if full_files:
        csv_merged_full = pd.concat([pd.read_csv(f) for f in full_files])
        csv_merged_full.to_csv(os.path.normpath(os.path.join(trc_dir, "pcan.csv")), index=False)
    else:
        # if self.parsing == "csv file only":
        #     self.job_failed(3,"unable to create pcan.csv")
        # else:
        #     self.job_failed(1,"unable to create pcan.csv")
        return False
    return True
    # if not all_dfs:
    #     print("No usable data decoded.")
    #     return

    # final_df = pd.concat(all_dfs).sort_values(by='Time').reset_index(drop=True)
    # signal_columns = [c for c in final_df.columns if c != 'Time']
    # missing_mask = final_df[signal_columns].isna()
    # final_df[signal_columns] = final_df[signal_columns].ffill()
    # final_df.to_csv("final_output.csv", index=False)

    # app = QApplication(sys.argv)
    # dialog = GroupedSignalSelector(sorted(full_signal_set))
    # if not dialog.exec_():
    #     return

    # signal_groups = dialog.get_groups()
    # if not signal_groups:
    #     print("No signal groups selected.")
    #     return

    # flat_signals = sorted(set(sig for group in signal_groups for sig in group))
    # images = plot_groups(final_df[flat_signals + ['Time']], signal_groups)
    

# if __name__ == "__main__":
#     main()

class ProcessingWorker(QThread):
    job_starting = Signal(int)
    job_completed = Signal(int)
    job_failed = Signal(int,str)
    data = Signal(list)
    def __init__(self,trc_list,dbc_loc,parsing):
        super().__init__()
        self.trc_list_location = trc_list
        self.dbc_location = dbc_loc
        self.parsing = parsing
        self.remarks = []
        # self.run()
        self._is_running = True
    def stop(self):
        self._is_running = False
    def run(self):
        time.sleep(2)
        # --- STEP 0: Fetching ---
        self.job_starting.emit(0)
        result = fetching_trc_dbc(self,self.trc_list_location,self.dbc_location)
        directory = os.path.dirname(self.trc_list_location[-1])
        # Check if user cancelled selection or it failed
        if not result or not result[0]:
            self.job_failed.emit(0,result[-1])
            return # Stop processing
        if not self._is_running: return
        # Unpack results for the next steps
        # result = (True, trc_files, dbc, dbc_signal_order, trc_dir)
        _, trc_files, dbc, dbc_signal_order, trc_dir = result
        if self.parsing == "csv file only":
            self.job_completed.emit(0)
        skip_flag = 0
        # --- STEP 1: Creating CSV ---
        if self.parsing == "csv file only":
            time.sleep(2)
            self.job_starting.emit(1)
        if os.path.exists(os.path.normpath(os.path.join(directory,"pcan.csv"))):
            skip_flag = 1
            if self.parsing == "csv file only":
                self.job_completed.emit(1)
            else:
                self.job_completed.emit(0)
        else:
            success_csv = creating_csv(self,trc_files, dbc, dbc_signal_order)
            re, remark = success_csv
            if not self._is_running: return
            if re:
                self.remarks.extend(remark)
                if self.parsing == "csv file only":
                    self.job_completed.emit(1)
                else:
                    self.job_completed.emit(0)
            else:
                string = remark[-1]
                if self.parsing == "csv file only":
                    self.job_failed.emit(1,string)
                else:
                    self.job_failed.emit(0,string)
                return
        time.sleep(1)
        # --- STEP 2: Merging ---
        if self.parsing == "csv file only":
            self.job_starting.emit(2)
        else:
            self.job_starting.emit(1)
        # result = (True, full_files)
        if skip_flag == 1:
            print("pcan.csv already exist")
            if self.parsing == "csv file only":
                self.job_completed.emit(2)
        else:
            merge_result = merging_trc(self,trc_dir)
            if not self._is_running: return
            if merge_result and merge_result[0]:
                _, full_files = merge_result
                if self.parsing == "csv file only":
                    self.job_completed.emit(2)
            else:
                if self.parsing == "csv file only":
                    self.job_failed.emit(2, "Failed to merge csv files")
                else:
                    self.job_failed.emit(1, "Failed to merge csv files")
                return

        # --- STEP 3: Creating Pcan ---
        if self.parsing == "csv file only":
            time.sleep(1)
            self.job_starting.emit(3)

        if skip_flag == 1:
            if self.parsing == "csv file only":
                time.sleep(3)
                self.job_completed.emit(3)
            else:
                self.job_completed.emit(1)
        else:
            time.sleep(2)
            if not self._is_running: return
            success = creating_pcan(self,trc_dir,full_files) 
            if success:
                if self.parsing == "csv file only":
                    self.job_completed.emit(3)
                else:
                    self.job_completed.emit(1)
                self.data.emit(self.remarks)
            else:
                if self.parsing == "csv file only":
                    self.job_failed.emit(3,"Failed to create pcan.csv")
                else:
                    self.job_failed.emit(1,"Failed to create pcan.csv")
                return