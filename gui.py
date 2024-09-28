# gui.py is the main file that creates the main window and the menu bar. It also imports the views and calls the functions to display the views in the main window.
import tkinter as tk
from views.home_view import show_home
from views.ino_tool_view import show_ino_tool
from views.abbreviation_tool_view import show_abbreviation_tool
from views.notepad_view import show_notepad
from views.todo_view import show_todo
from views.templates_view import show_templates

def create_main_window():
    root = tk.Tk()
    # root.iconbitmap('assets\images\plane_purple_12in sh.ico')
    root.title("EAD OPS Tool")
    root.geometry("1000x750")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Add menu items
    menu_bar.add_command(label="Home", command=lambda: show_home(root, main_frame))
    menu_bar.add_command(label="INO Tool", command=lambda: show_ino_tool(root, main_frame))
    menu_bar.add_command(label="Abbreviation Tool", command=lambda: show_abbreviation_tool(root, main_frame))
    menu_bar.add_command(label="Notepad", command=lambda: show_notepad(root, main_frame))
    menu_bar.add_command(label="ToDo", command=lambda: show_todo(root, main_frame))
    menu_bar.add_command(label="Templates", command=lambda: show_templates(root, main_frame))

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    show_home(root, main_frame)
    root.mainloop()
