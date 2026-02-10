# scanner.py
import os
import string

SUPPORTED_EXTENSIONS = {
    "PDF": (".pdf",),
    "DOCX": (".docx",),
    "XLSX": (".xlsx",),
    "ALL": (".pdf", ".docx", ".xlsx")
}

def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            drives.append(path)
    return drives


def scan_files(name_part="", file_type="ALL", max_results=2000):
    matches = []
    name_part = name_part.lower()
    extensions = SUPPORTED_EXTENSIONS[file_type]

    for drive in get_available_drives():
        for root, _, files in os.walk(drive):
            # skip dangerous / useless folders
            if root.lower().startswith(("c:\\windows", "c:\\program files")):
                continue

            for fname in files:
                if name_part and name_part not in fname.lower():
                    continue

                if not fname.lower().endswith(extensions):
                    continue

                full_path = os.path.join(root, fname)

                matches.append({
                    "name": fname,
                    "path": full_path,
                    "ext": os.path.splitext(fname)[1]
                })

                if len(matches) >= max_results:
                    return matches

    return matches
