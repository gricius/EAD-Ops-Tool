# utils/clipboard_utils.py
import tkinter as tk
from tkinter import messagebox
from .coordinate_utils import extract_coordinates, sort_coordinates
from .drawing_utils import draw_coordinates

def show_copied_modal(root, parent_frame):
    modal = tk.Toplevel(root)
    modal.title("Copied")
    label = tk.Label(modal, text="Original COORDs Copied", font=("Arial", 18), bg="lime")
    label.pack(padx=20, pady=20)
    modal.after(2000, modal.destroy)
    modal.transient(parent_frame)
    modal.grab_set()
    modal.update_idletasks()
    modal.geometry(f"+{parent_frame.winfo_rootx() + parent_frame.winfo_width() // 2 - modal.winfo_width() // 2}+{parent_frame.winfo_rooty() + parent_frame.winfo_height() // 2 - modal.winfo_height() // 2}")
    root.wait_window(modal)

def paste_from_clipboard(root, source_text, original_text=None, sorted_text=None, original_canvas=None, sorted_canvas=None, parent_frame=None):
    clipboard_content = root.clipboard_get()
    source_text.delete("1.0", tk.END)
    source_text.insert(tk.END, clipboard_content)
    
    coords, invalid_coords = extract_coordinates(clipboard_content)
    
    if original_text is not None:
        original_text.delete("1.0", tk.END)
        if coords:
            original_text.insert(tk.END, "\n".join(coords))
            # paste to clipboard
            root.clipboard_clear()
            root.clipboard_append("\n".join(coords))
            if parent_frame is not None:
                show_copied_modal(root, parent_frame)
        else:
            original_text.insert(tk.END, "No valid format coordinates found. Supported formats are: DD MM[NS] DDD MM [EW], DD MM SS[NS] DDD MM SS[EW], DD MM SS.d2(4)[NS] DDD MM SS.d2[4][EW]")
    
    if sorted_text is not None:
        sorted_coords = sort_coordinates(coords)
        sorted_text.delete("1.0", tk.END)
        sorted_text.insert(tk.END, "\n".join(sorted_coords))
        
        if original_canvas is not None and sorted_canvas is not None:
            draw_coordinates(coords, original_canvas)
            draw_coordinates(sorted_coords, sorted_canvas)
    
    if invalid_coords:
        messagebox.showwarning('Warning', f'The following coordinates are invalid and were skipped:\n' + '\n'.join(invalid_coords))
