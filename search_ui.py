# search_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scanner import scan_files
from logic import add_scanned_files


def open_search_window(parent, on_files_added=None):
    win = tk.Toplevel(parent)
    win.title("🔍 Search Files on System")
    win.geometry("800x500")
    win.transient(parent)
    win.grab_set()

    # --- Search controls ---
    top = ttk.Frame(win, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="File name contains:").pack(side="left")
    name_var = tk.StringVar()
    ttk.Entry(top, textvariable=name_var, width=30).pack(side="left", padx=5)

    ttk.Label(top, text="Type:").pack(side="left", padx=(15, 0))
    type_var = tk.StringVar(value="ALL")
    ttk.Combobox(
        top,
        textvariable=type_var,
        values=["ALL", "PDF", "DOCX", "XLSX"],
        state="readonly",
        width=8
    ).pack(side="left", padx=5)

    ttk.Button(top, text="Start Search", command=lambda: start_search())\
        .pack(side="left", padx=10)

    # --- Results table ---
    cols = ("Name", "Type", "Path")
    tree = ttk.Treeview(win, columns=cols, show="headings", selectmode="extended")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="w")
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    status = tk.StringVar(value="Ready")
    ttk.Label(win, textvariable=status).pack(anchor="w", padx=10)

    def start_search():
        tree.delete(*tree.get_children())
        status.set("Searching...")

        def task():
            results = scan_files(
                name_part=name_var.get(),
                file_type=type_var.get()
            )
            win.after(0, lambda: show_results(results))

        threading.Thread(target=task, daemon=True).start()

    def show_results(results):
        for r in results:
            tree.insert("", "end", values=(r["name"], r["ext"], r["path"]))
        status.set(f"Found {len(results)} file(s)")

    def add_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select files to add")
            return

        files = []
        for item in selected:
            vals = tree.item(item)["values"]
            files.append({
                "path": vals[2],
                "ext": vals[1]
            })

        add_scanned_files(files)

        if on_files_added:
            on_files_added()

        messagebox.showinfo("Done", "Selected files added to Document Manager")


    ttk.Button(win, text="➕ Add Selected to Manager", command=add_selected)\
        .pack(pady=10)
