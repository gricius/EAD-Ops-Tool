import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from utils.coordinate_utils import parse_coordinate

def draw_coordinates(coords, canvas):
    """
    Draws the coordinates on the given canvas.
    """
    canvas.delete("all")
    if not coords:
        return
    
    try:
        parsed_coords = [parse_coordinate(coord) for coord in coords]
        parsed_coords = [coord for coord in parsed_coords if coord != (None, None)]
        lats, lons = zip(*parsed_coords)
        max_lat = max(lats)
        min_lat = min(lats)
        max_lon = max(lons)
        min_lon = min(lons)

        def transform(lat, lon):
            x = (lon - min_lon) / (max_lon - min_lon) * canvas.winfo_width()
            y = (max_lat - lat) / (max_lat - min_lat) * canvas.winfo_height()
            return x, y

        for i, (lat, lon) in enumerate(zip(lats, lons)):
            x, y = transform(lat, lon)
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")
            canvas.create_text(x, y, text=str(i + 1), anchor=tk.NW)

        for i in range(len(lats) - 1):
            x1, y1 = transform(lats[i], lons[i])
            x2, y2 = transform(lats[i + 1], lons[i + 1])
            canvas.create_line(x1, y1, x2, y2, fill="blue")

        # Draw the closing line of the polygon
        x1, y1 = transform(lats[-1], lons[-1])
        x2, y2 = transform(lats[0], lons[0])
        canvas.create_line(x1, y1, x2, y2, fill="blue")

    except Exception as e:
        messagebox.showwarning('Warning', f'Coordinate drawing error: {e}')

def plot_coordinates(original_coords, sorted_coords):
    """
    Plots original and sorted coordinates on a map using Basemap and matplotlib.
    """
    parsed_original_coords = [parse_coordinate(coord) for coord in original_coords]
    parsed_sorted_coords = [parse_coordinate(coord) for coord in sorted_coords]

    parsed_original_coords = [coord for coord in parsed_original_coords if coord != (None, None)]
    parsed_sorted_coords = [coord for coord in parsed_sorted_coords if coord != (None, None)]

    if not parsed_original_coords or not parsed_sorted_coords:
        messagebox.showwarning('Warning', 'No valid coordinates to plot.')
        return

    original_lats, original_lons = zip(*parsed_original_coords)
    sorted_lats, sorted_lons = zip(*parsed_sorted_coords)

    fig, ax = plt.subplots(figsize=(10, 8))

    m = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=ax)
    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='lightgreen', lake_color='aqua')

    # Plot original coordinates
    x, y = m(original_lons, original_lats)
    m.plot(x, y, marker='o', markersize=5, linestyle='-', color='blue', label='Original Coordinates')
    for i, txt in enumerate(range(1, len(original_lons) + 1)):
        plt.text(x[i], y[i], txt, fontsize=12, color='blue')

    # Plot sorted coordinates
    x, y = m(sorted_lons, sorted_lats)
    m.plot(x, y, marker='o', markersize=5, linestyle='-', color='red', label='Sorted Coordinates')
    for i, txt in enumerate(range(1, len(sorted_lons) + 1)):
        plt.text(x[i], y[i], txt, fontsize=12, color='red')

    plt.legend()
    plt.title('Original and Sorted coordinates')
    plt.show()

def show_on_map(original_coords, sorted_coords):
    """
    Show coordinates on the map using matplotlib and Basemap.
    """
    plot_coordinates(original_coords, sorted_coords)
