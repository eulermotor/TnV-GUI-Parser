# Vehicle Data Parser & Summary Tool

Welcome to the internal Vehicle Data Parser and Summary Tool repository. This application is designed to parse vehicle TRC files, apply specific Database Container (DBC) files, and generate analytical heatmaps and summary tables for Euler Motors vehicles.

---

## 📋 Prerequisites & Access Control

Before running the application, ensure you meet the following access requirements:

* **Authentication:** You **must** use your official company email ID to log in and use the application.
* **Google Sheets Integration (Optional - Only required if you are working on TnV vehicles and want to upload summary):**
    * Before uploading summary data, click the **Connect** button located in the top-right corner to verify your permissions.
    * Navigating back to the *Home* page or *Vehicle Type* page will reset this connection, requiring you to reconnect.
    * **3W SpreadSheet:** [Click here to view](https://docs.google.com/spreadsheets/d/1TiTbPuTobJOnAO3HbH15xKbTO--J9yP-WsawDKNM0q4/edit?usp=sharing)
    * **4W SpreadSheet:** [Click here to view](https://docs.google.com/spreadsheets/d/1L6W5pay9hMtc22DRUZa4-1KNsMNEjhmd48XSKd4CPQ8/edit?usp=sharing)
* **Access Permissions:** If you encounter connection issues or lack upload permissions, please contact **vinayak.kushwah@eulermotors.com** for authorization.

---

## 🛠 Supported Vehicles & DBC Configurations for heatmap, summary and summary table

The heatmap and summary table generation features currently support a specific subset of vehicle configurations. 

| Vehicle Category | Supported DBC Cases | Limitations / Notes |
| :--- | :--- | :--- |
| **4-Wheeler (4W)** | 1. Vehicle Testing Marvel<br>2. Vehicle Testing NBMS | **DO NOT** use the 4W Stark-specific DBC, as it is currently non-functional. |
| **3-Wheeler (3W)** | 1. GTAKE (4 cases)<br>2. Pegasus (3 cases) | Fully optimized for these 7 specific cases. |

> ⚠️ **Important:** Heatmap and summary table generation will *only* work for the specific 4W and 3W cases listed above. 

---

## 📑 File Handling & Operational Guidelines

To prevent parsing errors or data corruption, please strictly adhere to the following file management rules:

### 1. Active File Restraints
* **DO NOT** run the application on any TRC files that are currently open on your PC.
* If you are utilizing an external DBC file, ensure it is completely closed before initiating the process.

### 2. Multi-Part TRC Files
If your log data spans across multiple TRC files, you must rename them sequentially using the word **"part"** (case-insensitive) followed immediately by the sequence number.
* *Correct Examples:* `data part 1.trc`, `LOG PART 2.trc`, `trip part 10.trc`

### 3. Directory Cleanliness
Before starting a new parsing sequence, verify that your target folder does **not** contain:
* `pcan.csv`
* Any files ending in `pcan_part (number)` 

If these files are present, the application will falsely identify them as already parsed and skip the process.

---

## 🚀 Roadmap & Future Releases

We are actively working to expand the capabilities of this tool. The following features are locked for the next release:

* **Version 2.0 Functionalities:** Full implementation of the **File**, **Setting**, and **Help** menus.
* **Feature Requests:** Additional pipeline requirements submitted by the 3W and 4W testing teams are being cataloged and will be integrated into the next version.

---

*For technical support, bugs, or feature contributions, please reach out to the internal diagnostics team or contact the permissions administrator listed above.*
