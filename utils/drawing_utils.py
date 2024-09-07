import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from shapely.geometry import Point
from cartopy.crs import Mercator, PlateCarree
from matplotlib.patches import Circle
from scipy.spatial import ConvexHull
import numpy as np
import sys
import os
from utils.coordinate_utils import parse_coordinate


def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def decimal_degrees_to_dms(deg, is_lat=True):
    """Convert decimal degrees to degrees, minutes, seconds format."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    direction = 'N' if is_lat and deg >= 0 else 'S' if is_lat else 'E' if deg >= 0 else 'W'
    return f"{abs(d):02d}°{abs(m):02d}'{abs(s):04.1f}\" {direction}"


def format_coord(x, y):
    """Format the coordinates for display on the toolbar with latitude first."""
    if x is None or y is None:
        return ""
    lat_dms = decimal_degrees_to_dms(y, is_lat=True)
    lon_dms = decimal_degrees_to_dms(x, is_lat=False)
    return f"Lat: {lat_dms}, Lon: {lon_dms}"


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
    Plots original and sorted coordinates on a map using Cartopy and matplotlib.
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

    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Set the map extent to zoom in on a region
    map_extent = [min(original_lons) - 3, max(original_lons) + 3, min(original_lats) - 3, max(original_lats) + 3]
    ax.set_extent(map_extent, crs=ccrs.PlateCarree())

    # Use local shapefiles for features
    countries_shp = ShapelyFeature(Reader(get_resource_path('shapes/ne_50m_admin_0_countries.shp')).geometries(),
                                   ccrs.PlateCarree(), edgecolor='black', facecolor='tan')
    disputed_shp = ShapelyFeature(Reader(get_resource_path('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp')).geometries(),
                                  ccrs.PlateCarree(), edgecolor='red', facecolor='none')
    disputed_boundaries_shp = ShapelyFeature(Reader(get_resource_path('shapes/ne_50m_admin_0_boundary_lines_disputed_areas.shp')).geometries(),
                                             ccrs.PlateCarree(), edgecolor='red', facecolor='none')
    elevations_shp = ShapelyFeature(Reader(get_resource_path('shapes/ne_50m_geography_regions_elevation_points.shp')).geometries(),
                                    ccrs.PlateCarree(), edgecolor='black', facecolor='none')
    
    ax.add_feature(countries_shp, zorder=1)
    ax.add_feature(disputed_shp, zorder=0)
    ax.add_feature(disputed_boundaries_shp, zorder=1)
    ax.add_feature(elevations_shp, zorder=1)

    # Plot original coordinates
    ax.plot(original_lons, original_lats, marker='o', markersize=5, linestyle='-', color='blue', transform=ccrs.Geodetic(), label='Original Coordinates')
    for i, txt in enumerate(range(1, len(original_lons) + 1)):
        ax.text(original_lons[i], original_lats[i], txt, fontsize=12, color='blue', transform=ccrs.Geodetic())

    # Plot sorted coordinates
    ax.plot(sorted_lons, sorted_lats, marker='o', markersize=5, linestyle='-', color='red', transform=ccrs.Geodetic(), label='Sorted Coordinates')
    for i, txt in enumerate(range(1, len(sorted_lons) + 1)):
        ax.text(sorted_lons[i], sorted_lats[i], txt, fontsize=12, color='red', transform=ccrs.Geodetic())

    # Calculate and plot the smallest enclosing circle
    sorted_points = np.array(list(zip(sorted_lons, sorted_lats)))
    hull = ConvexHull(sorted_points)
    hull_points = sorted_points[hull.vertices]
    center = np.mean(hull_points, axis=0)

    # Calculate the actual smallest radius that encloses all points in the hull
    max_distance = np.max(np.sqrt((hull_points[:, 0] - center[0])**2 + (hull_points[:, 1] - center[1])**2))

    # Add the circle and its center
    circle = Circle((center[0], center[1]), max_distance, color='red', fill=False, linestyle='--', transform=ccrs.PlateCarree())
    ax.add_patch(circle)
    ax.plot(center[0], center[1], 'ro', markersize=8, label='Center of Circle')

    # Convert center to DMS format
    center_lat_dms = decimal_degrees_to_dms(center[1], is_lat=True)
    center_lon_dms = decimal_degrees_to_dms(center[0], is_lat=False)

    # Display center coordinates in DMS and radius
    ax.text(center[0], center[1], f"Center: {center_lat_dms}, {center_lon_dms}\nRadius: {max_distance:.2f}°",
            fontsize=10, color='black', transform=ccrs.PlateCarree(), ha='left')

    plt.legend()
    plt.title('Original and Sorted Coordinates')
    ax.format_coord = lambda x, y: format_coord(x, y)
    plt.show()


def show_on_map(original_coords, sorted_coords):
    """
    Show coordinates on the map using matplotlib and Cartopy.
    """
    plot_coordinates(original_coords, sorted_coords)
