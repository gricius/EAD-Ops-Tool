# utils/misc_utils.py   
import re
import tkinter as tk  # Import tk if not already imported

def find_and_replace(text_widget, find_text, replace_text):
    if not find_text:
        return  # Do nothing if find_text is empty

    # Get the entire content of the text widget
    content = text_widget.get("1.0", tk.END)
    # Use regular expression for case-insensitive replacement
    pattern = re.compile(re.escape(find_text), re.IGNORECASE)
    new_content = pattern.sub(replace_text, content)
    # Replace the content in the text widget
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", new_content)

