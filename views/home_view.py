# views/home_view.py
import tkinter as tk

def show_home(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    header = tk.Label(frame, text="Disclaimer: This application shall not be used for operations. Can be used only for testing purposes.", font=("Arial", 14))
    header.pack(pady=10)

    try:
        with open("news.txt", "r") as file:
            news_content = file.read()
    except FileNotFoundError:
        news_content = "No recent updates."

    news_label = tk.Label(frame, text=f"The following was updated recently:\n\n{news_content}", justify=tk.LEFT, wraplength=600)
    news_label.pack(pady=10)
