import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import natural_earth
import sys
import os
from shapely.geometry import Point
from cartopy.crs import Mercator, PlateCarree
from utils.coordinate_utils import parse_coordinate

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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


    # Plot country names
    for record in Reader(get_resource_path('shapes/ne_50m_admin_0_countries.shp')).records():
        country_name = record.attributes['NAME']
        country_geometry = record.geometry
        ax.text(country_geometry.centroid.x, country_geometry.centroid.y, country_name,
                fontsize=8, color='black', transform=ccrs.PlateCarree())

    # Plot airports within the map extent, transforming from Mercator to PlateCarree
    airports_reader = Reader(get_resource_path('shapes/world_airports.shp'))
    mercator_proj = Mercator()  # Mercator projection for the airports
    platecarree_proj = PlateCarree()  # Target projection for plotting
    
    for record in airports_reader.records():
        airport_geometry = record.geometry
        if isinstance(airport_geometry, Point):
            # Transform airport coordinates from Mercator to PlateCarree
            lon, lat = platecarree_proj.transform_point(airport_geometry.x, airport_geometry.y, mercator_proj)
            if map_extent[0] <= lon <= map_extent[1] and map_extent[2] <= lat <= map_extent[3]:
                airport_ident = record.attributes['ident']
                airport_name = record.attributes['name']
                airport_ident_name = f"{airport_ident} - {airport_name}"
                ax.text(lon - 0.05, lat, '✈', fontsize=8, color='red', transform=ccrs.PlateCarree())
                ax.text(lon, lat, airport_ident_name, fontsize=8, color='black', transform=ccrs.PlateCarree())

    # Plot elevations
    for record in Reader(get_resource_path('shapes/ne_50m_geography_regions_elevation_points.shp')).records():
        elevation_name = record.attributes['name']
        elevation_geometry = record.geometry
        ax.text(elevation_geometry.centroid.x, elevation_geometry.centroid.y, elevation_name,
                fontsize=8, color='black', transform=ccrs.PlateCarree())
        ax.text(elevation_geometry.centroid.x, elevation_geometry.centroid.y + 0.3, f"{record.attributes['elevation']} M",
                fontsize=9, color='black', transform=ccrs.PlateCarree())

    # Plot disputed territories names
    for record in Reader(get_resource_path('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp')).records():
        disputed_name = record.attributes['BRK_NAME']
        disputed_geometry = record.geometry
        ax.text(disputed_geometry.centroid.x, disputed_geometry.centroid.y, disputed_name,
                fontsize=8, color='black', transform=ccrs.PlateCarree())

    # Plot original coordinates
    ax.plot(original_lons, original_lats, marker='o', markersize=5, linestyle='-', color='blue', transform=ccrs.Geodetic(), label='Original Coordinates')
    for i, txt in enumerate(range(1, len(original_lons) + 1)):
        ax.text(original_lons[i], original_lats[i], txt, fontsize=12, color='blue', transform=ccrs.Geodetic())

    # Plot sorted coordinates
    ax.plot(sorted_lons, sorted_lats, marker='o', markersize=5, linestyle='-', color='red', transform=ccrs.Geodetic(), label='Sorted Coordinates')
    for i, txt in enumerate(range(1, len(sorted_lons) + 1)):
        ax.text(sorted_lons[i], sorted_lats[i], txt, fontsize=12, color='red', transform=ccrs.Geodetic())

    plt.legend()
    plt.title('Original and Sorted Coordinates')
    plt.show()

def show_on_map(original_coords, sorted_coords):
    """
    Show coordinates on the map using matplotlib and Cartopy.
    """
    plot_coordinates(original_coords, sorted_coords)
