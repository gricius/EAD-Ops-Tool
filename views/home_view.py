# views/home_view.py
import tkinter as tk
import pandas as pd
import os
from tkinter import scrolledtext, messagebox
from datetime import datetime

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
    else:
        news_file_path = "Y:/99. Operator Folders/FRA/AG/news.xlsx"

    try:
        if os.path.exists(news_file_path):
            df = pd.read_excel(news_file_path, sheet_name="Sheet1")

            # Ensure the required columns are present
            expected_columns = {'Date', 'App', 'type', 'message'}
            actual_columns = set(df.columns)
            if not expected_columns.issubset(actual_columns):
                missing = expected_columns - actual_columns
                raise ValueError(f"Excel file is missing required columns: {missing}")

            # Convert 'Date' column to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df['Date']):
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
        else:
            news_content = "No recent updates."
    except Exception as e:
        news_content = f"Error reading news: {e}"

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
        text_widget.insert("end", "- Abbreviation tool for decoding abbreviations.\n", "normal")
        text_widget.insert("end", "- A point calculation based on a given COORD, radial and a distance.\n\n", "normal")

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

    # Function to report an issue
    def show_report_issue(parent):
        # Create the Toplevel window
        report_window = tk.Toplevel(parent)
        report_window.title("Report an Issue")

        # Create a frame for the input
        input_frame = tk.Frame(report_window)
        input_frame.pack(pady=10, padx=10)

        # Label for the input
        input_label = tk.Label(input_frame, text="Describe the issue:")
        input_label.pack(anchor='w')

        # Text widget for inputting the issue
        issue_text = tk.Text(input_frame, wrap='word', width=80, height=10)
        issue_text.pack()

        # Submit button
        submit_button = tk.Button(input_frame, text="Submit Issue", command=lambda: submit_issue())
        submit_button.pack(pady=5)

        # Function to handle submission
        def submit_issue():
            issue = issue_text.get("1.0", tk.END).strip()
            if issue:
                # Determine the path to issues.xlsx
                if os.path.exists("issues.xlsx"):
                    issues_file_path = "issues.xlsx"
                else:
                    issues_file_path = "Y:/99. Operator Folders/FRA/AG/issues.xlsx"

                # Get current date and time
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Create or append to the Excel file
                if os.path.exists(issues_file_path):
                    # Read existing issues
                    issues_df = pd.read_excel(issues_file_path)
                else:
                    # Create a new DataFrame
                    issues_df = pd.DataFrame(columns=['Date', 'Issue', 'Status'])

                # Append the new issue with Status
                new_issue = {'Date': now, 'Issue': issue, 'Status': 'Submitted'}
                new_issue_df = pd.DataFrame([new_issue])
                issues_df = pd.concat([issues_df, new_issue_df], ignore_index=True)

                # Save back to Excel
                issues_df.to_excel(issues_file_path, index=False)

                # Clear the input
                issue_text.delete("1.0", tk.END)

                # Refresh the issues display
                display_issues()
            else:
                messagebox.showwarning("Input Error", "Please enter an issue before submitting.")

        # ScrolledText widget to display the issues
        issues_text = scrolledtext.ScrolledText(report_window, wrap='word', width=80, height=20)
        issues_text.pack(pady=10, padx=10)

        # Configure text tags for underlining
        issues_text.tag_configure("underline", font=("Arial", 11, "underline", "bold"))

        # Function to display issues
        def display_issues():
            # Determine the path to issues.xlsx
            if os.path.exists("issues.xlsx"):
                issues_file_path = "issues.xlsx"
            else:
                issues_file_path = "Y:/99. Operator Folders/FRA/AG/issues.xlsx"

            # Check if the file exists
            if os.path.exists(issues_file_path):
                # Read the issues
                issues_df = pd.read_excel(issues_file_path)

                # Ensure 'Status' column exists
                if 'Status' not in issues_df.columns:
                    issues_df['Status'] = 'Submitted'

                # Clear the text widget
                issues_text.config(state='normal')
                issues_text.delete("1.0", tk.END)

                # Display issues with all columns and separator
                separator = "-" * 80  # Separator line

                for index, row in issues_df.iterrows():
                    date = row['Date']
                    issue = row['Issue']
                    status = row['Status']

                    # Insert Date
                    issues_text.insert(tk.END, f"Date: {date}\n")

                    # Insert Issue label with underline
                    issues_text.insert(tk.END, "Issue: ", "underline")
                    issues_text.insert(tk.END, f"{issue}\n")

                    # Insert Status label with underline
                    issues_text.insert(tk.END, "Status: ", "underline")
                    issues_text.insert(tk.END, f"{status}\n")

                    # Insert Separator
                    issues_text.insert(tk.END, f"{separator}\n\n")

                issues_text.config(state='disabled')
            else:
                issues_text.config(state='normal')
                issues_text.delete("1.0", tk.END)
                issues_text.insert(tk.END, "No issues reported yet.")
                issues_text.config(state='disabled')

        # Initially display the issues
        display_issues()

    # Create a frame for the buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    # Add the "About the EAD OPS Tool" button
    about_button = tk.Button(
        button_frame,
        text="About the EAD OPS Tool",
        command=lambda: show_info(root)
    )
    about_button.pack(side='left', padx=5)

    # Add the "Report an Issue" button
    report_button = tk.Button(
        button_frame,
        text="Report an Issue",
        command=lambda: show_report_issue(root)
    )
    report_button.pack(side='left', padx=5)
