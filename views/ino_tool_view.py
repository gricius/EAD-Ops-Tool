import tkinter as tk
from utils.clipboard_utils import paste_from_clipboard
from utils.drawing_utils import show_on_map
from utils.button_utils import copy_to_clipboard

def show_ino_tool(root, main_frame):
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(frame)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    paste_coord_button = tk.Button(input_frame, text="Paste COORD", command=lambda: paste_from_clipboard(root, source_text, original_text, sorted_text, original_canvas, sorted_canvas, original_frame))
    paste_coord_button.grid(row=0, column=0, padx=5, pady=5)

    # clear the text area on click
    source_text = tk.Text(input_frame, height=20, width=30)
    source_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Conversion frame
    conversion_frame = tk.Frame(frame)
    conversion_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    km_label = tk.Label(conversion_frame, text="KM")
    km_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    km_entry = tk.Entry(conversion_frame, width=10)
    km_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    nm_label = tk.Label(conversion_frame, text="NM")
    nm_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    nm_entry = tk.Entry(conversion_frame, width=10)
    nm_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    mt_label = tk.Label(conversion_frame, text="MT")
    mt_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    mt_entry = tk.Entry(conversion_frame, width=10)
    mt_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ft_label = tk.Label(conversion_frame, text="FT")
    ft_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
    ft_entry = tk.Entry(conversion_frame, width=10)
    ft_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    def convert_km_to_nm(event):
        try:
            km_value = float(km_entry.get())
            nm_value = km_value * 0.539957
            nm_entry.delete(0, tk.END)
            nm_entry.insert(0, f"{nm_value:.2f}")
        except ValueError:
            pass

    def convert_nm_to_km(event):
        try:
            nm_value = float(nm_entry.get())
            km_value = nm_value / 0.539957
            km_entry.delete(0, tk.END)
            km_entry.insert(0, f"{km_value:.2f}")
        except ValueError:
            pass

    def convert_mt_to_ft(event):
        try:
            mt_value = float(mt_entry.get())
            ft_value = mt_value * 3.28084
            ft_entry.delete(0, tk.END)
            ft_entry.insert(0, f"{ft_value:.2f}")
        except ValueError:
            pass

    def convert_ft_to_mt(event):
        try:
            ft_value = float(ft_entry.get())
            mt_value = ft_value / 3.28084
            mt_entry.delete(0, tk.END)
            mt_entry.insert(0, f"{mt_value:.2f}")
        except ValueError:
            pass

    km_entry.bind("<FocusOut>", convert_km_to_nm)
    nm_entry.bind("<FocusOut>", convert_nm_to_km)
    mt_entry.bind("<FocusOut>", convert_mt_to_ft)
    ft_entry.bind("<FocusOut>", convert_ft_to_mt)

    # Original frame with "Show on map" button, original text
    original_frame = tk.Frame(frame)
    original_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)

    show_map_button = tk.Button(original_frame, text="Show on map", command=lambda: show_on_map(
        [coord for coord in original_text.get("1.0", "end-1c").split('\n') if coord],
        [coord for coord in sorted_text.get("1.0", "end-1c").split('\n') if coord]
    ))
    show_map_button.grid(row=0, column=0, padx=5, pady=5)

    # Original text label
    original_label = tk.Label(original_frame, text="Original COORDs")
    original_label.grid(row=1, column=0, padx=5, pady=5)

    # Original text
    original_text = tk.Text(original_frame, height=14, width=15)
    original_text.grid(row=2, column=0, padx=5, pady=5)

    # Copy button to replace Windows clipboard with original text
    copy_button = tk.Button(original_frame, text="Copy")
    copy_button.grid(row=3, column=0, padx=5, pady=5)
    copy_button.config(command=lambda: copy_to_clipboard(root, original_text.get("1.0", tk.END).strip(), copy_button))

    # Original canvas
    original_canvas = tk.Canvas(frame, bg="white", width=320, height=320)
    original_canvas.grid(row=0, column=3, padx=5, pady=5)

    # Sorted frame with sorted text
    sorted_frame = tk.Frame(frame)
    sorted_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)

    # Sorted text label
    sorted_label = tk.Label(sorted_frame, text="Sorted COORDs")
    sorted_label.grid(row=0, column=0, padx=5, pady=5)

    sorted_text = tk.Text(sorted_frame, height=14, width=15)
    sorted_text.grid(row=1, column=0, padx=5, pady=5)

    # Copy button to replace Windows clipboard with sorted text
    sorted_copy_button = tk.Button(sorted_frame, text="Copy")
    sorted_copy_button.grid(row=2, column=0, padx=5, pady=5)
    sorted_copy_button.config(command=lambda: copy_to_clipboard(root, sorted_text.get("1.0", tk.END).strip(), sorted_copy_button))

    # Sorted canvas
    sorted_canvas = tk.Canvas(frame, bg="white", width=320, height=320)
    sorted_canvas.grid(row=1, column=3, padx=5, pady=5)

    # Configure grid weights for responsiveness
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("INO Tool")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    show_ino_tool(root, main_frame)

    root.mainloop()