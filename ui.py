# ui.py
import tkinter as tk
from tkinter import ttk
from db import fetch_documents
from logic import choose_and_add, open_file, remove_file

class DocumentManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📁 Document Manager")
        self.root.geometry("900x500")

        self.build_top_bar()
        self.build_table()
        self.build_buttons()

        self.refresh()

    def build_top_bar(self):
        bar = ttk.Frame(self.root, padding=10)
        bar.pack(fill="x")

        self.search_var = tk.StringVar()
        self.type_var = tk.StringVar(value="ALL")

        ttk.Entry(bar, textvariable=self.search_var, width=40)\
            .pack(side="left", padx=5)
        ttk.Combobox(
            bar,
            textvariable=self.type_var,
            values=["ALL", ".pdf", ".docx", ".xlsx"],
            width=10,
            state="readonly"
        ).pack(side="left", padx=5)

        ttk.Button(bar, text="Search", command=self.refresh)\
            .pack(side="left", padx=5)

    def build_table(self):
        cols = ("ID", "Name", "Type", "Description")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10)

    def build_buttons(self):
        bar = ttk.Frame(self.root, padding=10)
        bar.pack()

        ttk.Button(bar, text="➕ Add", command=self.add)\
            .pack(side="left", padx=5)
        ttk.Button(bar, text="📂 Open", command=self.open_selected)\
            .pack(side="left", padx=5)
        ttk.Button(bar, text="🗑 Remove", command=self.remove_selected)\
            .pack(side="left", padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        rows = fetch_documents(
            self.search_var.get(),
            self.type_var.get()
        )
        for r in rows:
            self.tree.insert("", "end", values=r[:-1])

    def add(self):
        if choose_and_add(""):
            self.refresh()

    def open_selected(self):
        item = self.tree.focus()
        if not item:
            return
        doc_id = self.tree.item(item)["values"][0]
        rows = fetch_documents()
        for r in rows:
            if r[0] == doc_id:
                open_file(r[4])

    def remove_selected(self):
        item = self.tree.focus()
        if not item:
            return
        doc_id = self.tree.item(item)["values"][0]
        remove_file(doc_id)
        self.refresh()
