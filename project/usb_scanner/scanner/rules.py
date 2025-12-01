from math import log2
import os
import re

SUSPICIOUS_EXTS = {
    '.exe', '.dll', '.scr', '.msi', '.bat', '.cmd',
    '.vbs', '.js', '.ps1', '.lnk', '.pif'
}

EXEC_EXTS = {'.exe', '.dll', '.scr', '.msi', '.pif'}

AUTORUN_NAMES = {'autorun.inf', 'Autorun.inf'}

DEFAULT_ENTROPY_THRESHOLD = 7.5

LNK_ROOT_THRESHOLD = 3
DIR_NAME_LENGTH_THRESHOLD = 20
HEX_DIR_REGEX = re.compile(r'^[0-9a-fA-F]{8,}$')

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    entropy = 0.0
    length = len(data)
    for c in counts:
        if c == 0:
            continue
        p = c / length
        entropy -= p * log2(p)
    return entropy

def entropy_of_file(path: str, max_bytes: int = 1024 * 1024) -> float:
    try:
        with open(path, 'rb') as fh:
            data = fh.read(max_bytes)
            return shannon_entropy(data)
    except Exception:
        return 0.0

def is_root_file(mountpoint: str, filepath: str) -> bool:
    mp = os.path.normpath(mountpoint)
    fp = os.path.normpath(filepath)

    parent = os.path.dirname(fp)
    return os.path.normpath(parent) == mp

def count_files_in_root_with_ext(mountpoint: str, ext: str) -> int:

    try:
        cnt = 0
        for entry in os.scandir(mountpoint):
            if entry.is_file():
                if os.path.splitext(entry.name)[1].lower() == ext:
                    cnt += 1
        return cnt
    except Exception:
        return 0

def is_odd_dir_name(segment: str) -> bool:

    if not segment:
        return False
    if len(segment) >= DIR_NAME_LENGTH_THRESHOLD:
        return True
    if HEX_DIR_REGEX.match(segment):
        return True
    return False

def any_odd_dir_in_path(relpath: str) -> bool:

    parts = relpath.split(os.sep)
    if len(parts) <= 1:
        return False
    dir_segments = parts[:-1]
    for seg in dir_segments:
        if is_odd_dir_name(seg):
            return True
    return False