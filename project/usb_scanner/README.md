# Automated USB Security Scanner

A Python-based tool that automatically scans USB drives for potential malware indicators using hashing, entropy analysis, PE parsing, and heuristic detection.

The scanner never executes files — it only analyzes them safely.

---

# Project Summary

### This project implements a lightweight USB security scanner.
When a USB device is connected, the scanner:
- Detects the new removable drive
- Recursively scans all files on it
- Flags suspicious files based on:
- Executable extensions (.exe, .dll, .bat, .vbs, .lnk, etc.)
- PE (Portable Executable) metadata using pefile
- High entropy detection (common in malware packing/obfuscation)
- Autorun.inf presence
- Suspicious file placement (e.g., EXE inside root directory)
- Stores results into a local SQLite database (scanner.db)
- Prints warnings in the console

### This scanner provides a safe introduction to USB malware detection without attempting real-time antivirus behavior.

---

# Project Structure

```
usb_scanner/
│
├── starter_scanner.py         # Entry point that starts the watcher
├── create_demo.py             # Demo dataset + run scanner
│
├── scanner/
│   ├── watcher.py             # Detects removable drives (Phase 1)
│   ├── scanner.py             # File scanning logic (hash, entropy, PE)
│   ├── rules.py               # Suspicious rules + entropy function
│   ├── db.py                  # SQLite DB logic
│
├── demo_usb/                  # Auto-created demo USB folder
│
├── requirements.txt
└── README.md   <— (this file)
```


---

# Installation & Environment Setup

### 1. Clone the project
```
git clone <repo_url>
cd usb_scanner
```
### 2. Create and activate a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```
### 3. Install dependencies
```
pip install -r requirements.txt
```
---

# How to Run the Scanner

### Run normally:
```
python starter_scanner.py
```
This will start the USB watcher. When a USB drive is connected:
-	It detects the new mountpoint
-	Calls the scanner
-	Outputs warnings
-	Saves results to scanner.db

---

# How to Test with a Demo Folder (no USB needed)

### I provided a demo script that generates a folder mimicking a USB drive.

1. Create demo files + run scanner:
```
python create_demo.py
```
This will:
-	Generate folder demo_usb/ containing:
-	good.txt
-	fake_installer.exe
-	autorun.inf
-	script.vbs
-	packed_like.exe (high-entropy data)
-	Run the scanner against it
-	Print detected warnings
-	Insert results into scanner.db
-	Print a database preview

---

# Inspecting the Database

### Quick 1-liner:
```
python - <<'PY' 
import sqlite3
conn = sqlite3.connect("scanner.db")
for row in conn.execute("SELECT id, filename, triggered_rules, is_pe, entropy, timestamp FROM scans ORDER BY id DESC"):
    print(row)
conn.close()
PY
```

---

# Design Choices & Limitations

### 1. Safety First (No Execution)
- scanner never executes any file, even suspicious ones.
- It only reads bytes safely and computes metadata.

### 2. Lightweight Malware Indicators

This is not full antivirus software.
It uses indicators such as:
- Entropy > threshold
- Suspicious extensions
- PE header metadata
- Autorun.inf
- Suspicious directory placement

These heuristics are not as powerful as real malware engines but demonstrate real-world detection concepts.

### 3. Local SQLite Storage

Scan results are stored in:

scanner.db

---

# Conclusion

This USB Security Scanner is a fully working, safe, and tool that demonstrates:
-	USB detection
-	File system analysis
-	Hashing
-	Entropy-based threat indication
-	PE parsing
-	Security heuristics
-	Database logging

---

# Video Presentation 

### https://www.youtube.com/watch?v=68CTwEHeicI