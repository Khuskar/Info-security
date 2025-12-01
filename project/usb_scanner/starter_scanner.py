from scanner.watcher import start_watch
from scanner.scanner import scan_drive

def on_new_mount(mountpoint: str):
    scan_drive(mountpoint)

def main():
    print("[*] USB Security Scanner started...")
    print("[*] Waiting for USB device insertion...")
    start_watch(on_new_mount=on_new_mount, poll_interval=2.0)

if __name__ == "__main__":
    main()