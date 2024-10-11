# utils/theme_utils.py
import tkinter as tk

# Define themes
DAY_THEME = {
    'bg': 'white',
    'fg': 'black',
    'button_bg': 'lightgrey',
    'button_active_bg': 'lightgreen',
    'highlight_bg': 'darkgrey',
    'nav_bar_bg': 'white',
    'window_alpha': .85,
    'canvas_bg': 'white',
    'canvas_fg': 'black',
    'point_fill_color': 'blue',
    'line_color': 'red',
    'text_color': 'black',
    'highlightbackground': 'lightgrey',
}

NIGHT_THEME = {
    'bg': 'black',
    'fg': 'white',
    'button_bg': 'black',
    'button_active_bg': 'darkgreen',
    'highlight_bg': 'grey',
    'nav_bar_bg': 'black',
    'window_alpha': 0.85,
    'canvas_bg': 'black',
    'canvas_fg': 'white',
    'point_fill_color': 'cyan',
    'line_color': 'cyan',
    'text_color': 'white',
    'highlightbackground': 'black',
}

def set_theme(widget, theme):
    """Recursively sets the background and foreground colors for all child widgets based on the theme."""
    try:
        widget_type = widget.winfo_class()
        if widget_type in ('Frame', 'LabelFrame'):
            widget.config(bg=theme['bg'])
        elif widget_type in ('Frame', 'highlightbackground'):
            widget.config(bg=theme['highlightbackground'])
        elif widget_type == 'Label':
            widget.config(bg=theme['bg'], fg=theme['fg'])
        elif widget_type == 'Button':
            widget.config(bg=theme['button_bg'], fg=theme['fg'], activebackground=theme['button_active_bg'])
        elif widget_type in ('Entry', 'Text'):
            widget.config(bg=theme['bg'], fg=theme['fg'], insertbackground=theme['fg'])
        elif widget_type == 'Canvas':
            widget.config(bg=theme['canvas_bg'])
        else:
            widget.config(bg=theme['bg'], fg=theme['fg'])
    except tk.TclError:
        pass  # Ignore widgets that don't support bg/fg configuration

    for child in widget.winfo_children():
        set_theme(child, theme)
