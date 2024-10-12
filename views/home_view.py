# views/home_view.py
import tkinter as tk
import pandas as pd
import os
from tkinter import scrolledtext  # Import ScrolledText for better text display

def show_home(root, main_frame, current_theme):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    root.title("EAD OPS Tool")

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    header = tk.Label(
        frame, 
        text="Disclaimer: This application can be used only for testing purposes.", 
        font=("Arial", 14)
    )
    header.pack(pady=10)

    # Determine the path to news.xlsx
    if os.path.exists("news.xlsx"):
        news_file_path = "news.xlsx"
        print("Using local news.xlsx file.")
    else:
        news_file_path = "Y:/99.Operator Folders/FRA/AG/news.xlsx"
        print("Local news.xlsx not found. Using network path:", news_file_path)

    try:
        if os.path.exists(news_file_path):
            print(f"Reading news from: {news_file_path}")
            # Read the Excel file using pandas
            df = pd.read_excel(news_file_path, sheet_name="Sheet1")
            print("Excel file read successfully.")

            # Ensure the required columns are present
            expected_columns = {'Date', 'App', 'type', 'message'}
            actual_columns = set(df.columns)
            print("Columns in Excel file:", actual_columns)
            if not expected_columns.issubset(actual_columns):
                missing = expected_columns - actual_columns
                raise ValueError(f"Excel file is missing required columns: {missing}")

            # Convert 'Date' column to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                print("Converting 'Date' column to datetime.")
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Drop rows where all elements are NaN
            df.dropna(how='all', inplace=True)

            # Sort the news by Date in descending order (latest first)
            df.sort_values(by='Date', ascending=False, inplace=True)

            # Format the news content
            news_content = ""
            for _, row in df.iterrows():
                date = row['Date'].strftime('%Y-%m-%d') if pd.notnull(row['Date']) else "N/A"
                app = row['App'] if pd.notnull(row['App']) else "N/A"
                type_ = row['type'] if pd.notnull(row['type']) else "N/A"
                message = row['message'] if pd.notnull(row['message']) else ""
                news_content += f"{date} - {app} - {type_}: {message}\n"

            if not news_content.strip():
                news_content = "No recent updates."
                print("News content is empty after processing.")
            else:
                print("News content formatted successfully.")
        else:
            print("News file does not exist at:", news_file_path)
            news_content = "No recent updates."
    except Exception as e:
        news_content = f"Error reading news: {e}"
        print(news_content)

    # Title for the news section
    news_label_title = tk.Label(
        frame, 
        text='News, hints etc.:', 
        font=("Arial", 12)
    )
    news_label_title.pack(pady=10)

    # Display the news content using ScrolledText for better handling of large content
    news_text = scrolledtext.ScrolledText(
        frame, 
        wrap=tk.WORD, 
        width=80, 
        height=20, 
        font=("Arial", 10, "italic"), 
        bg=current_theme['bg'], 
        fg=current_theme['fg']
    )
    news_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # Insert the news content
    news_text.insert(tk.END, news_content)

    # Make the text read-only
    news_text.config(state='disabled')

    # Function to show the information about the application
    def show_info(parent):
        info_window = tk.Toplevel(parent)
        info_window.title("About the EAD OPS Tool")

        # Create a Text widget
        text_widget = tk.Text(info_window, wrap="word", width=70, height=32)
        text_widget.pack(pady=10)

        # Define text styles (tags)
        text_widget.tag_configure("title", font=("Arial", 14, "bold"))
        text_widget.tag_configure("section", font=("Arial", 12, "bold"))
        text_widget.tag_configure("normal", font=("Arial", 11), lmargin1=10, lmargin2=20)
        text_widget.tag_configure("italic", font=("Arial", 11, "italic"))

        # Insert styled text
        text_widget.insert("end", "EAD OPS Tool\n", "title")
        text_widget.insert("end", "Created by operations staff to assist in daily tasks.\n\n", "normal")

        text_widget.insert("end", "Home\n", "section")
        text_widget.insert("end", "- Shows information about the application and news.\n", "normal")
        text_widget.insert("end", "- Potentially info about important staff information.\n\n", "normal")

        text_widget.insert("end", "INO Tool\n", "section")
        text_widget.insert("end", "- Coordinates formatting for INO Polygon function, plotting on a map containing various airspace information.\n", "normal")
        text_widget.insert("end", "- Distance conversion between different units.\n", "normal")
        text_widget.insert("end", "- Flight level conversion between different units.\n", "normal")
        text_widget.insert("end", "- Abbreviation tool for decoding abbreviations.\n\n", "normal")

        text_widget.insert("end", "ToDo\n", "section")
        text_widget.insert("end", "- Simple todo or notes list. Add and remove tasks.\n\n", "normal")

        text_widget.insert("end", "Notepad\n", "section")
        text_widget.insert("end", "- Simple notepad for text formatting for item E. Removes not allowed characters, etc.\n", "normal")
        text_widget.insert("end", "  The notepad resets after closing or switching to another tool.\n\n", "normal")

        text_widget.insert("end", "Templates\n", "section")
        text_widget.insert("end", "- Tool for creating, editing, and saving text templates. Copy button copies the template to the clipboard.\n\n", "normal")

        text_widget.insert("end", "The application is still in development, and new features will be added in the future.\n", "normal")
        text_widget.insert("end", "If you have any suggestions or found a bug, please contact AG.\n\n", "normal")
        text_widget.insert("end", "TKS IN ADV,", "italic")
        text_widget.insert("end", "BRGDS AG :)", "italic")

        # Disable editing
        text_widget.config(state="disabled")

    # Add a button to show modal top-level window information about the application
    button = tk.Button(
        frame, 
        text="About the EAD OPS Tool", 
        command=lambda: show_info(root)
    )
    button.pack(pady=10)
