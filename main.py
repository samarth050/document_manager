# main.py
import tkinter as tk
from db import init_db
from ui import DocumentManagerUI

init_db()

root = tk.Tk()
DocumentManagerUI(root)
root.mainloop()
