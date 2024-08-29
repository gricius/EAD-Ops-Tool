import tkinter as tk

def copy_to_clipboard(root, text, button):
    root.clipboard_clear()
    root.clipboard_append(text)
    button.config(bg="lime", text="Copied!")
    root.after(2000, lambda: reset_copy_button(button))

def reset_copy_button(button):
    if button.winfo_exists():
        button.config(bg="SystemButtonFace", text="Copy")