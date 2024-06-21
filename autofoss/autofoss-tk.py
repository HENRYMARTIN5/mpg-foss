"""
Script to automatically take full recordings of drains - GUI version.

Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Procedure:
1. Ensure the Gator, power supply, and scale are connected and turned on.
2. Run this script.
3. This script will automatically start everything neccesary to record data, and will refill the tank as needed. You shouldn't need to do anything.
4. You can stop the script at the next cycle gracefully by pressing CTRL+C. If you want to stop the script immediately, press CTRL+C a second time.
"""

import scale
import gator
import power
import refill
from csv_util import write_csv
import customtkinter
import tkinter as tk
from tkinter import filedialog as tkFileDialog
import threading

class AutofossApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoFOSS")
        self.geometry("400x400")
        self.grid_columnconfigure((0, 1), weight=1)

        self.outfolder = "."

        self.button = customtkinter.CTkButton(self, text="Start", command=self.start)
        self.button.grid(row=0, column=0, padx=20, pady=5, sticky="ew", columnspan=2)
        self.scale_output = customtkinter.CTkTextbox(self, height=1, width=20)
        self.scale_output.grid(row=2, column=0, padx=20, pady=5, sticky="ew", columnspan=2)
        self.scale_output.insert(tk.END, "Scale output will appear here.")
        self.scale_output.configure(state="disabled")
        self.status_label = customtkinter.CTkLabel(self, text="Status: Not running")
        self.status_label.grid(row=3, column=0, padx=20, pady=5, sticky="ew", columnspan=2)
        # self.status_bar = customtkinter.CTkProgressBar(self)
        # self.status_bar.grid(row=1, column=0, padx=20, pady=5, sticky="ew", columnspan=2)
        self.folder_select = customtkinter.CTkButton(self, text="Select output folder", command=self.select_folder)
        self.folder_select.grid(row=4, column=0, padx=20, pady=5, sticky="ew", columnspan=2)
        self.folder_label = customtkinter.CTkLabel(self, text="Output folder: ./")
        self.folder_label.grid(row=5, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

    def select_folder(self):
        folder = tkFileDialog.askdirectory()
        self.folder_label.configure(text=f"Output folder: {folder}")
        self.outfolder = folder

    def start(self):
        pass


def main() -> int:
    """
Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Procedure for use:
1. Ensure the Gator, power supply, and scale are connected and turned on.
2. Run this script.
3. This script will automatically start everything neccesary to record data, and will refill the tank as needed. You shouldn't need to do anything.
4. You can stop the script at the next cycle gracefully by pressing CTRL+C. If you want to stop the script immediately, press CTRL+C a second time.
    """

    if args.log_gator:
        print("WARNING: Don't be an idiot and read this!")
        print("Logging Gator data to the console will kill performance and make the script run slower than a snail on a salt flat. You have been warned.")
        print("This feature should only *ever* be used for debugging purposes. If you're not debugging, turn it off.")
        yn = input("Do you really, actually, seriously want to continue? [y/N] ")
        if yn.lower() != 'y':
            return 1

    components = {}
    components['scale'] = scale.AutofossScale(components, log_scale=not args.no_log_scale, default_port=args.scale_port)
    components['gator'] = gator.AutofossGator(components, auto_end=True, log_gator=args.log_gator)
    components['power'] = power.AutofossPowersupply(components, address=args.power_port) # NOTE: no start() or stop() methods
    components['refill'] = refill.AutofossRefiller(components, threshold=args.bucket_weight)

    running = True
    interrupted = False
    force_shutdown = False
    while running:
        if not interrupted:
            components['gator'].start()
            components['scale'].start()
        try:
            while components['scale'].thread_running:
                pass
        except KeyboardInterrupt:
            print("Interrupted!")
            if not interrupted:
                print("Press CTRL+C again to force shutdown. This script will sto gracefully after this drain.")
                interrupted = True
                continue
            print("Forcing shutdown...")
            force_shutdown = True
        print("Shutting down...")
        components['gator'].stop()
        components['scale'].stop()
        if force_shutdown:
            components['power'].stop()
            return 128 # SIGINT
        print('Everything is off. Writing samples to CSV...')
        file_name = write_csv(components['gator'].samples)
        print(f'CSV file written: {file_name}')
        if not interrupted:
            print('Refilling tank...')
            components['refill'].start()
            res = components['refill'].wait_for_refill()
            if not res:
                print("Refill failed! Pausing for human intervention. Press ENTER to continue.")
                input()
            print('Tank refilled.')
            print('Resetting components...')
            for component in components.values():
                components[component].reset()
            print('And now, again!')
        else:
            running = False
            break # really neccesary? probably not
    return 0

if __name__ == '__main__':
    app = AutofossApp()
    app.mainloop()