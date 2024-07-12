import tkinter as tk
from utils.clipboard_utils import paste_from_clipboard
from utils.misc_utils import find_and_replace

def show_notepad(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(frame)
    input_frame.pack(fill="x", pady=10)

    text_widget = tk.Text(input_frame, height=20, width=80)
    text_widget.pack(padx=5, pady=5)

    button_frame = tk.Frame(input_frame)
    button_frame.pack(fill="x", pady=5)

    paste_button = tk.Button(button_frame, text="Paste", command=lambda: paste_from_clipboard(root, text_widget))
    paste_button.pack(side=tk.LEFT, padx=5)

    find_entry = tk.Entry(button_frame)
    find_entry.pack(side=tk.LEFT, padx=5)

    replace_entry = tk.Entry(button_frame)
    replace_entry.pack(side=tk.LEFT, padx=5)

    replace_button = tk.Button(button_frame, text="Replace", command=lambda: find_and_replace(text_widget, find_entry.get(), replace_entry.get()))
    replace_button.pack(side=tk.LEFT, padx=5)
