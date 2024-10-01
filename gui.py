import tkinter as tk
from views.home_view import show_home
from views.ino_tool_view import show_ino_tool
from views.abbreviation_tool_view import show_abbreviation_tool
from views.notepad_view import show_notepad
from views.todo_view import show_todo
from views.templates_view import show_templates

def set_theme(widget):
    """Recursively sets the black background and white font for all child widgets."""
    try:
        widget.config(bg="black", fg="white")
    except tk.TclError:
        pass  # Ignore widgets that don't support bg/fg configuration

    for child in widget.winfo_children():
        set_theme(child)

def create_main_window():
    root = tk.Tk()
    # root.iconbitmap('assets/images/purple_plane_big.ico')
    root.title("EAD OPS Tool")
    root.geometry("840x740")

    # Set transparent window
    root.attributes('-alpha', 0.9)

    # Create a menu bar
    menu_bar = tk.Menu(root, bg="black", fg="white")  # Set menu background and font colors
    root.config(menu=menu_bar)

    # Add menu items
    menu_bar.add_command(label="Home", command=lambda: show_home(root, main_frame), background="black", foreground="white")
    menu_bar.add_command(label="INO Tool", command=lambda: show_ino_tool(root, main_frame), background="black", foreground="white")
    menu_bar.add_command(label="Abbreviation Tool", command=lambda: show_abbreviation_tool(root, main_frame), background="black", foreground="white")
    menu_bar.add_command(label="Notepad", command=lambda: show_notepad(root, main_frame), background="black", foreground="white")
    menu_bar.add_command(label="ToDo", command=lambda: show_todo(root, main_frame), background="black", foreground="white")
    menu_bar.add_command(label="Templates", command=lambda: show_templates(root, main_frame), background="black", foreground="white")

    # Create the main frame with a black background
    main_frame = tk.Frame(root, bg="black")
    main_frame.pack(fill="both", expand=True)

    # Set theme for all widgets in the main frame (recursively)
    set_theme(root)

    # Show the home view by default
    show_home(root, main_frame)

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
