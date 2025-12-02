import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import webbrowser

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
TOOLKIT_PATH = "/Users/clevyyy/Documents/overleaf-toolkit"
CONTAINERS = ["sharelatex", "mongo", "redis"]

# ----------------------------------------------------
# DOCKER STATUS CHECK
# ----------------------------------------------------
def get_container_status(container):
    try:
        result = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.State.Status}}", container],
            stderr=subprocess.STDOUT
        ).decode().strip()

        if result == "running":
            return "green"
        elif result in ("created", "restarting", "starting"):
            return "orange"
        else:
            return "red"
    except subprocess.CalledProcessError:
        return "red"

# ----------------------------------------------------
# UPDATE LIGHTS
# ----------------------------------------------------
def update_lights():
    while True:
        for container, label in container_labels.items():
            color = get_container_status(container)
            label.config(bg=color)
        time.sleep(2)

# ----------------------------------------------------
# RUN COMMAND WITH LOG CAPTURE
# ----------------------------------------------------
def run_command(command):
    process = subprocess.Popen(
        command,
        cwd=TOOLKIT_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:
        console.insert(tk.END, line)
        console.see(tk.END)

    process.wait()

def start_overleaf():
    console.insert(tk.END, "\n=== Starting Overleaf... ===\n")
    threading.Thread(target=run_command, args=(["bin/up"],), daemon=True).start()

def stop_overleaf():
    console.insert(tk.END, "\n=== Stopping Overleaf... ===\n")
    threading.Thread(target=run_command, args=(["bin/stop"],), daemon=True).start()

# ----------------------------------------------------
# AUTO STOP WHEN WINDOW CLOSES
# ----------------------------------------------------
def on_close():
    console.insert(tk.END, "\n=== Fenêtre fermée : arrêt d'Overleaf... ===\n")
    threading.Thread(target=run_command, args=(["bin/stop"],), daemon=True).start()
    root.after(1500, root.destroy)

# ----------------------------------------------------
# OPEN OVERLEAF IN BROWSER
# ----------------------------------------------------
def open_overleaf():
    webbrowser.open("http://localhost:80")

# ----------------------------------------------------
# UI SETUP
# ----------------------------------------------------
root = tk.Tk()
root.title("Overleaf Control Panel")
root.geometry("550x500")

title = tk.Label(root, text="Overleaf Local Manager", font=("Helvetica", 18))
title.pack(pady=10)

# ----------------------------------------------------
# LIGHTS PANEL
# ----------------------------------------------------
panel = tk.Frame(root)
panel.pack(pady=5)

container_labels = {}

for name in CONTAINERS:
    frame = tk.Frame(panel)
    frame.pack(side=tk.LEFT, padx=15)

    tk.Label(frame, text=name.capitalize()).pack()
    light = tk.Label(frame, width=4, height=2, bg="red", relief="sunken")
    light.pack(pady=5)

    container_labels[name] = light

# ----------------------------------------------------
# BUTTONS
# ----------------------------------------------------
buttons = tk.Frame(root)
buttons.pack(pady=10)

btn_start = tk.Button(buttons, text="🟢 Start", width=15, command=start_overleaf)
btn_start.grid(row=0, column=0, padx=10)

btn_stop = tk.Button(buttons, text="🟥 Stop", width=15, command=stop_overleaf)
btn_stop.grid(row=0, column=1, padx=10)

btn_open = tk.Button(buttons, text="🌐 Ouvrir Overleaf", width=18, command=open_overleaf)
btn_open.grid(row=0, column=2, padx=10)

# ----------------------------------------------------
# CONSOLE LOG WINDOW
# ----------------------------------------------------
console_label = tk.Label(root, text="Console logs:")
console_label.pack()

console = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
console.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ----------------------------------------------------
# START LIGHT THREAD
# ----------------------------------------------------
threading.Thread(target=update_lights, daemon=True).start()

# ----------------------------------------------------
# HANDLE CLOSE WINDOW
# ----------------------------------------------------
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
