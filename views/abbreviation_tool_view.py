import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import os
import sys
import json

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
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
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
    
    # Save the selected file path to the config
    config = load_config()
    config["excel_file_path"] = file_path
    save_config(config)
    
    return file_path

# Load the configuration
config = load_config()
excel_file = config.get("excel_file_path")

# Check if the stored file path exists, if not prompt the user to select a file
if not excel_file or not os.path.exists(excel_file):
    excel_file = prompt_for_excel_file()

def copy_to_clipboard(text, widget):
    """Copy the provided text to the clipboard."""
    widget.clipboard_clear()
    widget.clipboard_append(text)
    widget.update()  # Keeps the clipboard content after the window is closed

def search_abbreviation(abbr_text, decoded_text, result_frame):
    try:
        df = pd.read_excel(excel_file, sheet_name=None)
        results = []

        abbr_text = abbr_text.lower()
        decoded_text = decoded_text.lower()

        if abbr_text:
            for sheet_name, sheet_df in df.items():
                matches = sheet_df[sheet_df.iloc[:, 0].astype(str).str.lower().str.contains(abbr_text, na=False)]
                for _, row in matches.iterrows():
                    results.append((row.iloc[0], row.iloc[1], sheet_name))

        if decoded_text:
            for sheet_name, sheet_df in df.items():
                matches = sheet_df[sheet_df.iloc[:, 1].astype(str).str.lower().str.contains(decoded_text, na=False)]
                for _, row in matches.iterrows():
                    results.append((row.iloc[0], row.iloc[1], sheet_name))

        # Clear previous results
        for widget in result_frame.winfo_children():
            widget.destroy()

        if results:
            for i, (abbr, decoded, sheet_name) in enumerate(results):
                tk.Label(result_frame, text=f"Abbr: {abbr}, Decoded: {decoded}, Sheet: {sheet_name}").grid(row=i, column=0, sticky="w")
                tk.Button(result_frame, text="Copy", command=lambda d=decoded: copy_to_clipboard(f"[{d}]", result_frame)).grid(row=i, column=1, padx=5)
        else:
            tk.Label(result_frame, text="No matches found").grid(row=0, column=0)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def calculate_flight_level(nof_entry, uom_var, height_entry, result_entry):
    try:
        df = pd.read_excel(excel_file, sheet_name="UPPER_TABLE")
        nof_value = nof_entry.get().strip().upper()
        height_value = height_entry.get().strip()
        uom_value = uom_var.get()

        if len(nof_value) < 1 or len(nof_value) > 4:
            raise ValueError("NOF must be between 1 and 4 characters long")

        result = df[df.iloc[:, 0].str.upper() == nof_value]

        if result.empty:
            result_entry.delete(0, tk.END)
            result_entry.insert(0, "No match found")
            return

        if not height_value:
            selected_value = result.iloc[0, 5]  # Column F
        else:
            height_value = float(height_value)
            if uom_value == "M":
                selected_value = result.iloc[0, 3]  # Column D
                selected_value += height_value
                selected_value = selected_value / 0.31  # Convert to feet
            elif uom_value == "FT":
                selected_value = result.iloc[0, 4]  # Column E
                selected_value += height_value
            selected_value = selected_value / 100  # Convert to hundreds of feet

        result_entry.delete(0, tk.END)
        result_entry.insert(0, f"{selected_value:.0f}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_abbreviation_tool(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(frame)
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    tk.Label(input_frame, text="Abbr.").grid(row=0, column=0)
    abbr_entry = tk.Entry(input_frame, width=20)
    abbr_entry.grid(row=0, column=1, padx=5)

    tk.Label(input_frame, text="Decoded").grid(row=1, column=0)
    decoded_entry = tk.Entry(input_frame, width=20)
    decoded_entry.grid(row=1, column=1, padx=5)

    search_button = tk.Button(input_frame, text="Search", command=lambda: search_abbreviation(abbr_entry.get(), decoded_entry.get(), result_frame))
    search_button.grid(row=2, column=0, columnspan=2, pady=5)

    result_frame = tk.Frame(frame)
    result_frame.grid(row=1, column=0, padx=10, pady=10)

    # Flight Level Calculator
    fl_frame = tk.Frame(frame)
    fl_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    tk.Label(fl_frame, text="NOF").grid(row=0, column=0)
    nof_entry = tk.Entry(fl_frame, width=10)
    nof_entry.grid(row=0, column=1, padx=5)

    tk.Label(fl_frame, text="UOM").grid(row=0, column=2)
    uom_var = tk.StringVar(value="M")
    uom_m = tk.Radiobutton(fl_frame, text="M", variable=uom_var, value="M")
    uom_m.grid(row=0, column=3, padx=5)
    uom_ft = tk.Radiobutton(fl_frame, text="FT", variable=uom_var, value="FT")
    uom_ft.grid(row=0, column=4, padx=5)

    tk.Label(fl_frame, text="Height").grid(row=1, column=0)
    height_entry = tk.Entry(fl_frame, width=10)
    height_entry.grid(row=1, column=1, padx=5)

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
