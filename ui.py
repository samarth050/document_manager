# ui.py
import json
import os
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
        self.root.bind("<Return>", lambda e: self.open_selected())
        self.root.bind("<Delete>", lambda e: self.remove_selected())
        self.root.bind("<Control-e>", lambda e: self.edit_description())
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Escape>", lambda e: self.clear_search())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def focus_search(self):
        self.search_entry.focus()

    def clear_search(self):
        self.search_var.set("")
        self.type_var.set("ALL")
        self.refresh()


    def on_close(self):
        self.save_column_widths()
        self.root.destroy()

    def on_search_change(self, event=None):
        self.refresh()

    def load_column_widths(self):
        if not os.path.exists("ui_state.json"):
            return

        with open("ui_state.json", "r") as f:
            data = json.load(f)

        for col, width in data.get("columns", {}).items():
            if col in self.tree["columns"]:
                self.tree.column(col, width=width)


    def save_column_widths(self):
        data = {
            "columns": {
                col: self.tree.column(col)["width"]
                for col in self.tree["columns"]
            }
        }
        with open("ui_state.json", "w") as f:
            json.dump(data, f)


    def sort_column(self, col, reverse):
        data = [
            (self.tree.set(k, col), k)
            for k in self.tree.get_children("")
        ]

        # numeric sort for ID
        if col == "ID":
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        else:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)

        # toggle sort direction on next click
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


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

    def open_search(self):
        from search_ui import open_search_window

        def on_files_added():
            self.search_var.set("")      # clear live search
            self.type_var.set("ALL")     # reset filter
            self.refresh()

        open_search_window(self.root, on_files_added=on_files_added)

    def build_top_bar(self):
        bar = ttk.Frame(self.root, padding=10)
        bar.pack(fill="x")

        self.search_var = tk.StringVar()
        self.type_var = tk.StringVar(value="ALL")

        self.search_entry = ttk.Entry(
            bar,
            textvariable=self.search_var,
            width=40
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        type_combo = ttk.Combobox(
            bar,
            textvariable=self.type_var,
            values=["ALL", ".pdf", ".docx", ".xlsx"],
            width=10,
            state="readonly"
        )
        type_combo.pack(side="left", padx=5)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        ttk.Button(
            bar,
            text="🔍 Search System",
            command=self.open_search
        ).pack(side="left", padx=5)


    def on_double_click(self, event):
        self.edit_description()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.tk_popup(event.x_root, event.y_root)


    def build_table(self):
        cols = ("ID", "Name", "Type", "Description", "Tags")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")

        # ID – small, fixed
        for col in ("ID", "Name", "Type", "Description", "Tags"):
            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_column(c, False)
            )
        self.tree.column("ID", width=50, anchor="center", stretch=False)

        # Name – wide
        for col in ("ID", "Name", "Type", "Description", "Tags"):
            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_column(c, False)
            )
        self.tree.column("Name", width=220, anchor="w", stretch=True)

        # Type – small
        for col in ("ID", "Name", "Type", "Description", "Tags"):
            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_column(c, False)
            )
        self.tree.column("Type", width=70, anchor="center", stretch=False)

        # Description – medium
        for col in ("ID", "Name", "Type", "Description", "Tags"):
            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_column(c, False)
            )
        self.tree.column("Description", width=260, anchor="w", stretch=True)

        # Tags – visible and usable
        for col in ("ID", "Name", "Type", "Description", "Tags"):
            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_column(c, False)
            )
        self.tree.column("Tags", width=180, anchor="w", stretch=True)

        self.tree.pack(fill="both", expand=True, padx=10)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="📂 Open", command=self.open_selected)
        self.menu.add_command(label="✏ Edit Description", command=self.edit_description)
        self.menu.add_separator()
        self.menu.add_command(label="🗑 Remove", command=self.remove_selected)

        self.tree.bind("<Button-3>", self.show_context_menu)

        self.load_column_widths()





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
