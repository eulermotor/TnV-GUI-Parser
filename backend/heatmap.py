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

from collections import defaultdict
from PySide6.QtCore import QThread, Signal
import time


class ProcessingWorkerheatmap(QThread):
    job_starting = Signal(int)
    job_completed = Signal(int)
    job_failed = Signal(int,str)
    def __init__(self,path_n,option1,rpm_max,V_type):
        super().__init__()
        import warnings
        warnings.filterwarnings("ignore")
        self.Vehicle_type = V_type
        self.Option= option1
        self.RPM_MAX = rpm_max
        self.path_new = os.path.abspath(os.path.dirname(path_n[-1]))
    def run(self):
        self.job_starting.emit(0)
        self.Heatmap(self.path_new,self.Option,self.RPM_MAX)

    def Heatmap(self,path,option,rpm_max):
        if self.Vehicle_type == "4W":
            torque_max = option
            TORQUE_MAX = round(torque_max + 30)
        elif self.Vehicle_type == "3W":
            ARMS_max = option
            ARMS_MAX = round(ARMS_max + 50)
        file_path = path
        pcan_path = os.path.join(file_path, "pcan.csv")
        if not os.path.exists(pcan_path):
            print("pcan.csv doesnt exist in the current folder")
            self.job_failed.emit(0,"Unable to find pcan.csv for heatmap")
            return 
        df = pd.read_csv(pcan_path)
        RPM_MAX = round(rpm_max + 1500)
        if self.Vehicle_type == "4W":
            df_filtered = df[
                (df['TORQUE'] >= 10) & (df['TORQUE'] <= TORQUE_MAX) &
                (df['RPM'] >= 500) & (df['RPM'] <= RPM_MAX)
            ].copy()
            torque_bins = list(range(10, TORQUE_MAX, 10)) 
            df_filtered['Torque_Group'] = pd.cut(df_filtered['TORQUE'], bins=torque_bins, labels=torque_bins[:-1], include_lowest=True)
            index_grp_name = "Torque_Group"
        elif self.Vehicle_type == "3W":
            df_filtered = df[
                (df['ARMS'] >= 25) & (df['ARMS'] <= ARMS_MAX) &
                (df['RPM'] >= 500) & (df['RPM'] <= RPM_MAX)
            ].copy()
            ARMS_bins = list(range(25, ARMS_MAX, 25))  
            df_filtered['ARMS_Group'] = pd.cut(df_filtered['ARMS'], bins=ARMS_bins, labels=ARMS_bins[:-1], include_lowest=True)
            index_grp_name = "ARMS_Group"
        rpm_bins = list(range(500, RPM_MAX, 500))    
        # Bin data
        df_filtered['RPM_Group'] = pd.cut(df_filtered['RPM'], bins=rpm_bins, labels=rpm_bins[:-1], include_lowest=True)
        
        # Create pivot table as percentages
        total_points = len(df_filtered)
        percent_table = pd.pivot_table(
            df_filtered,
            values='RPM',
            index=index_grp_name,
            columns='RPM_Group',
            aggfunc='count',
            fill_value=0
        )
        percent_table = (percent_table / total_points) * 100
        percent_table = percent_table.round(1)

        # Annotate only non-zero values
        annot = percent_table.map(lambda x: f"{x:.1f}" if x > 0 else '')

        # Mask zero values
        mask = percent_table == 0

        # Custom black-to-orange colormap
        black_orange = LinearSegmentedColormap.from_list(
            'black_orange', ['black', '#ff5500', '#ffcc00']
        )

        # Plot heatmap
        plt.figure(figsize=(8, 6))
        ax = sns.heatmap(
            percent_table,
            annot=annot,
            fmt='',
            cmap=black_orange,
            mask=mask,
            linewidths=0,
            linecolor='white',
            cbar=True,
            cbar_kws={'label': 'Instance Percentage (%)'}
        )

        # Title and axis labels
        if self.Vehicle_type == "4W":
            plt.title('Torque vs RPM Efficiency Map (Percentage)', fontsize=14, fontweight='bold')
            plt.ylabel('Torque (N.m)', fontsize=12, fontweight='bold')
            ax.set_yticks(np.arange(len(torque_bins) - 1))
            ax.set_yticklabels([str(x) for x in torque_bins[:-1]], rotation=0)
        elif self.Vehicle_type == "3W":
            plt.title('ARMS vs RPM Efficiency Map (Percentage)', fontsize=14, fontweight='bold')
            plt.ylabel('ARMS (A)', fontsize=12, fontweight='bold')
            ax.set_yticks(np.arange(len(ARMS_bins) - 1))
            ax.set_yticklabels([str(x) for x in ARMS_bins[:-1]], rotation=0)
        plt.xlabel('RPM', fontsize=12, fontweight='bold')

        # Tick marks aligned with bin edges
        ax.set_xticks(np.arange(len(rpm_bins) - 1))
        ax.set_xticklabels([str(x) for x in rpm_bins[:-1]], rotation=0)

        
        date = str("dd/mm/yy")

        # Torque increases from bottom to top
        ax.invert_yaxis()

        # plt.tight_layout()
        # safe_date = re.sub(r'[\\/:"*?<>|]+', "_", date)
        # filename = f"{safe_date}_heatmap.png"
        # plt.savefig(filename, dpi=300, bbox_inches="tight")
        # print(f"Plot saved as {filename}")
        # self.job_completed.emit(0)
        plt.tight_layout()

        # 1. Clean the date string for filenames
        safe_date = re.sub(r'[\\/:"*?<>|]+', "_", date)
        filename = f"{safe_date}_heatmap.png"

        # 2. Create the FULL path to the destination folder
        # This ensures the image goes into the same folder as pcan.csv
        save_destination = os.path.join(file_path, filename)

        # 3. Save using the full path
        plt.savefig(save_destination, dpi=300, bbox_inches="tight")

        print(f"Plot saved as {save_destination}")
        self.job_completed.emit(0)