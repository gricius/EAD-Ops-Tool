# views/ino_tool_view.py
import tkinter as tk
from utils.clipboard_utils import paste_from_clipboard
from utils.drawing_utils import show_on_map
from utils.button_utils import copy_to_clipboard
import re
from tkinter import messagebox

def format_time_ranges(time_ranges):
    months = {
        '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY', '06': 'JUN',
        '07': 'JUL', '08': 'AUG', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
    }
    
    formatted_output = []
    previous_date = ""
    
    for i, time_range in enumerate(time_ranges):
        start, end = time_range.split(' TO ')
        start_date = start[2:6]  # Extract MMDD (MMDD for start date)
        end_date = end[2:6]  # Extract MMDD (MMDD for end date)
        
        # Format start and end times as HHMM
        start_time = start[6:]
        end_time = end[6:]
        
        # Month and day formatting
        start_month = months[start[2:4]]
        start_day = start[4:6]
        end_month = months[end[2:4]]
        end_day = end[4:6]
        
        if start_date == previous_date:
            # Same day, just append the time range
            if start_date == end_date:
                formatted_output[-1] += f" {start_time}-{end_time}"
            else:
                # If the activity ends the next day but the same month, show only the time
                if start_month == end_month:
                    formatted_output[-1] += f" {start_time}-{end_time}"
                else:
                    formatted_output[-1] += f" {start_time}-{end_month} {end_day} {end_time}"
        else:
            # New day, display the month and day
            if start_date == end_date:
                if formatted_output:
                    formatted_output[-1] += ","  # Add a comma before the next date range
                formatted_output.append(f"{start_month} {start_day} {start_time}-{end_time}")
            else:
                # Cross-day logic: if in the same month, show only the time for the end
                if start_month == end_month:
                    if formatted_output:
                        formatted_output[-1] += ","  # Add a comma before the next date range
                    formatted_output.append(f"{start_month} {start_day} {start_time}-{end_time}")
                else:
                    # Cross-month logic: include the end month in the output
                    if formatted_output:
                        formatted_output[-1] += ","  # Add a comma before the next date range
                    formatted_output.append(f"{start_month} {start_day} {start_time}-{end_month} {end_day} {end_time}")
        
        # Update the previous date to the current start date
        previous_date = start_date

    return ' '.join(formatted_output)



def paste_time_ranges(root, time_text):
    clipboard_content = root.clipboard_get()

    # Extract time ranges in ICAO format using regex
    time_ranges = re.findall(r'\d{10} TO \d{10}', clipboard_content)
    
    if not time_ranges:
        messagebox.showwarning("Invalid Input", "No valid time ranges found in the clipboard")
        return

    # Format the time ranges
    formatted_times = format_time_ranges(time_ranges)
    
    # Clear the text area and insert formatted times
    time_text.delete("1.0", tk.END)
    time_text.insert(tk.END, formatted_times)

def show_ino_tool(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()
        
    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(frame)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    paste_coord_button = tk.Button(input_frame, text="Paste COORD", command=lambda: paste_from_clipboard(root, source_text, original_text, sorted_text, original_canvas, sorted_canvas, original_frame))
    paste_coord_button.grid(row=0, column=0, padx=5, pady=5)

    paste_time_button = tk.Button(input_frame, text="Paste YB D)", command=lambda: paste_time_ranges(root, source_text))
    paste_time_button.grid(row=0, column=1, padx=5, pady=5)

    # clear the text area on click
    source_text = tk.Text(input_frame, height=20, width=30)
    source_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Conversion frame
    conversion_frame = tk.Frame(frame)
    conversion_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    km_label = tk.Label(conversion_frame, text="KM")
    km_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    km_entry = tk.Entry(conversion_frame, width=10)
    km_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    nm_label = tk.Label(conversion_frame, text="NM")
    nm_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    nm_entry = tk.Entry(conversion_frame, width=10)
    nm_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    mt_label = tk.Label(conversion_frame, text="MT")
    mt_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    mt_entry = tk.Entry(conversion_frame, width=10)
    mt_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ft_label = tk.Label(conversion_frame, text="FT")
    ft_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
    ft_entry = tk.Entry(conversion_frame, width=10)
    ft_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    def convert_km_to_nm(event):
        try:
            km_value = float(km_entry.get())
            nm_value = km_value * 0.539957
            nm_entry.delete(0, tk.END)
            nm_entry.insert(0, f"{nm_value:.2f}")
        except ValueError:
            pass

    def convert_nm_to_km(event):
        try:
            nm_value = float(nm_entry.get())
            km_value = nm_value / 0.539957
            km_entry.delete(0, tk.END)
            km_entry.insert(0, f"{km_value:.2f}")
        except ValueError:
            pass

    def convert_mt_to_ft(event):
        try:
            mt_value = float(mt_entry.get())
            ft_value = mt_value * 3.28084
            ft_entry.delete(0, tk.END)
            ft_entry.insert(0, f"{ft_value:.2f}")
        except ValueError:
            pass

    def convert_ft_to_mt(event):
        try:
            ft_value = float(ft_entry.get())
            mt_value = ft_value / 3.28084
            mt_entry.delete(0, tk.END)
            mt_entry.insert(0, f"{mt_value:.2f}")
        except ValueError:
            pass

    km_entry.bind("<FocusOut>", convert_km_to_nm)
    nm_entry.bind("<FocusOut>", convert_nm_to_km)
    mt_entry.bind("<FocusOut>", convert_mt_to_ft)
    ft_entry.bind("<FocusOut>", convert_ft_to_mt)
    
    # Load templates and get the first three for copying
    from views.templates_view import load_template_order
    import os
    import json

    TEMPLATES_DIR = "templates"

    def get_template_content(template_name):
        template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
        if os.path.exists(template_path):
            with open(template_path, "r") as file:
                return json.load(file).get("content", "")
        return ""
    
    # Fetch the first three templates
    template_order = load_template_order()
    first_three_templates = template_order[:3] if len(template_order) >= 3 else template_order

    # Create copy buttons for the first three templates
    tpl_label = tk.Label(conversion_frame, text='Copy template:')
    tpl_label.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    copy_template1_button = tk.Button(conversion_frame, text=" # 1")
    copy_template1_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
    copy_template1_button.config(command=lambda: copy_to_clipboard(root, get_template_content(first_three_templates[0]), copy_template1_button))

    copy_template2_button = tk.Button(conversion_frame, text=" # 2")
    copy_template2_button.grid(row=3, column=1, padx=5, pady=5 )
    copy_template2_button.config(command=lambda: copy_to_clipboard(root, get_template_content(first_three_templates[1]), copy_template2_button))

    copy_template3_button = tk.Button(conversion_frame, text=" # 3")
    copy_template3_button.grid(row=3, column=2, padx=5, pady=5, sticky="ew")
    copy_template3_button.config(command=lambda: copy_to_clipboard(root, get_template_content(first_three_templates[2]), copy_template3_button))

    # Original frame with "Show on map" button, original text
    original_frame = tk.Frame(frame)
    original_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)

    show_map_button = tk.Button(original_frame, text="Show on map", command=lambda: show_on_map(
        [coord for coord in original_text.get("1.0", "end-1c").split('\n') if coord],
        [coord for coord in sorted_text.get("1.0", "end-1c").split('\n') if coord]
    ))
    show_map_button.grid(row=0, column=0, padx=5, pady=5)

    # Original text label
    original_label = tk.Label(original_frame, text="Original COORDs")
    original_label.grid(row=1, column=0, padx=5, pady=5)

    # Original text
    original_text = tk.Text(original_frame, height=14, width=15)
    original_text.grid(row=2, column=0, padx=5, pady=5)

    # Copy button to replace Windows clipboard with original text
    copy_button = tk.Button(original_frame, text="Copy")
    copy_button.grid(row=3, column=0, padx=5, pady=5)
    copy_button.config(command=lambda: copy_to_clipboard(root, original_text.get("1.0", tk.END).strip(), copy_button))

    # Original canvas
    original_canvas = tk.Canvas(frame, bg="white", width=320, height=320)
    original_canvas.grid(row=0, column=3, padx=5, pady=5)

    # Sorted frame with sorted text
    sorted_frame = tk.Frame(frame)
    sorted_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)

    # Sorted text label
    sorted_label = tk.Label(sorted_frame, text="Sorted COORDs")
    sorted_label.grid(row=0, column=0, padx=5, pady=5)

    sorted_text = tk.Text(sorted_frame, height=14, width=15)
    sorted_text.grid(row=1, column=0, padx=5, pady=5)

    # Copy button to replace Windows clipboard with sorted text
    sorted_copy_button = tk.Button(sorted_frame, text="Copy")
    sorted_copy_button.grid(row=2, column=0, padx=5, pady=5)
    sorted_copy_button.config(command=lambda: copy_to_clipboard(root, sorted_text.get("1.0", tk.END).strip(), sorted_copy_button))

    # Sorted canvas
    sorted_canvas = tk.Canvas(frame, bg="white", width=320, height=320)
    sorted_canvas.grid(row=1, column=3, padx=5, pady=5)

    # Configure grid weights for responsiveness
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("INO Tool")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    show_ino_tool(root, main_frame)

    root.mainloop()