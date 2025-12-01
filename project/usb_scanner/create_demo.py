import os
import sqlite3
from pathlib import Path

from scanner.scanner import scan_drive

DEMO_DIR = Path("demo_usb")

def prepare_demo():
    demo = DEMO_DIR
    demo.mkdir(exist_ok=True)

    (demo / "good.txt").write_text("This is a harmless text file.\n", encoding="utf-8")

    (demo / "fake_installer.exe").write_text("Fake installer - this is just text, not a real exe.\n", encoding="utf-8")

    (demo / "autorun.inf").write_text("[Autorun]\nopen=fake_installer.exe\n", encoding="utf-8")

    (demo / "script.vbs").write_text("MsgBox \"Hello from demo VBS\"\n", encoding="utf-8")

    random_bytes = bytes([i % 256 for i in range(200000)])  # ~200KB
    with open(demo / "packed_like.exe", "wb") as fh:
        fh.write(random_bytes)

    print(f"[+] Demo folder created at: {demo.resolve()}")


def show_db_preview(limit=20):
    db_path = "scanner.db"
    if not os.path.exists(db_path):
        print("[!] scanner.db not found. Run the scanner first to populate the DB.")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, triggered_rules, is_pe, entropy, pe_timestamp, pe_imports, timestamp FROM scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    print("\n--- DB preview (last results) ---")
    for r in rows:
        print(r)
    conn.close()

if __name__ == "__main__":
    prepare_demo()
    scan_drive(str(DEMO_DIR))
    show_db_preview()