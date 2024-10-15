# views/ino_tool_view.py
import tkinter as tk
import tkinter.font as tkFont
from utils.clipboard_utils import paste_from_clipboard
from utils.drawing_utils import show_on_map, draw_coordinates
import re
from tkinter import messagebox, filedialog
import pandas as pd
import json
import os
import sys
import math

CONFIG_FILE = "config.json"
excel_file = None  # Global variable for the Excel file
excel_data = None

# Global variable for extreme coordinates
extremities_str = ""

def prompt_for_excel_file():
    """Prompt the user to select the Excel file if it's not found or not specified."""
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        messagebox.showerror("Error", "No file selected. The application will exit.")
        sys.exit()  # Exit the application if no file is selected
    return file_path

def load_config():
    """Load configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

def save_config(config):
    """Save configuration to the config file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

def get_resource_path(file_name):
    """Get the absolute path to the resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, file_name)

def load_excel_data(file_path):
    """Load the Excel data from the given file path."""
    try:
        excel_data = pd.read_excel(file_path, sheet_name=None)
        if excel_data is None or not excel_data:
            raise ValueError("Failed to load any data from the Excel file.")
        return excel_data
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load Excel file: {e}")
        return None

def copy_to_clipboard(root, text, button):
    """Copies text to the clipboard and updates the button to indicate success."""
    root.clipboard_clear()
    root.clipboard_append(text)

def add_line_numbers_to_text_widget(text_widget):
    """Add line numbers to each line in the text widget."""
    text = text_widget.get("1.0", tk.END).strip()
    lines = text.split('\n')
    text_widget.delete("1.0", tk.END)
    for i, line in enumerate(lines):
        numbered_line = f"{i+1}. {line}"
        text_widget.insert(tk.END, numbered_line + '\n', 'right_align')

def get_text_without_line_numbers(text_widget):
    """Retrieve text from a text widget, stripping line numbers."""
    text = text_widget.get("1.0", tk.END).strip()
    lines = text.split('\n')
    clean_lines = [line.partition('. ')[2] if '. ' in line else line for line in lines]
    return '\n'.join(clean_lines)
def calculate_new_coordinate(start_coord, radial, distance_nm, result_entry):
    # Earth's radius in nautical miles
    EARTH_RADIUS_NM = 3440.065

    # Helper function to parse coordinate string
    def parse_coord(coord_str):
        # Find indices of hemisphere indicators
        lat_hemi_idx = max(coord_str.find('N'), coord_str.find('S'))
        lon_hemi_idx = max(coord_str.find('E'), coord_str.find('W'))

        if lat_hemi_idx == -1 or lon_hemi_idx == -1:
            raise ValueError("Invalid coordinate format.")

        # Extract latitude and longitude strings
        lat_str = coord_str[:lat_hemi_idx]
        lat_hemi = coord_str[lat_hemi_idx]
        lon_str = coord_str[lat_hemi_idx+1:lon_hemi_idx]
        lon_hemi = coord_str[lon_hemi_idx]

        # Parse latitude
        if len(lat_str) == 4:  # DDMM
            lat_deg = int(lat_str[:2])
            lat_min = int(lat_str[2:])
            lat_sec = 0
        elif len(lat_str) == 6:  # DDMMSS
            lat_deg = int(lat_str[:2])
            lat_min = int(lat_str[2:4])
            lat_sec = int(lat_str[4:])
        else:
            raise ValueError("Invalid latitude format.")

        # Parse longitude
        if len(lon_str) == 5:  # DDDMM
            lon_deg = int(lon_str[:3])
            lon_min = int(lon_str[3:])
            lon_sec = 0
        elif len(lon_str) == 7:  # DDDMMSS
            lon_deg = int(lon_str[:3])
            lon_min = int(lon_str[3:5])
            lon_sec = int(lon_str[5:])
        else:
            raise ValueError("Invalid longitude format.")

        # Convert to decimal degrees
        lat = lat_deg + lat_min / 60 + lat_sec / 3600
        lon = lon_deg + lon_min / 60 + lon_sec / 3600

        # Apply hemisphere
        if lat_hemi == 'S':
            lat = -lat
        if lon_hemi == 'W':
            lon = -lon

        return lat, lon

    # Convert degrees to radians
    def deg_to_rad(degrees):
        return degrees * math.pi / 180

    # Convert radians to degrees
    def rad_to_deg(radians):
        return radians * 180 / math.pi

    # Parse the starting coordinate
    lat1_deg, lon1_deg = parse_coord(start_coord)
    lat1_rad = deg_to_rad(lat1_deg)
    lon1_rad = deg_to_rad(lon1_deg)

    # Convert radial and distance
    bearing_rad = deg_to_rad(radial % 360)
    angular_distance = distance_nm / EARTH_RADIUS_NM

    # Calculate the new latitude
    lat2_rad = math.asin(
        math.sin(lat1_rad) * math.cos(angular_distance) +
        math.cos(lat1_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
    )

    # Calculate the new longitude
    lon2_rad = lon1_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat1_rad),
        math.cos(angular_distance) - math.sin(lat1_rad) * math.sin(lat2_rad)
    )

    # Normalize longitude to be between -180 and 180 degrees
    lon2_rad = (lon2_rad + 3 * math.pi) % (2 * math.pi) - math.pi

    # Convert back to degrees
    lat2_deg = rad_to_deg(lat2_rad)
    lon2_deg = rad_to_deg(lon2_rad)

    # Determine hemispheres
    lat_hemi = 'N' if lat2_deg >= 0 else 'S'
    lon_hemi = 'E' if lon2_deg >= 0 else 'W'

    # Convert to absolute values
    lat2_deg = abs(lat2_deg)
    lon2_deg = abs(lon2_deg)

    # Extract degrees and minutes
    lat_deg_int = int(lat2_deg)
    lat_min_float = (lat2_deg - lat_deg_int) * 60
    lat_min_int = int(round(lat_min_float))

    lon_deg_int = int(lon2_deg)
    lon_min_float = (lon2_deg - lon_deg_int) * 60
    lon_min_int = int(round(lon_min_float))

    # Handle rounding that could push minutes to 60
    if lat_min_int == 60:
        lat_min_int = 0
        lat_deg_int += 1

    if lon_min_int == 60:
        lon_min_int = 0
        lon_deg_int += 1

    # Format the new coordinate
    lat_deg_str = f"{lat_deg_int:02d}"
    lat_min_str = f"{lat_min_int:02d}"
    lon_deg_str = f"{lon_deg_int:03d}"
    lon_min_str = f"{lon_min_int:02d}"

    new_coord = f"{lat_deg_str}{lat_min_str}{lat_hemi}{lon_deg_str}{lon_min_str}{lon_hemi}"
    result_entry.delete(0, tk.END)  
    result_entry.insert(0, new_coord)  
    # print(new_coord)
    return new_coord

def search_abbreviation(abbr_text, decoded_text, root, current_theme):
    """Perform search and display results in a modal pop-up window."""
    try:
        results = []

        abbr_text = abbr_text.lower()
        decoded_text = decoded_text.lower()

        for sheet_name, sheet_df in excel_data.items():
            if abbr_text:
                matches = sheet_df[sheet_df.iloc[:, 0].astype(str).str.lower().str.contains(abbr_text, na=False)]
                results.extend((row.iloc[0], row.iloc[1], sheet_name) for _, row in matches.iterrows())

            if decoded_text:
                matches = sheet_df[sheet_df.iloc[:, 1].astype(str).str.lower().str.contains(decoded_text, na=False)]
                results.extend((row.iloc[0], row.iloc[1], sheet_name) for _, row in matches.iterrows())

        # If no results found, show a message and return
        if not results:
            messagebox.showinfo("No Results", "No matches found.")
            return

        # Open a modal pop-up window
        result_popup = tk.Toplevel(root)
        result_popup.title("Search Results")
        
        # Set the background color for dark mode
        result_popup.configure(bg=current_theme['bg'])

        # Set a minimum width for the modal window
        result_popup.geometry("900x300")  # Adjust this size if necessary to fit the results and button

        # Create a scrollable frame in the pop-up
        canvas = tk.Canvas(
            result_popup, 
            highlightbackground=current_theme['highlightbackground'], 
            highlightthickness=2, 
            relief="raised",
            bg=current_theme['bg']
        )
        scrollbar = tk.Scrollbar(result_popup, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(
            canvas, 
            highlightbackground=current_theme['highlightbackground'], 
            highlightthickness=2, 
            relief="raised",
            bg=current_theme['bg']
        )

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create result widgets inside the scrollable frame
        for i, (abbr, decoded, sheet_name) in enumerate(results):
            create_result_widgets(scrollable_frame, i, abbr, decoded, sheet_name, root, current_theme)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during search: {e}")

def create_result_widgets(result_frame, index, abbr, decoded, sheet_name, root, current_theme):
    """Create and place result widgets in the result frame (now in the pop-up)."""

    # Create a frame to hold multiple labels for better formatting
    widget_frame = tk.Frame(result_frame, bg=current_theme['bg'])
    widget_frame.grid(row=2 * index, column=0, sticky="w", padx=5, pady=2)

    # Abbreviation Label
    abbr_label = tk.Label(widget_frame, text=f"Abbr: {abbr}, ", bg=current_theme['bg'], fg=current_theme['fg'])
    abbr_label.pack(side="left")

    # Decoded Label
    decoded_label = tk.Label(widget_frame, text=f"Decoded: {decoded}, ", bg=current_theme['bg'], fg=current_theme['fg'])
    decoded_label.pack(side="left")

    # Source Label (with "Source:" in bold)
    source_label = tk.Label(widget_frame, text="Source: ", bg=current_theme['bg'], fg=current_theme['fg'], font=("TkDefaultFont", 10, "bold"))
    source_label.pack(side="left")

    # Sheet Name Label (following the "Source:" label)
    sheet_name_label = tk.Label(widget_frame, text=sheet_name, bg=current_theme['bg'], fg=current_theme['fg'])
    sheet_name_label.pack(side="left")

    def on_copy():
        # Copy the text to the clipboard
        copy_to_clipboard(root, f"({decoded})", None)
        # Close the pop-up window
        result_frame.winfo_toplevel().destroy()

    copy_button = tk.Button(
        result_frame, 
        text="Copy",
        command=on_copy,
        bg=current_theme['button_bg'],
        fg=current_theme['fg']
    )
    copy_button.grid(row=2 * index, column=1, padx=5)


    def on_copy():
        # Copy the text to the clipboard
        copy_to_clipboard(root, f"({decoded})", None)
        # Close the pop-up window
        result_frame.winfo_toplevel().destroy()

    copy_button = tk.Button(
        result_frame, 
        text="Copy",
        command=on_copy,
        bg=current_theme['button_bg'],
        fg=current_theme['fg']
    )
    copy_button.grid(row=2 * index, column=1, padx=5)

# Flight level calculation
def calculate_flight_level(nof_entry, uom_var, height_entry, result_entry, root):
    try:
        global excel_file, excel_data
        if excel_data is None:
            raise ValueError("Excel data is not loaded.")

        df = excel_data.get("UPPER_TABLE")
        if df is None:
            raise ValueError("UPPER_TABLE sheet not found in the Excel file")

        nof_value = nof_entry.get().strip().upper()
        height_value = height_entry.get().strip()
        uom_value = uom_var.get()

        if not (1 <= len(nof_value) <= 4):
            raise ValueError("NOF must be between 1 and 4 characters long")

        result = df[df.iloc[:, 0].str.upper() == nof_value]

        if result.empty:
            result_entry.delete(0, tk.END)
            result_entry.insert(0, "No match found")
            return

        selected_value = calculate_flight_level_value(result, height_value, uom_value)
        result_entry.delete(0, tk.END)
        result_entry.insert(0, f"{selected_value:.0f}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during calculation: {e}")

def calculate_flight_level_value(result, height_value, uom_value):
    """Calculate the flight level based on height and unit of measure."""
    if not height_value:
        return result.iloc[0, 5]

    if uom_value == "M":
        height_value = round(int(height_value) * 3.28084 + 49)
        selected_value = result.iloc[0, 5] * 100
        return round((selected_value + height_value) / 100)
    elif uom_value == "FT":
        selected_value = result.iloc[0, 5] * 100
        height_value = int(height_value) + 49
        return round(selected_value / 100)

def create_entry_with_label(parent, label_text, entry_width, row, column):
    """Helper function to create a label and entry widget."""
    tk.Label(parent, text=label_text).grid(row=row, column=column, padx=5, pady=5, sticky="e")
    entry = tk.Entry(parent, width=entry_width)
    entry.grid(row=row, column=column + 1, padx=5, pady=5, sticky="w")
    return entry

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
        end_date = end[2:6]      # Extract MMDD (MMDD for end date)

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

    # Copy the formatted times to the clipboard
    copy_to_clipboard(root, formatted_times, None)  # Passing None for the button as it's not associated here

def bind_paste_shortcuts(root, paste_and_add_line_numbers):
    # Bind both Ctrl+P and Ctrl+Shift+P to call paste_and_add_line_numbers function
    def on_paste_event(event):
        paste_and_add_line_numbers()

    # Binding Ctrl+P (lowercase p)
    root.bind_all("<Control-p>", on_paste_event)

    # Binding Ctrl+Shift+P (uppercase P)
    root.bind_all("<Control-P>", on_paste_event)

def show_ino_tool(root, main_frame, current_theme):
    global excel_file, excel_data
    root.title("EAD OPS Tool - INO OPS Tool")

    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Load configuration
    config = load_config()
    excel_file = config.get("excel_file_path")

    if not excel_file or not os.path.exists(excel_file):
        excel_file = prompt_for_excel_file()  # Ask for the file if not found
        config["excel_file_path"] = excel_file
        save_config(config)

    excel_data = load_excel_data(excel_file)  # Load the Excel data
    if excel_data is None:
        return  # Stop if there's an error loading the data

    # Set up the main frame layout
    frame = tk.Frame(main_frame, cursor="cross", highlightbackground=current_theme['highlightbackground'], highlightthickness=2, highlightcolor=current_theme['highlightbackground'])
    frame.grid(sticky="nsew", padx=5, pady=5)

   

    # Configure grid weights for responsiveness
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Function to clear source_text on click
    def clear_text(event):
        source_text.delete("1.0", tk.END)

    # Input frame for paste buttons and text area
    input_frame = tk.Frame(frame, relief="raised", border=5)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    input_frame.grid_columnconfigure(0, weight=1)  # Allow input frame to expand

    # Text area for input
    source_text = tk.Text(input_frame, height=15, width=30)
    source_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Bind left mouse click to clear the text area
    source_text.bind("<Button-1>", clear_text)

    # Column 2: Original and Sorted canvases
    column_two_frame = tk.Frame(frame, highlightbackground=current_theme['highlightbackground'], highlightthickness=2, relief="raised")
    column_two_frame.grid(row=0, column=2, rowspan=5, padx=5, pady=5, sticky="nsew")
    column_two_frame.grid_rowconfigure(0, weight=1)
    column_two_frame.grid_columnconfigure(0, weight=1)

    # Original canvas
    original_canvas_frame = tk.Frame(column_two_frame, bg=current_theme['bg'], relief="raised")
    original_canvas = tk.Canvas(original_canvas_frame, width=320, height=320, bg=current_theme['canvas_bg'], border=0)
    original_canvas.grid(row=0, column=0, padx=5, pady=5)

    # Sorted canvas
    sorted_canvas = tk.Canvas(column_two_frame, width=320, height=320, bg=current_theme['canvas_bg'], border=0)
    sorted_canvas.grid(row=1, column=0, padx=5, pady=5)

    # Function to update the coordinate count label
    def update_coord_count(event=None):
        """Update the coordinate count in the original_label."""
        original_text.edit_modified(False)  # Reset the modified flag
        text = original_text.get("1.0", tk.END).strip()
        if text:
            num_coords = len(text.split('\n'))
        else:
            num_coords = 0
        original_label.config(text=f"Original COORDs: {num_coords}")

    # Function to paste and add line numbers
    def paste_and_add_line_numbers():
        global extremities_str
        extremities_str = paste_from_clipboard(
            root,
            source_text,
            original_text=original_text,
            sorted_text=sorted_text,
            original_canvas=original_canvas,
            sorted_canvas=sorted_canvas,
            current_theme=current_theme
        )
        add_line_numbers_to_text_widget(original_text)
        add_line_numbers_to_text_widget(sorted_text)
        update_coord_count()

    # Paste COORD button
    paste_coord_button = tk.Button(input_frame, text="Paste & Format COORD", command=paste_and_add_line_numbers,
                                   bg=current_theme['button_bg'], fg=current_theme['fg'])
    paste_coord_button.grid(row=0, column=0, padx=5, pady=5)

    # Paste YB D) button
    paste_time_button = tk.Button(input_frame, text="Paste YB D)", command=lambda: paste_time_ranges(root, source_text))
    paste_time_button.grid(row=0, column=1, padx=5, pady=5)

    # Conversion frame for calculations and results
    conversion_frame = tk.Frame(frame, bd=2, relief="raised", border=5)
    conversion_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    conversion_frame.grid_columnconfigure(1, weight=1)

    # KM to NM conversion
    km_label = tk.Label(conversion_frame, text="KM")
    km_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    km_entry = tk.Entry(conversion_frame, width=10)
    km_entry.grid(row=0, column=1, padx=5, pady=5)

    # NM to KM conversion
    nm_label = tk.Label(conversion_frame, text="NM")
    nm_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    nm_entry = tk.Entry(conversion_frame, width=10)
    nm_entry.grid(row=0, column=3, padx=5, pady=5)

    # MT to FT conversion
    mt_label = tk.Label(conversion_frame, text="MT")
    mt_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    mt_entry = tk.Entry(conversion_frame, width=10)
    mt_entry.grid(row=1, column=1, padx=5, pady=5)

    # FT to MT conversion
    ft_label = tk.Label(conversion_frame, text="FT")
    ft_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
    ft_entry = tk.Entry(conversion_frame, width=10)
    ft_entry.grid(row=1, column=3, padx=5, pady=5)
    # button without function
    calc_dist_btn = tk.Button(conversion_frame, text="Calculate Distance", bg=current_theme['button_bg'], fg=current_theme['fg'], command=lambda: calc_dist_btn.focus_set())
    calc_dist_btn.grid(row=2, column=0, padx=5, pady=5, columnspan=4)

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

    # fl fram
    fl_frame = tk.Frame(frame, bd=2, relief="raised", border=5)
    fl_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
    fl_frame.grid_columnconfigure(1, weight=1)

    # Flight level conversion
    tk.Label(fl_frame, text="NOF").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    nof_entry = tk.Entry(fl_frame, width=6)
    nof_entry.config(validate="key", validatecommand=(root.register(lambda P: len(P) <= 4), '%P'))
    nof_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(fl_frame, text="Height").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    height_entry = tk.Entry(fl_frame, width=10)
    height_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(fl_frame, text="UOM").grid(row=1, column=0, padx=5, pady=5)
    uom_var = tk.StringVar(value="M")
    tk.Radiobutton(fl_frame, text="M", variable=uom_var, value="M", selectcolor=current_theme['highlightbackground']).grid(row=1, column=1, padx=5, sticky="w")
    tk.Radiobutton(fl_frame, text="FT", variable=uom_var, value="FT", selectcolor=current_theme['highlightbackground']).grid(row=1, column=2, padx=5, sticky="w")

    calculate_button = tk.Button(fl_frame, text="Calculate FL", command=lambda: calculate_flight_level(nof_entry, uom_var, height_entry, fl_result_entry, root))
    calculate_button.grid(row=2, column=1, pady=5, sticky="ew")

    # result_label = tk.Label(fl_frame, text="FL ")
    # result_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    fl_result_entry = tk.Entry(fl_frame, width=4)
    fl_result_entry.grid(row=2, column=2, padx=5, pady=5, sticky="e")

    # Template frame
    template_frame = tk.Frame(frame, bd=2, relief="raised", border=5)
    template_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
    template_frame.grid_columnconfigure(1, weight=1)

    tpl_label = tk.Label(template_frame, text="Copy template:")
    tpl_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    from views.templates_view import load_template_order  # Ensure this import is correct

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
    copy_template1_button = tk.Button(template_frame, text=" #  1  ", command=lambda: copy_to_clipboard(root, get_template_content(first_three_templates[0]), copy_template1_button))
    copy_template1_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    copy_template2_button = tk.Button(template_frame, text="  # 2  ", command=lambda: copy_to_clipboard(root, get_template_content(first_three_templates[1]), copy_template2_button))
    copy_template2_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    
    copy_template3_button = tk.Button(template_frame, text="  # 3  ", command=lambda: copy_to_clipboard(root, get_template_content(first_three_templates[2]), copy_template3_button))
    copy_template3_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")

   # Abbreviation search frame
    abbreviation_frame = tk.Frame(frame, bd=2, relief="raised", border=5)
    abbreviation_frame.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
    
    abbr_entry = create_entry_with_label(abbreviation_frame, "Abbr.", 15, 0, 0)
    decoded_entry = create_entry_with_label(abbreviation_frame, "Decoded", 15, 1, 0)

    search_button = tk.Button(abbreviation_frame, text="Search", command=lambda: search_abbreviation(abbr_entry.get(), decoded_entry.get(), root, current_theme))
    search_button.grid(row=1, column=2, pady=5, sticky="e")

    # Abbreviation result frame
    # result_frame = tk.Frame(frame)
    # result_frame.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")

     # Column 1: Show on map, original/sorted text, and copy buttons
    column_one_frame = tk.Frame(frame, bd=2, relief="raised", border=5)
    column_one_frame.grid(row=0, column=1, rowspan=5, padx=5, pady=5, sticky="new")
    column_one_frame.grid_rowconfigure(0, weight=1)
    column_one_frame.grid_columnconfigure(0, weight=1)

    # Show on map button
    show_map_button = tk.Button(column_one_frame, text="Show on map", command=lambda: show_on_map(
        [coord.partition('. ')[2] for coord in original_text.get("1.0", "end-1c").split('\n') if coord],
        [coord.partition('. ')[2] for coord in sorted_text.get("1.0", "end-1c").split('\n') if coord]
    ))
    show_map_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # Original text label with coordinate count
    original_label = tk.Label(column_one_frame, text="Original COORDs: 0", bg=current_theme['bg'], fg=current_theme['fg'])
    original_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # Original text
    original_text = tk.Text(column_one_frame, height=10, width=19, bg=current_theme['bg'], fg=current_theme['fg'], insertbackground=current_theme['fg'])
    original_text.grid(row=2, column=0, padx=5, pady=5)

    # Configure right alignment tag for original_text
    original_text.tag_configure('right_align', justify='right')

    # Bind events to update the coordinate count whenever the text changes
    original_text.bind('<KeyRelease>', update_coord_count)
    original_text.bind('<<Modified>>', update_coord_count)

    # Copy button for original text
    original_copy_button = tk.Button(column_one_frame, text="Copy", command=lambda: copy_to_clipboard(
        root, get_text_without_line_numbers(original_text), original_copy_button
    ))
    original_copy_button.grid(row=3, column=0, padx=5, pady=5)


    # Sorted text label
    sorted_label = tk.Label(column_one_frame, text="Sorted COORDs", bg=current_theme['bg'], fg=current_theme['fg'])
    sorted_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

    # Sorted text
    sorted_text = tk.Text(column_one_frame, height=10, width=19, bg=current_theme['bg'], fg=current_theme['fg'], insertbackground=current_theme['fg'])
    sorted_text.grid(row=5, column=0, padx=5, pady=5)

    # Copy button for sorted text (modified to strip line numbers)
    sorted_copy_button = tk.Button(column_one_frame, text=" Copy Sorted  ", command=lambda: copy_to_clipboard(
        root, get_text_without_line_numbers(sorted_text), sorted_copy_button
    ))
    sorted_copy_button.grid(row=6, column=0, padx=5, pady=5, sticky="w")

    # Extreme coordinates Copy button for var extremities_text
    extremities_copy_button = tk.Button(column_one_frame, text="Extremities", command=lambda: copy_to_clipboard(
    root, extremities_str, extremities_copy_button
    ))
    extremities_copy_button.grid(row=6, column=0, padx=5, pady=5, sticky="e")

    # new coordinate calculation 
    # frame within coumn_one frame for new coordinate calculation
    new_coord_frame = tk.Frame(column_one_frame, bg=current_theme['bg'], relief="raised", border=5)
    new_coord_frame.grid(row=7, column=0, padx=5, pady=5, sticky="nsew")

    start_coord_label = tk.Label(new_coord_frame, text="COORD", bg=current_theme['bg'], fg=current_theme['fg'])
    start_coord_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # Entry for start_coord
    start_coord_entry = tk.Entry(new_coord_frame, width=16)
    start_coord_entry.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    # Label radial
    # Create a frame to hold both labels and entries
    radial_distance_frame = tk.Frame(new_coord_frame, bg=current_theme['bg'], border=0)
    radial_distance_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # Radial Label and Entry
    radial_label = tk.Label(radial_distance_frame, text="RAD", bg=current_theme['bg'], fg=current_theme['fg'])
    radial_label.pack(side="left")
    radial_entry = tk.Entry(radial_distance_frame, width=5)
    radial_entry.config(validate="key", validatecommand=(root.register(lambda P: len(P) <= 3), '%P'))
    radial_entry.pack(side="left", padx=(0, 10))  

    # Distance Label and Entry
    distance_label = tk.Label(radial_distance_frame, text="Dist.(NM)", bg=current_theme['bg'], fg=current_theme['fg'])
    distance_label.pack(side="left")
    distance_entry = tk.Entry(radial_distance_frame, width=5)
    distance_entry.pack(side="left")


    # Calculate new coordinate button
    calculate_new_coord_button = tk.Button(
    new_coord_frame,
    text="Calculate New COORD",
    command=lambda: calculate_new_coordinate(
            start_coord_entry.get(),
            int(radial_entry.get()),
            int(distance_entry.get()),
            result_entry
        )
    )
    calculate_new_coord_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    # result label
    result_label = tk.Label(new_coord_frame, text="Result", bg=current_theme['bg'], fg=current_theme['fg'])
    result_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    # Entry for result
    result_entry = tk.Entry(new_coord_frame, width=12)
    result_entry.grid(row=3, column=0, padx=5, pady=5, sticky="e")


    # Column 2: Oroginal and Sorted canvases
    column_two_frame = tk.Frame(frame, relief="raised", border=5)
    column_two_frame.grid(row=0, column=2, rowspan=5, padx=5, pady=5, sticky="nsew")
    column_two_frame.grid_rowconfigure(0, weight=1)
    column_two_frame.grid_columnconfigure(0, weight=1)

    # Original canvas
    original_canvas = tk.Canvas(column_two_frame, width=320, height=320, bg=current_theme['canvas_bg'])
    original_canvas.grid(row=0, column=0, padx=5, pady=5)


    # Sorted canvas
    sorted_canvas = tk.Canvas(column_two_frame, width=320, height=320, bg=current_theme['canvas_bg'])
    sorted_canvas.grid(row=1, column=0, padx=5, pady=5)

    # Bind Ctrl+P or Ctrl+Shift+P to paste_from_clipboard
    bind_paste_shortcuts(root, paste_and_add_line_numbers)
