import os
import sys
import threading
from tkinter import Tk, Label, Button, Frame, END
from tkinter import ttk
import subprocess

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.pack(pady=20)

        self.label = Label(self, text="Processes:")
        self.label.pack()

        self.text_area = Text(self, height=10, width=40)
        self.text_area.pack()

        self.button = Button(self, text="Start", command=self.start)
        self.button.pack()

    def start(self):
        self.button.config(state="disabled")

        # Get the number of cores
        num_cores = int(subprocess.check_output(["nproc"]).decode().strip())

        # Set the affinity value
        affinity_value = (1 << num_cores) - 2

        # Get the username
        username = subprocess.check_output(["whoami"]).decode().strip()

        # Get the list of processes
        process_list = subprocess.check_output(["tasklist", "/FI", f"USERNAME eq {username}"]).decode().strip().split("\n")

        # Create a set to store the process names
        process_set = set()

        # Parse the process list
        for process in process_list[2:]:
            process_name = process.split()[0]
            if process_name not in ["System Idle Process", "System"]:
                process_set.add(process_name)

        # Set the maximum value for the progress bar
        self.progress_bar["maximum"] = len(process_set)

        # Create a thread to update the progress bar
        threading.Thread(target=self.update_progress_bar, args=(process_set, affinity_value)).start()

    def update_progress_bar(self, process_set, affinity_value):
        for i, process in enumerate(process_set):
            # Update the progress bar
            self.progress_bar["value"] = i + 1
            self.progress_bar.update()

            # Update the text area
            self.text_area.insert(END, f"Setting affinity for {process}...\n")
            self.text_area.update()

            # Set the affinity
            subprocess.run(["powershell", f"ForEach ($PROCESS in GET-PROCESS {process}) {{ $PROCESS.ProcessAffinity={affinity_value} }}"])

        self.button.config(state="normal")

root = Tk()
app = Application(master=root)
app.mainloop()
