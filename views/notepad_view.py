# views/notepad_view.py
import tkinter as tk
from utils.clipboard_utils import paste_from_clipboard
from utils.misc_utils import find_and_replace

def show_notepad(root, main_frame, current_theme):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.grid(row=0, column=0, sticky="nsew")

    input_frame = tk.Frame(frame)
    input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    text_widget = tk.Text(input_frame)
    text_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    button_frame = tk.Frame(input_frame)
    button_frame.grid(row=1, column=0, pady=5, sticky="ew")

    paste_button = tk.Button(button_frame, text="Paste", command=lambda: paste_from_clipboard(root, text_widget))
    paste_button.grid(row=0, column=0, padx=5)

    find_entry = tk.Entry(button_frame)
    find_entry.grid(row=0, column=1, padx=5)

    replace_entry = tk.Entry(button_frame)
    replace_entry.grid(row=0, column=2, padx=5)

    replace_button = tk.Button(button_frame, text="Replace", command=lambda: find_and_replace(text_widget, find_entry.get(), replace_entry.get()))
    replace_button.grid(row=0, column=3, padx=5)

    # copy to clipboard
    copy_button = tk.Button(button_frame, text="Copy", command=lambda: (root.clipboard_clear(), root.clipboard_append(text_widget.get("1.0", "end-1c"))))
    copy_button.grid(row=0, column=4, padx=5)

    # Configure grid weights to make the text widget expand
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    input_frame.grid_rowconfigure(0, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)
