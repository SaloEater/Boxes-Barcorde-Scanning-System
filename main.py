import os
import datetime
import requests
from pynput import keyboard
import tkinter as tk
from tkinter import messagebox

# Global variables
last_logfile_path: str = ""
key_buffer = []
is_active = False  # Flag to control the handler
scanned_lines = set()  # Set to store scanned lines

def on_press(key):
    if not is_active:
        return  # Do nothing if not active
    try:
        if key == keyboard.Key.enter:
            line = ''.join(key_buffer)
            print("Line scanned:", line)
            if line in scanned_lines:
                print("Duplicate line, not sending.")
                key_buffer.clear()
                return
            scanned_lines.add(line)
            if last_logfile_path != "":
                with open(last_logfile_path, 'a') as logfile:
                    logfile.write(f"{line}\n")
            root.after(0, update_text_box, line)
            key_buffer.clear()

            # Make a POST request
            host = os.getenv('SYSTEM_HOST')
            url = f"{host}/api/box/update"
            data = {
                "code": line,
                "status": status_var.get()
            }
            response = requests.post(url, json=data)
            print(f"POST request sent. Status code: {response.status_code}")
        else:
            key_buffer.append(key.char if hasattr(key, 'char') else str(key))
    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    pass

def update_text_box(line):
    text_box.config(state=tk.NORMAL)
    text_box.insert(tk.END, f"{line}\n")
    text_box.config(state=tk.DISABLED)

def create_logfile():
    global last_logfile_path, is_active
    if start_button['text'] == "Start":
        if not os.path.exists('logs'):
            os.makedirs('logs')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        last_logfile_path = os.path.join('logs', f"{timestamp}.log")
        with open(last_logfile_path, 'w') as logfile:
            logfile.write("Logfile created\n")
        print(f"Logfile created: {last_logfile_path}")
        start_button.config(text="Stop", bg="red")
        text_box.config(state=tk.NORMAL)
        text_box.insert(tk.END, "Waiting for scans\n")
        text_box.config(state=tk.DISABLED)
        is_active = True  # Activate the handler
    else:
        start_button.config(text="Start", bg="SystemButtonFace")
        is_active = False  # Deactivate the handler

def on_closing():
    listener.stop()
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Mount Olympus Scanner")
root.geometry("350x150")

# Create a text box
text_box = tk.Text(root, height=80, width=200)
text_box.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
text_box.config(state=tk.DISABLED)

# Create a LabelFrame for the button and option menu
frame = tk.LabelFrame(root, text="Controls")
frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

# Create a "Start" button
start_button = tk.Button(frame, text="Start", command=create_logfile)
start_button.grid(row=0, column=0, padx=5, pady=5)

# Create an OptionMenu for selecting status
status_var = tk.StringVar(root)
status_var.set("Shipping")  # default value
status_options = ["Shipping", "Delivered", "Used"]
status_menu = tk.OptionMenu(frame, status_var, *status_options)
status_menu.grid(row=1, column=0, padx=5, pady=5)

# Bind the closing event to the cleanup function
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start listening
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Run the application
root.mainloop()