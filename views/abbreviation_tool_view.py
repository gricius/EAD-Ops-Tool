# views/abbreviation_tool_view.py
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import os
import sys
import json
from utils.button_utils import copy_to_clipboard

CONFIG_FILE = "config.json"

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

def prompt_for_excel_file():
    """Prompt the user to select the Excel file if it's not found or not specified."""
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        messagebox.showerror("Error", "No file selected. The application will exit.")
        sys.exit()  # Exit the application if no file is selected
    
    config = load_config()
    config["excel_file_path"] = file_path
    save_config(config)
    
    return file_path

def load_excel_data(file_path):
    """Load the Excel data from the given file path."""
    return pd.read_excel(file_path, sheet_name=None)

# Load configuration and Excel file
config = load_config()
excel_file = config.get("excel_file_path")
if not excel_file or not os.path.exists(excel_file):
    excel_file = prompt_for_excel_file()

# Load the Excel data
excel_data = load_excel_data(excel_file)

def search_abbreviation(abbr_text, decoded_text, result_frame):
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

        # Clear previous results
        for widget in result_frame.winfo_children():
            widget.destroy()

        if results:
            for i, (abbr, decoded, sheet_name) in enumerate(results):
                create_result_widgets(result_frame, i, abbr, decoded, sheet_name)
        else:
            tk.Label(result_frame, text="No matches found").grid(row=0, column=0)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during search: {e}")

def create_result_widgets(result_frame, index, abbr, decoded, sheet_name):
    """Create and place result widgets in the result frame."""
    tk.Label(result_frame, text=f"Abbr: {abbr}, Decoded: {decoded}, Sheet: {sheet_name}").grid(row=2 * index, column=0, sticky="w")

    copy_button = tk.Button(result_frame, text="Copy")
    copy_button.grid(row=2 * index, column=1, padx=5)
    copy_button.config(command=lambda d=decoded, b=copy_button: copy_to_clipboard(result_frame, f"({d})", b))

    # separator
    tk.Frame(result_frame, height=1, width=300, bg="black").grid(row=2 * index + 1, column=0, columnspan=2, pady=5)

def calculate_flight_level(nof_entry, uom_var, height_entry, result_entry):
    try:
        df = pd.read_excel(excel_file, sheet_name="UPPER_TABLE")
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
    tk.Label(parent, text=label_text).grid(row=row, column=column)
    entry = tk.Entry(parent, width=entry_width)
    entry.grid(row=row, column=column + 1, padx=5)
    return entry

def show_abbreviation_tool(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(frame)
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    abbr_entry = create_entry_with_label(input_frame, "Abbr.", 20, 0, 0)
    decoded_entry = create_entry_with_label(input_frame, "Decoded", 20, 1, 0)

    search_button = tk.Button(input_frame, text="Search", command=lambda: search_abbreviation(abbr_entry.get(), decoded_entry.get(), result_frame))
    search_button.grid(row=2, column=0, columnspan=2, pady=5)

    result_frame = tk.Frame(frame)
    result_frame.grid(row=1, column=0, padx=10, pady=10)

    fl_frame = tk.Frame(frame)
    fl_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    nof_entry = create_entry_with_label(fl_frame, "NOF", 10, 0, 0)
    height_entry = create_entry_with_label(fl_frame, "Height", 10, 1, 0)

    tk.Label(fl_frame, text="UOM").grid(row=0, column=2)
    uom_var = tk.StringVar(value="M")
    tk.Radiobutton(fl_frame, text="M", variable=uom_var, value="M").grid(row=0, column=3, padx=5)
    tk.Radiobutton(fl_frame, text="FT", variable=uom_var, value="FT").grid(row=0, column=4, padx=5)

    calculate_button = tk.Button(fl_frame, text="Calculate", command=lambda: calculate_flight_level(nof_entry, uom_var, height_entry, result_entry))
    calculate_button.grid(row=1, column=2, columnspan=3, pady=5)

    result_label = tk.Label(fl_frame, text="Result")
    result_label.grid(row=2, column=0)
    result_entry = tk.Entry(fl_frame, width=20)
    result_entry.grid(row=2, column=1, padx=5)

# Example usage with a Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Abbreviation Tool")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    show_abbreviation_tool(root, main_frame)

    root.mainloop()
