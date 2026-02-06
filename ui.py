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
        self.setup_style()

        self.build_top_bar()
        self.build_table()
        self.build_buttons()

        self.refresh()

    def setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            rowheight=26,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=6
        )

        style.configure(
            "TLabel",
            font=("Segoe UI", 10)
        )


    def edit_description(self):
        item = self.tree.focus()
        if not item:
            return

        values = self.tree.item(item)["values"]
        doc_id = values[0]
        current_desc = values[3]
        current_tags = values[4]

        popup = tk.Toplevel(self.root)
        popup.title("Edit Document Details")
        popup.geometry("420x220")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text="Description").pack(anchor="w", padx=15, pady=(10, 0))
        desc_var = tk.StringVar(value=current_desc)
        ttk.Entry(popup, textvariable=desc_var, width=50).pack(padx=15)

        ttk.Label(popup, text="Tags (comma separated)").pack(anchor="w", padx=15, pady=(10, 0))
        tags_var = tk.StringVar(value=current_tags)
        ttk.Entry(popup, textvariable=tags_var, width=50).pack(padx=15)

        def save():
            from logic import save_document_details

            if save_document_details(doc_id, desc_var.get(), tags_var.get()):
                popup.destroy()
                self.refresh()


        ttk.Button(popup, text="Save", command=save).pack(pady=15)


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

    def on_double_click(self, event):
        self.edit_description()


    def build_table(self):
        cols = ("ID", "Name", "Type", "Description", "Tags")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10)
        self.tree.bind("<Double-1>", self.on_double_click)


    def build_buttons(self):
        bar = ttk.Frame(self.root, padding=10)
        bar.pack()

        ttk.Button(bar, text="➕ Add", command=self.add)\
            .pack(side="left", padx=5)
        ttk.Button(bar, text="📂 Open", command=self.open_selected)\
            .pack(side="left", padx=5)
        ttk.Button(bar, text="✏ Edit Description", command=self.edit_description)\
            .pack(side="left", padx=5)
        ttk.Button(bar, text="🗑 Remove", command=self.remove_selected)\
            .pack(side="left", padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        rows = fetch_documents(
            self.search_var.get(),
            self.type_var.get(),
            self.search_var.get()
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
        item = self.tree.item(item)["values"]
        file_path = item[-1] if len(item) > 5 else None


    def remove_selected(self):
        item = self.tree.focus()
        if not item:
            return
        doc_id = self.tree.item(item)["values"][0]
        remove_file(doc_id)
        self.refresh()
