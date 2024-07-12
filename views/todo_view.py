import tkinter as tk
import json
import os

todo_file = os.path.join(os.path.dirname(__file__), "../todo.json")

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

def show_todo(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    tasks = load_tasks()

    task_listbox = tk.Listbox(frame)
    task_listbox.pack(fill="both", expand=True, padx=5, pady=5)

    for task in tasks:
        task_listbox.insert(tk.END, task)

    def add_task():
        task = task_entry.get()
        if task:
            task_listbox.insert(tk.END, task)
            tasks.append(task)
            save_tasks(tasks)
            task_entry.delete(0, tk.END)

    def remove_task():
        selected_task_index = task_listbox.curselection()
        if selected_task_index:
            task = task_listbox.get(selected_task_index)
            task_listbox.delete(selected_task_index)
            tasks.remove(task)
            save_tasks(tasks)

    task_entry = tk.Entry(frame)
    task_entry.pack(fill="x", padx=5, pady=5)

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=5)

    add_button = tk.Button(button_frame, text="Add Task", command=add_task)
    add_button.pack(side=tk.LEFT, padx=5, pady=5)

    remove_button = tk.Button(button_frame, text="Remove Task", command=remove_task)
    remove_button.pack(side=tk.LEFT, padx=5, pady=5)

# Example usage with a Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("To-Do List")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    show_todo(root, main_frame)

    root.mainloop()
