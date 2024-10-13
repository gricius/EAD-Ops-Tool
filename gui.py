# gui.py
import tkinter as tk
import sys
import os
import json
from pathlib import Path

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

# Define the path to the configuration file
CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Config file is corrupted. Loading default settings.")
    return {}

def save_config(config):
    """Save configuration to the config file."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")

def create_main_window():
    root = tk.Tk()
    
    # Load configuration
    config = load_config()
    saved_theme = config.get("theme", "day")  # Default to 'day' if not set
    
    # Set the current theme based on the saved configuration
    if saved_theme == "night":
        current_theme = NIGHT_THEME
    else:
        current_theme = DAY_THEME
    
    # Set window icon
    icon_path = get_resource_path('assets/images/ead_ops_tool_16.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Icon file not found at {icon_path}. Skipping icon setting.")
    
    root.title("EAD OPS Tool")
    root.geometry("830x750")
    root.attributes('-alpha', current_theme.get('window_alpha', 1.0))

    # Create a navigation bar frame
    nav_bar = tk.Frame(root, bg=current_theme.get('nav_bar_bg', '#FFFFFF'), bd=2, relief="raised")
    nav_bar.pack(side="top", fill="x")

    # Create the main frame with the theme background
    main_frame = tk.Frame(root, bg=current_theme.get('bg', '#FFFFFF'), bd=2, relief="raised")
    main_frame.pack(fill="both", expand=True)

    # Variable to keep track of the active button and current view
    active_button = None
    current_view = None  # This will hold the function reference of the active view

    # Define the theme toggle function BEFORE creating the theme_button
    def toggle_theme():
        nonlocal current_theme, config, current_view
        # Toggle the theme
        if current_theme == NIGHT_THEME:
            current_theme = DAY_THEME
            config['theme'] = 'day'
        else:
            current_theme = NIGHT_THEME
            config['theme'] = 'night'

        # Update window attributes
        root.attributes('-alpha', current_theme.get('window_alpha', 1.0))

        # Update backgrounds of nav_bar and main_frame
        nav_bar.config(bg=current_theme.get('nav_bar_bg', '#FFFFFF'))
        main_frame.config(bg=current_theme.get('bg', '#FFFFFF'))

        # Reapply theme to all widgets
        set_theme(root, current_theme)

        # Update button styles
        for btn in buttons.values():
            btn.config(
                bg=current_theme.get('button_bg', '#F0F0F0'),
                fg=current_theme.get('fg', '#000000'),
                activebackground=current_theme.get('button_active_bg', '#D0D0D0')
            )

        # Update the theme button itself
        theme_button.config(
            bg=current_theme.get('button_bg', '#F0F0F0'),
            fg=current_theme.get('fg', '#000000'),
            activebackground=current_theme.get('button_active_bg', '#D0D0D0')
        )

        # Highlight the currently active button to maintain UI consistency
        if active_button:
            highlight_button(active_button)

        # Reload the current view to apply the new theme
        if current_view:
            current_view()

        # Save the updated configuration
        save_config(config)

    # Now create the theme toggle button after the function is defined
    theme_button = tk.Button(
        nav_bar, 
        text="Day / Night", 
        command=toggle_theme, 
        font=("Arial", 11, "bold"),
        bg=current_theme.get('button_bg', '#F0F0F0'), 
        fg=current_theme.get('fg', '#000000'), 
        bd=1, 
        relief="raised", 
        padx=10, 
        pady=5,
        activebackground=current_theme.get('button_active_bg', '#D0D0D0')
    )
    theme_button.pack(side="right", padx=5)

    # Define a function to update the button styles
    def highlight_button(selected_button):
        nonlocal active_button
        for btn in buttons.values():
            btn.config(
                bg=current_theme.get('button_bg', '#F0F0F0'),
                fg=current_theme.get('fg', '#000000'),
                relief="flat",
                bd=2
            )
        selected_button.config(
            bg=current_theme.get('button_active_bg', '#D0D0D0'),
            fg=current_theme.get('fg', '#000000'),
            relief="sunken"
        )
        active_button = selected_button

    # Define hover effects
    def on_enter(e):
        e.widget['bg'] = current_theme.get('highlight_bg', '#E0E0E0')

    def on_leave(e):
        if e.widget != active_button:
            e.widget['bg'] = current_theme.get('button_bg', '#F0F0F0')
        else:
            e.widget['bg'] = current_theme.get('button_active_bg', '#D0D0D0')

    # Define the commands for each button
    def show_home_view():
        nonlocal current_view
        show_home(root, main_frame, current_theme)
        highlight_button(buttons['Home'])
        set_theme(main_frame, current_theme)
        current_view = show_home_view  # Set current_view to this function

    def show_ino_tool_view():
        nonlocal current_view
        show_ino_tool(root, main_frame, current_theme)
        highlight_button(buttons['INO Tool'])
        set_theme(main_frame, current_theme)
        current_view = show_ino_tool_view  # Set current_view to this function

    def show_notepad_view():
        nonlocal current_view
        show_notepad(root, main_frame, current_theme)
        highlight_button(buttons['Notepad'])
        set_theme(main_frame, current_theme)
        current_view = show_notepad_view  # Set current_view to this function

    def show_todo_view():
        nonlocal current_view
        show_todo(root, main_frame, current_theme)
        highlight_button(buttons['ToDo'])
        set_theme(main_frame, current_theme)
        current_view = show_todo_view  # Set current_view to this function

    def show_templates_view():
        nonlocal current_view
        show_templates(root, main_frame, current_theme)
        highlight_button(buttons['Templates'])
        set_theme(main_frame, current_theme)
        current_view = show_templates_view  # Set current_view to this function

    # Create buttons for navigation
    buttons = {}
    btn_names = ['Home', 'INO Tool', 'Notepad', 'ToDo', 'Templates']
    btn_commands = [show_home_view, show_ino_tool_view, show_notepad_view, show_todo_view, show_templates_view]

    for name, cmd in zip(btn_names, btn_commands):
        btn_font = ("Arial", 11, "bold")
        btn = tk.Button(
            nav_bar, 
            text=name, 
            command=cmd, 
            font=btn_font,
            bg=current_theme.get('button_bg', '#F0F0F0'), 
            fg=current_theme.get('fg', '#000000'), 
            bd=0, 
            relief="raised", 
            padx=10, 
            pady=5,
            activebackground=current_theme.get('button_active_bg', '#D0D0D0')
        )
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
