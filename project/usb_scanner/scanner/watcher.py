import time
import os
import psutil
from typing import Callable, Optional, Set

def _find_candidate_mounts() -> Set[str]:
    mounts = psutil.disk_partitions(all=False)
    candidates = set()

    for p in mounts:
        mp = p.mountpoint
        opts = (p.opts or "").lower()

        if 'removable' in opts:
            candidates.add(mp)
            continue

        if os.name == 'nt':
            system_root = os.getenv('SystemDrive', 'C:\\').upper()
            if mp.upper() != system_root:
                candidates.add(mp)
        else:
            if mp.startswith('/media') or mp.startswith('/run/media') or mp.startswith('/Volumes'):
                candidates.add(mp)

    return candidates

def start_watch(on_new_mount: Optional[Callable[[str], None]] = None, poll_interval: float = 2.0):
    if on_new_mount is None:
        raise ValueError("on_new_mount callback is required.")

    known = _find_candidate_mounts()
    print(f"Watcher started. Known mounts: {known}")
    try:
        while True:
            current = _find_candidate_mounts()
            new = current - known
            removed = known - current

            for m in new:
                print(f"[+] New removable detected: {m}")
                try:
                    on_new_mount(m)
                except Exception as e:
                    print(f"    [!] Error in on_new_mount callback for {m}: {e}")

            for m in removed:
                print(f"[-] Removed: {m}")

            known = current
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("Watcher stopped by user (KeyboardInterrupt).")