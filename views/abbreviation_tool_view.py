import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

# Load the Excel file
excel_file = os.path.join(os.path.dirname(__file__), "../Abbreviation and Elevation Tool.xlsx")

def search_abbreviation(abbr_text, decoded_text, result_text):
    try:
        df = pd.read_excel(excel_file, sheet_name=None)
        results = []

        abbr_text = abbr_text.lower()
        decoded_text = decoded_text.lower()

        if abbr_text:
            for sheet_name, sheet_df in df.items():
                matches = sheet_df[sheet_df.iloc[:, 0].astype(str).str.lower().str.contains(abbr_text, na=False)]
                for _, row in matches.iterrows():
                    results.append(f"Abbr: {row.iloc[0]}, Decoded: {row.iloc[1]}, Sheet: {sheet_name}")

        if decoded_text:
            for sheet_name, sheet_df in df.items():
                matches = sheet_df[sheet_df.iloc[:, 1].astype(str).str.lower().str.contains(decoded_text, na=False)]
                for _, row in matches.iterrows():
                    results.append(f"Abbr: {row.iloc[0]}, Decoded: {row.iloc[1]}, Sheet: {sheet_name}")

        result_text.delete("1.0", tk.END)
        if results:
            result_text.insert(tk.END, "\n".join(results))
        else:
            result_text.insert(tk.END, "No matches found")

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

    search_button = tk.Button(input_frame, text="Search", command=lambda: search_abbreviation(abbr_entry.get(), decoded_entry.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=5)

    result_text = tk.Text(frame, height=15, width=80)
    result_text.grid(row=1, column=0, padx=10, pady=10)
