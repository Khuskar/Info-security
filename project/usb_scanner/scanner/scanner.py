import os
import hashlib
import traceback
import importlib.util

from .rules import (
    SUSPICIOUS_EXTS, AUTORUN_NAMES, entropy_of_file, DEFAULT_ENTROPY_THRESHOLD,
    EXEC_EXTS, is_root_file, count_files_in_root_with_ext, any_odd_dir_in_path
)
from . import db as dbmod

if importlib.util.find_spec("pefile") is not None:
    import pefile as pefile_module
else:
    pefile_module = None

_conn = None

def get_db_conn():
    global _conn
    if _conn is None:
        _conn = dbmod.init_db()
    return _conn


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def _is_pe_file_quick(path: str) -> bool:
    try:
        with open(path, 'rb') as f:
            sig = f.read(2)
            return sig == b'MZ'
    except Exception:
        return False

def _analyze_pe_with_pefile(path: str):
    if pefile_module is None:
        return None, 0

    try:
        pe = pefile_module.PE(path, fast_load=True)
        try:
            pe.parse_data_directories(directories=[pefile_module.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
        except Exception:
            pass

        ts = None
        try:
            ts = int(pe.FILE_HEADER.TimeDateStamp)
        except Exception:
            ts = None

        import_count = 0
        try:
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') and pe.DIRECTORY_ENTRY_IMPORT:
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    if hasattr(entry, 'imports') and entry.imports:
                        import_count += len(entry.imports)
        except Exception:
            import_count = 0

        try:
            pe.close()
        except Exception:
            pass

        return ts, import_count
    except Exception:
        return None, 0

def scan_drive(mountpoint: str, quarantine=False):

    conn = get_db_conn()
    print(f"[+] Scanning: {mountpoint}")

    try:
        lnk_root_count = count_files_in_root_with_ext(mountpoint, '.lnk')
        vbs_root_count = count_files_in_root_with_ext(mountpoint, '.vbs')
    except Exception:
        lnk_root_count = 0
        vbs_root_count = 0

    many_lnk_root = lnk_root_count >= 3

    for root, dirs, files in os.walk(mountpoint):
        for name in files:
            filepath = os.path.join(root, name)
            relpath = os.path.relpath(filepath, mountpoint)
            try:
                ext = os.path.splitext(name)[1].lower()
                triggered = []

                lname = name.lower()
                if lname in {n.lower() for n in AUTORUN_NAMES}:
                    triggered.append('autorun_file')
                    if is_root_file(mountpoint, filepath):
                        triggered.append('autorun_root')

                if ext in SUSPICIOUS_EXTS:
                    triggered.append('suspicious_extension')

                if ext in EXEC_EXTS and is_root_file(mountpoint, filepath):
                    triggered.append('exe_in_root')

                if many_lnk_root and ext == '.lnk' and is_root_file(mountpoint, filepath):
                    triggered.append('many_lnk_in_root')

                if ext == '.vbs' and is_root_file(mountpoint, filepath):
                    triggered.append('vbs_in_root')

                if any_odd_dir_in_path(relpath):
                    triggered.append('odd_dir_name')

                if triggered:
                    sha = None
                    size = None
                    try:
                        sha = sha256_of_file(filepath)
                    except Exception as e:
                        print(f"    [!] Failed to hash {filepath}: {e}")

                    try:
                        size = os.path.getsize(filepath)
                    except Exception:
                        size = None

                    is_pe = 0
                    pe_ts = None
                    pe_imports = 0

                    if pefile_module is not None:
                        try:
                            ts, imports_n = _analyze_pe_with_pefile(filepath)
                            if ts is not None or imports_n:
                                is_pe = 1
                                pe_ts = ts
                                pe_imports = imports_n
                            else:
                                is_pe = 1 if _is_pe_file_quick(filepath) else 0
                        except Exception:
                            is_pe = 1 if _is_pe_file_quick(filepath) else 0
                    else:
                        is_pe = 1 if _is_pe_file_quick(filepath) else 0

                    entropy = None
                    try:
                        entropy = entropy_of_file(filepath)
                        if entropy is not None and entropy >= DEFAULT_ENTROPY_THRESHOLD and 'high_entropy' not in triggered:
                            triggered.append('high_entropy')
                    except Exception:
                        pass

                    meta_notes = []
                    if pe_ts is not None:
                        meta_notes.append(f"pe_ts={pe_ts}")
                    if pe_imports:
                        meta_notes.append(f"pe_imports={pe_imports}")
                    meta_str = ";".join(meta_notes) if meta_notes else None

                    # Log to DB
                    triggered_str = ",".join(triggered) if triggered else ""
                    dbmod.insert_scan(conn, filepath, name, sha, size, triggered_str, is_pe, entropy, meta_str, pe_ts, pe_imports)

                    # Print warning in console
                    print(f"    [!] Suspicious: {relpath}")
                    print(f"        rules: {triggered_str}")
                    print(f"        sha256: {sha}")
                    print(f"        size: {size} bytes")
                    print(f"        is_pe: {is_pe}  pe_ts: {pe_ts}  pe_imports: {pe_imports}")
                    print(f"        entropy: {entropy}")

            except Exception:
                print(f"    [!] Error scanning file {filepath}")
                traceback.print_exc()