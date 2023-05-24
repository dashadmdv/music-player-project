import tkinter as tk
from tkinter.filedialog import askdirectory


def select_path():
    window = tk.Tk()
    window.wm_attributes("-topmost", 1)
    window.withdraw()
    path = askdirectory(
        parent=window, title="Select folder", initialdir="C:", mustexist=True
    )
    return path
