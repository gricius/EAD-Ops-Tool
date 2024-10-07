# views/todo_view.py
import tkinter as tk
import json
import os

# Determine the user's home directory
home_dir = os.path.expanduser('~')

# Define the application data directory
app_data_dir = os.path.join(home_dir, '.ead_ops_tool')

# Ensure the application data directory exists
if not os.path.exists(app_data_dir):
    os.makedirs(app_data_dir)

# Define the path to the todo.json file
todo_file = os.path.join(app_data_dir, 'todo.json')

def load_tasks():
    try:
        with open(todo_file, "r") as file:
            tasks = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []
    return tasks

def save_tasks(tasks):
    with open(todo_file, "w") as file:
        json.dump(tasks, file)

def show_todo(root, main_frame, current_theme):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    root.title("EAD OPS Tool - ToDo")

    frame = tk.Frame(main_frame, bd=2, relief="groove")
    frame.pack(fill="both", expand=True)

    tasks = load_tasks()

    task_listbox = tk.Listbox(frame)
    task_listbox.pack(fill="both", expand=True, padx=5, pady=5)

    for task in tasks:
        task_listbox.insert(tk.END, task)
        # add separator
        task_listbox.insert(tk.END, "-" * 50)

    def add_task():
        task = task_entry.get()
        if task:
            task_listbox.insert(tk.END, task)
            task_listbox.insert(tk.END, "-" * 50)
            tasks.append(task)
            save_tasks(tasks)
            task_entry.delete(0, tk.END)

    def remove_task():
        selected_indices = task_listbox.curselection()
        if selected_indices:
            # Remove selected items and their separators
            for index in reversed(selected_indices):
                task_listbox.delete(index)
                if index < task_listbox.size() and task_listbox.get(index) == "-" * 50:
                    task_listbox.delete(index)
            # Update tasks
            tasks[:] = [task_listbox.get(i) for i in range(0, task_listbox.size(), 2)]
            save_tasks(tasks)

    task_entry = tk.Entry(frame, bd=2, relief="groove")
    task_entry.pack(fill="x", padx=5, pady=5)

    button_frame = tk.Frame(frame, bd=2, relief="groove")
    button_frame.pack(pady=5)

    add_button = tk.Button(button_frame, text="Add Task", command=add_task)
    add_button.pack(side=tk.LEFT, padx=5, pady=5)

    remove_button = tk.Button(button_frame, text="Remove Task", command=remove_task)
    remove_button.pack(side=tk.LEFT, padx=5, pady=5)
