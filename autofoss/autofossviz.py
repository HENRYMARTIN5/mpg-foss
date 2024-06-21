import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import threading
import plotters

def pick_file(type="csv"):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[(f"{type.upper()} files", f"*.{type}")])
    return file_path

loadbox_window = None
def show_loadbox(msg):
    global loadbox_window
    loadbox_window = tk.Tk()
    loadbox_window.resizable(False, False)
    loadbox_window.protocol("WM_DELETE_WINDOW", lambda: None)
    loadbox_window.title("Loading")
    tk.Label(loadbox_window, text=msg).pack()
    loadbox_window.mainloop()

def open_loadbox(msg: str):
    threading.Thread(target=show_loadbox, args=(msg,), daemon=True).start()

def close_loadbox():
    global loadbox_window
    if loadbox_window:
        loadbox_window.after(0, loadbox_window.destroy)
        loadbox_window = None

def main() -> int:
    file_path = pick_file()
    if not file_path:
        print("No file selected.")
        return 1
    open_loadbox("Loading CSV...")
    df = pd.read_csv(file_path)
    print(df)
    close_loadbox()

    prompt_window = tk.Tk()
    prompt_window.title("Select Viz Type")
    prompt_window.geometry("200x100")
    selected_plotter = None
    def on_submit():
        nonlocal selected_plotter
        selected_plotter = plotters.ALL_PLOTTERS[plot_type_var.get()]
        prompt_window.quit()
    tk.Label(prompt_window, text="Select Viz Type").pack()
    plot_type_var = tk.StringVar(prompt_window)
    plot_type_var.set("Weight Over Time")
    tk.OptionMenu(prompt_window, plot_type_var, *plotters.ALL_PLOTTERS.keys()).pack()
    tk.Button(prompt_window, text="Submit", command=on_submit).pack()
    prompt_window.mainloop()
    prompt_window.destroy()
    
    plotter = selected_plotter(df)
    plotter.plot()
    plotter.show()
    return 0

if __name__ == "__main__":
    exit(main())