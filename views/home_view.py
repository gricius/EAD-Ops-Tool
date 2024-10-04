# views/home_view.py
import tkinter as tk

def show_home(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    header = tk.Label(frame, text="Disclaimer: This application can be used only for testing purposes.", font=("Arial", 14))
    header.pack(pady=10)

    try:
        with open("news.txt", "r") as file:
            news_content = file.read()
    except FileNotFoundError:
        news_content = "No recent updates."

    news_label = tk.Label(frame, text='News, hints etc.:', font=("Arial", 12))
    news_label.pack(pady=10)

    news_label = tk.Label(frame, text=f"{news_content}", justify=tk.LEFT, wraplength=600, font=("Italic", 10))
    news_label.pack(pady=10)

    # function to show the information about the application
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


    # add a button to show modal top level window information about the application
    button = tk.Button(frame, text="About the EAD OPS Tool", command=lambda: show_info(root))
    button.pack(pady=10)