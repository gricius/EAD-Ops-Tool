import tkinter as tk
from views.home_view import show_home
from views.ino_tool_view import show_ino_tool
# from views.abbreviation_tool_view import show_abbreviation_tool
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
    root.geometry("800x750")

    # Set transparent window
    root.attributes('-alpha', 0.85)

    # Create a navigation bar frame
    nav_bar = tk.Frame(root, bg="black")
    nav_bar.pack(side="top", fill="x")

    # Create the main frame with a black background
    main_frame = tk.Frame(root, bg="black")
    main_frame.pack(fill="both", expand=True)

    # Variable to keep track of the active button
    active_button = None

    # Define a function to update the button styles
    def highlight_button(selected_button):
        nonlocal active_button
        for btn in buttons.values():
            btn.config(bg="black", fg="white", relief="flat")
        selected_button.config(bg="grey", fg="white", relief="sunken")
        active_button = selected_button

    # Define hover effects
    def on_enter(e):
        e.widget['bg'] = 'darkgrey'

    def on_leave(e):
        if e.widget != active_button:
            e.widget['bg'] = 'black'
        else:
            e.widget['bg'] = 'grey'

    # Define the commands for each button
    def show_home_view():
        show_home(root, main_frame)
        highlight_button(buttons['Home'])

    def show_ino_tool_view():
        show_ino_tool(root, main_frame)
        highlight_button(buttons['INO Tool'])

    # def show_abbreviation_tool_view():
    #     show_abbreviation_tool(root, main_frame)
    #     highlight_button(buttons['Abbreviation Tool'])

    def show_notepad_view():
        show_notepad(root, main_frame)
        highlight_button(buttons['Notepad'])

    def show_todo_view():
        show_todo(root, main_frame)
        highlight_button(buttons['ToDo'])

    def show_templates_view():
        show_templates(root, main_frame)
        highlight_button(buttons['Templates'])

    # Create buttons for navigation
    buttons = {}
    btn_names = ['Home', 'INO Tool', 'Notepad', 'ToDo', 'Templates'] # 'Abbreviation Tool',
    btn_commands = [show_home_view, show_ino_tool_view, show_notepad_view, show_todo_view, show_templates_view] # show_abbreviation_tool_view,

    for name, cmd in zip(btn_names, btn_commands):
        btn_font = ("Arial", 11, "bold")
        btn = tk.Button(nav_bar, text=name, command=cmd, font=btn_font, bg="black", fg="white", bd=0, relief="flat", padx=10, pady=5)
        btn.pack(side="left", padx=5)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        buttons[name] = btn

    # Set theme for all widgets in the main frame (recursively)
    set_theme(root)

    # Show the home view by default and highlight the Home button
    show_home_view()

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
