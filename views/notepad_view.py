# views/notepad_view.py
import tkinter as tk
from utils.clipboard_utils import paste_from_clipboard
from utils.misc_utils import find_and_replace

def show_notepad(root, main_frame, current_theme):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    root.title("EAD OPS Tool - Notepad")

    frame = tk.Frame(main_frame, bd=2, relief="groove")
    frame.grid(row=0, column=0, sticky="nsew")

    # Configure main_frame to expand
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # options frame for the notepad view
    options_frame = tk.Frame(frame, bd=2, relief="groove")
    options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    # Variable to track whether invisible characters are shown
    invisible_shown = False
    original_content = ''

    # Variable to track Caps Lock state
    caps_lock_on = False

    # Function to toggle invisible characters
    def toggle_invisible_characters():
        nonlocal invisible_shown, original_content
        if not invisible_shown:
            # Save the original content
            original_content = text_widget.get("1.0", tk.END)
            # Replace invisible characters with visible symbols
            modified_content = original_content.replace(' ', '·').replace('\t', '→').replace('\n', '¶\n')
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", modified_content)
            invisible_shown = True
            show_invisible_button.config(text='Hide Invisible')
        else:
            # Restore the original content
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", original_content)
            invisible_shown = False
            show_invisible_button.config(text='Show Invisible')

    # All to Caps function
    def convert_to_caps():
        # Get the current cursor position
        cursor_position = text_widget.index(tk.INSERT)
        
        # Convert the content of the text widget to uppercase
        current_content = text_widget.get("1.0", "end-1c")
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", current_content.upper())

        # Restore the cursor to its original position
        text_widget.mark_set(tk.INSERT, cursor_position)

    # Function to enable/disable always Caps Lock On
    def toggle_caps_lock():
        nonlocal caps_lock_on
        caps_lock_on = not caps_lock_on
        if caps_lock_on:
            caps_lock_button.config(fg="green")
        else:
            caps_lock_button.config(fg=current_theme['fg'])

    # Function to enforce Caps Lock On if enabled
    def on_key_release(event):
        if caps_lock_on:
            # Get the current cursor position
            cursor_position = text_widget.index(tk.INSERT)
            
            # Convert the content of the text widget to uppercase
            current_content = text_widget.get("1.0", "end-1c")
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", current_content.upper())

            # Restore the cursor to its original position
            text_widget.mark_set(tk.INSERT, cursor_position)

    # Show invisible characters button
    show_invisible_button = tk.Button(options_frame, text="Show Invisible", command=toggle_invisible_characters)
    show_invisible_button.grid(row=0, column=0, padx=5, sticky="e")

    # All to Caps button
    all_caps_button = tk.Button(options_frame, text="All to Caps", command=lambda: convert_to_caps())
    all_caps_button.grid(row=0, column=1, padx=5, sticky="e")

    # Caps Lock switch button
    caps_lock_button = tk.Button(options_frame, text="Caps Lock", command=toggle_caps_lock)
    caps_lock_button.grid(row=0, column=2, padx=5, sticky="e")

    # input frame for the notepad view
    input_frame = tk.Frame(frame, bd=2, relief="groove")
    input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # text widget
    text_widget = tk.Text(input_frame)
    text_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    # Bind the text widget to handle key release when Caps Lock is on
    text_widget.bind('<KeyRelease>', on_key_release)

    # button frame inside input_frame
    button_frame = tk.Frame(input_frame, bd=2, relief="groove")
    button_frame.grid(row=1, column=0, pady=5, sticky="ew")

    paste_button = tk.Button(button_frame, text="Paste",
                             command=lambda: paste_from_clipboard(root, text_widget))
    paste_button.grid(row=0, column=0, padx=5)

    find_entry = tk.Entry(button_frame)
    find_entry.grid(row=0, column=1, padx=5)

    replace_entry = tk.Entry(button_frame)
    replace_entry.grid(row=0, column=2, padx=5)

    replace_button = tk.Button(button_frame, text="Replace all",
                               command=lambda: find_and_replace(text_widget, find_entry.get(), replace_entry.get()))
    replace_button.grid(row=0, column=3, padx=5)

    copy_button = tk.Button(button_frame, text="Copy",
                            command=lambda: (root.clipboard_clear(),
                                             root.clipboard_append(text_widget.get("1.0", "end-1c"))))
    copy_button.grid(row=0, column=4, padx=5)

    # Configure grid weights to make the text widget expand
    frame.grid_rowconfigure(0, weight=0)  # options_frame (fixed size)
    frame.grid_rowconfigure(1, weight=1)  # input_frame (expands)
    frame.grid_columnconfigure(0, weight=1)

    input_frame.grid_rowconfigure(0, weight=1)  # text_widget row
    input_frame.grid_columnconfigure(0, weight=1)

