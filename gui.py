import tkinter as tk
from views.home_view import show_home
from views.ino_tool_view import show_ino_tool
from views.notepad_view import show_notepad
from views.todo_view import show_todo
from views.templates_view import show_templates
import sys
import os

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Define themes
DAY_THEME = {
    'bg': 'white',
    'fg': 'black',
    'button_bg': 'lightgrey',
    'button_active_bg': 'grey',
    'highlight_bg': 'darkgrey',
    'nav_bar_bg': 'white',
    'window_alpha': 1.0,
    'canvas_bg': 'white',
    'canvas_fg': 'black',
    'point_fill_color': 'blue',
    'line_color': 'blue',
    'text_color': 'black',
}

NIGHT_THEME = {
    'bg': 'black',
    'fg': 'white',
    'button_bg': 'black',
    'button_active_bg': 'darkgrey',
    'highlight_bg': 'grey',
    'nav_bar_bg': 'black',
    'window_alpha': 0.85,
    'canvas_bg': 'black',
    'canvas_fg': 'white',
    'point_fill_color': 'cyan',
    'line_color': 'cyan',
    'text_color': 'white',
}


def set_theme(widget, theme):
    """Recursively sets the background and foreground colors for all child widgets based on the theme."""
    try:
        widget_type = widget.winfo_class()
        if widget_type in ('Frame', 'LabelFrame'):
            widget.config(bg=theme['bg'])
        elif widget_type == 'Label':
            widget.config(bg=theme['bg'], fg=theme['fg'])
        elif widget_type == 'Button':
            widget.config(bg=theme['button_bg'], fg=theme['fg'], activebackground=theme['button_active_bg'])
        elif widget_type in ('Entry', 'Text'):
            widget.config(bg=theme['bg'], fg=theme['fg'], insertbackground=theme['fg'])
        elif widget_type == 'Canvas':
            widget.config(bg=theme['canvas_bg'])
            # Optionally, you can clear and redraw the canvas here if needed
        else:
            widget.config(bg=theme['bg'], fg=theme['fg'])
    except tk.TclError:
        pass  # Ignore widgets that don't support bg/fg configuration

    for child in widget.winfo_children():
        set_theme(child, theme)

def create_main_window():
    root = tk.Tk()
    current_theme = NIGHT_THEME  # Start with the night theme
    icon_path = get_resource_path('assets/images/ead_ops_tool_32.ico')
    root.iconbitmap(icon_path)
    root.title("EAD OPS Tool")
    root.geometry("800x750")
    root.attributes('-alpha', current_theme['window_alpha'])

    # Create a navigation bar frame
    nav_bar = tk.Frame(root, bg=current_theme['nav_bar_bg'])
    nav_bar.pack(side="top", fill="x")

    # Create the main frame with the theme background
    main_frame = tk.Frame(root, bg=current_theme['bg'])
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
                             bg=current_theme['button_bg'], fg=current_theme['fg'], bd=0, relief="flat", padx=10, pady=5,
                             activebackground=current_theme['button_active_bg'])
    theme_button.pack(side="right", padx=5)

    # Define a function to update the button styles
    def highlight_button(selected_button):
        nonlocal active_button
        for btn in buttons.values():
            btn.config(bg=current_theme['button_bg'], fg=current_theme['fg'], relief="flat")
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
        show_home(root, main_frame)
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
        show_todo(root, main_frame)
        highlight_button(buttons['ToDo'])
        set_theme(main_frame, current_theme)

    def show_templates_view():
        show_templates(root, main_frame)
        highlight_button(buttons['Templates'])
        set_theme(main_frame, current_theme)

    # Create buttons for navigation
    buttons = {}
    btn_names = ['Home', 'INO Tool', 'Notepad', 'ToDo', 'Templates']
    btn_commands = [show_home_view, show_ino_tool_view, show_notepad_view, show_todo_view, show_templates_view]

    for name, cmd in zip(btn_names, btn_commands):
        btn_font = ("Arial", 11, "bold")
        btn = tk.Button(nav_bar, text=name, command=cmd, font=btn_font,
                        bg=current_theme['button_bg'], fg=current_theme['fg'], bd=0, relief="flat", padx=10, pady=5,
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
