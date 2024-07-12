import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import json

TEMPLATES_DIR = "templates"
ORDER_FILE = "templates_order.json"

if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

def load_template_order():
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "r") as file:
            return json.load(file)
    return []

def save_template_order(order):
    with open(ORDER_FILE, "w") as file:
        json.dump(order, file)

def show_templates(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    def open_editor(template_name=None):
        editor_window = tk.Toplevel(root)
        editor_window.title("Template Editor")

        text_editor = tk.Text(editor_window, wrap=tk.WORD, width=80, height=20)
        text_editor.pack(padx=10, pady=10)

        if template_name:
            with open(os.path.join(TEMPLATES_DIR, f"{template_name}.json"), "r") as file:
                text_editor.insert(tk.END, json.load(file)["content"])

        def save_template():
            name = simpledialog.askstring("Template Name", "Enter the name for the template:")
            if name:
                content = text_editor.get("1.0", tk.END)
                template = {"name": name, "content": content}
                with open(os.path.join(TEMPLATES_DIR, f"{name}.json"), "w") as file:
                    json.dump(template, file)
                messagebox.showinfo("Success", f"Template '{name}' saved successfully.")
                editor_window.destroy()
                show_templates(root, main_frame)

        def cancel_editor():
            editor_window.destroy()

        save_button = tk.Button(editor_window, text="Save", command=save_template)
        save_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = tk.Button(editor_window, text="Cancel", command=cancel_editor)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def copy_template(template_name):
        with open(os.path.join(TEMPLATES_DIR, f"{template_name}.json"), "r") as file:
            template_content = json.load(file)["content"]
        root.clipboard_clear()
        root.clipboard_append(template_content)
        messagebox.showinfo("Copied", f"Template '{template_name}' copied to clipboard.")

    def edit_template(template_name):
        open_editor(template_name)

    def delete_template(template_name):
        if messagebox.askyesno("Delete", f"Are you sure you want to delete the template '{template_name}'?"):
            os.remove(os.path.join(TEMPLATES_DIR, f"{template_name}.json"))
            order = load_template_order()
            order.remove(template_name)
            save_template_order(order)
            messagebox.showinfo("Deleted", f"Template '{template_name}' deleted successfully.")
            show_templates(root, main_frame)

    def move_template_up(template_name):
        order = load_template_order()
        idx = order.index(template_name)
        if idx > 0:
            order[idx], order[idx - 1] = order[idx - 1], order[idx]
            save_template_order(order)
            show_templates(root, main_frame)

    def move_template_down(template_name):
        order = load_template_order()
        idx = order.index(template_name)
        if idx < len(order) - 1:
            order[idx], order[idx + 1] = order[idx + 1], order[idx]
            save_template_order(order)
            show_templates(root, main_frame)

    new_template_button = tk.Button(frame, text="New template", command=lambda: open_editor())
    new_template_button.pack(pady=10)

    templates_list = tk.Frame(frame)
    templates_list.pack(fill="both", expand=True, padx=10, pady=10)

    templates = [f.split(".")[0] for f in os.listdir(TEMPLATES_DIR) if f.endswith(".json")]
    order = load_template_order()

    if not order:
        order = templates
        save_template_order(order)
    else:
        for template in templates:
            if template not in order:
                order.append(template)
                save_template_order(order)

    for template in order:
        if template in templates:
            template_frame = tk.Frame(templates_list)
            template_frame.pack(fill="x", pady=5)

            template_label = tk.Label(template_frame, text=template, anchor="w")
            template_label.pack(side=tk.LEFT, fill="x", expand=True)

            copy_button = tk.Button(template_frame, text="Copy", command=lambda t=template: copy_template(t))
            copy_button.pack(side=tk.LEFT, padx=5)

            edit_button = tk.Button(template_frame, text="Edit", command=lambda t=template: edit_template(t))
            edit_button.pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(template_frame, text="Delete", command=lambda t=template: delete_template(t))
            delete_button.pack(side=tk.LEFT, padx=5)

            up_button = tk.Button(template_frame, text="Up", command=lambda t=template: move_template_up(t))
            up_button.pack(side=tk.LEFT, padx=5)

            down_button = tk.Button(template_frame, text="Down", command=lambda t=template: move_template_down(t))
            down_button.pack(side=tk.LEFT, padx=5)

# Example usage with a Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Templates")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    show_templates(root, main_frame)

    root.mainloop()
