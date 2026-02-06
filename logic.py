# logic.py
import os
from tkinter import filedialog, messagebox
from db import insert_document, delete_document

SUPPORTED_TYPES = [".pdf", ".docx", ".xlsx"]

def choose_and_add(description):
    path = filedialog.askopenfilename(
        filetypes=[("Documents", "*.pdf *.docx *.xlsx")]
    )
    if not path:
        return False

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_TYPES:
        messagebox.showerror("Invalid file", "Unsupported file type")
        return False

    try:
        insert_document(
            os.path.basename(path),
            path,
            ext,
            description
        )
        return True
    except Exception:
        messagebox.showerror("Error", "File already exists")
        return False

def open_file(path):
    if os.path.exists(path):
        os.startfile(path)
    else:
        messagebox.showerror("Error", "File not found")

def remove_file(doc_id):
    delete_document(doc_id)
