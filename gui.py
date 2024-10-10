# gui.py
import tkinter as tk
import sys
import os

# Import set_theme and theme definitions from theme_utils
from utils.theme_utils import set_theme, DAY_THEME, NIGHT_THEME

from views.home_view import show_home
from views.ino_tool_view import show_ino_tool
from views.notepad_view import show_notepad
from views.todo_view import show_todo
from views.templates_view import show_templates

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_main_window():
    root = tk.Tk()
    current_theme = NIGHT_THEME  # Start with the night theme
    icon_path = get_resource_path('assets/images/ead_ops_tool_16.ico')
    root.iconbitmap(icon_path)
    root.title("EAD OPS Tool")
    root.geometry("810x750")
    root.attributes('-alpha', current_theme['window_alpha'])

    # Create a navigation bar frame
    nav_bar = tk.Frame(root, bg=current_theme['nav_bar_bg'], bd=2, relief="raise")
    nav_bar.pack(side="top", fill="x")

    # Create the main frame with the theme background
    main_frame = tk.Frame(root, bg=current_theme['bg'], bd=2, relief="raise")
    main_frame.pack(fill="both", expand=True)

    # Variable to keep track of the active button
    active_button = None

    # Define the theme toggle function BEFORE creating the theme_button
    def toggle_theme():
        nonlocal current_theme
        if current_theme == NIGHT_THEME:
            current_theme = DAY_THEME
        else:
            current_theme = NIGHT_THEME

        # Update window attributes
        root.attributes('-alpha', current_theme['window_alpha'])

        # Update backgrounds of nav_bar and main_frame
        nav_bar.config(bg=current_theme['nav_bar_bg'])
        main_frame.config(bg=current_theme['bg'])

        # Reapply theme to all widgets
        set_theme(root, current_theme)

        # Update button styles
        for btn in buttons.values():
            btn.config(bg=current_theme['button_bg'], fg=current_theme['fg'], activebackground=current_theme['button_active_bg'])

        # Update the theme button itself
        theme_button.config(bg=current_theme['button_bg'], fg=current_theme['fg'], activebackground=current_theme['button_active_bg'])

        # Update the theme button itself
        theme_button.config(bg=current_theme['button_bg'], fg=current_theme['fg'], activebackground=current_theme['button_active_bg'])

    # Now create the theme toggle button after the function is defined
    theme_button = tk.Button(nav_bar, text="Day / Night", command=toggle_theme, font=("Arial", 11, "bold"),
                             bg=current_theme['button_bg'], fg=current_theme['fg'], bd=1, relief="raised", padx=10, pady=5,
                             activebackground=current_theme['button_active_bg'])
    theme_button.pack(side="right", padx=5)

    # Define a function to update the button styles
    def highlight_button(selected_button):
        nonlocal active_button
        for btn in buttons.values():
            btn.config(bg=current_theme['button_bg'], fg=current_theme['fg'], relief="flat", bd=2)
        selected_button.config(bg=current_theme['button_active_bg'], fg=current_theme['fg'], relief="sunken")
        active_button = selected_button

    # Define hover effects
    def on_enter(e):
        e.widget['bg'] = current_theme['highlight_bg']

    def on_leave(e):
        if e.widget != active_button:
            e.widget['bg'] = current_theme['button_bg']
        else:
            e.widget['bg'] = current_theme['button_active_bg']

    # Define the commands for each button
    def show_home_view():
        show_home(root, main_frame, current_theme)
        highlight_button(buttons['Home'])
        set_theme(main_frame, current_theme)

    def show_ino_tool_view():
        show_ino_tool(root, main_frame, current_theme)
        highlight_button(buttons['INO Tool'])
        set_theme(main_frame, current_theme)

    def show_notepad_view():
        show_notepad(root, main_frame, current_theme)
        highlight_button(buttons['Notepad'])
        set_theme(main_frame, current_theme)

    def show_todo_view():
        show_todo(root, main_frame, current_theme)
        highlight_button(buttons['ToDo'])
        set_theme(main_frame, current_theme)

    def show_templates_view():
        show_templates(root, main_frame, current_theme)
        highlight_button(buttons['Templates'])
        set_theme(main_frame, current_theme)

   

    # Create buttons for navigation
    buttons = {}
    btn_names = ['Home', 'INO Tool', 'Notepad', 'ToDo', 'Templates']
    btn_commands = [show_home_view, show_ino_tool_view, show_notepad_view, show_todo_view, show_templates_view]

    for name, cmd in zip(btn_names, btn_commands):
        btn_font = ("Arial", 11, "bold")
        btn = tk.Button(nav_bar, text=name, command=cmd, font=btn_font,
                        bg=current_theme['button_bg'], fg=current_theme['fg'], bd=0, relief="raised", padx=10, pady=5,
                        activebackground=current_theme['button_active_bg'])
        btn.pack(side="left", padx=5)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        buttons[name] = btn

    # Apply theme for all widgets in the main frame (recursively)
    set_theme(root, current_theme)

    # Show the home view by default and highlight the Home button
    show_home_view()

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
