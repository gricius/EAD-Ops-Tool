# utils/drawing_utils.py
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.crs import Globe
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from shapely.geometry import Point, box
from cartopy.crs import Mercator, PlateCarree
from matplotlib.patches import Circle
import numpy as np
import sys
import os
from utils.coordinate_utils import parse_coordinate
from geopy.distance import great_circle  
from cartopy.geodesic import Geodesic
import warnings
import pyogrio
from osgeo import gdal
import mplcursors


def set_gdal_data_path():
    """Set the GDAL data path based on whether the script is running from PyInstaller or development."""
    if getattr(sys, 'frozen', False):  # If bundled with PyInstaller
        base_path = sys._MEIPASS  # PyInstaller's temporary directory
        gdal_data_path = os.path.join(base_path, 'gdal')
    else:
        gdal_data_path = r"C:\Users\grici\miniconda3\Library\share\gdal"  # Normal path during development
    
    os.environ['GDAL_DATA'] = gdal_data_path

set_gdal_data_path()  

def check_gdal_data():
    gdal_data = gdal.GetConfigOption('GDAL_DATA')
    # print(f"GDAL_DATA from GDAL: {gdal_data}")

# Check if GDAL can detect the data files
check_gdal_data()


# Ensure we're using a font that can handle most glyphs
matplotlib.rcParams['font.family'] = 'Arial'

active_cursors = []

def get_resource_path(relative_path):
    """ Get the absolute path to resource, works for PyInstaller and development. """
    try:
        # If running as a PyInstaller bundle, use the temporary _MEIPASS directory.
        base_path = sys._MEIPASS
    except AttributeError:
        # If running in development, use the normal relative path.
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create a spherical globe (no flattening)
spherical_globe = Globe(ellipse='sphere')

# Create a Geodetic CRS using the spherical globe
geodetic_spherical = ccrs.Geodetic(globe=spherical_globe)

# Use Plate Carree projection with the spherical globe
plate_carree_spherical = ccrs.PlateCarree(globe=spherical_globe)

# airplane_img = plt.imread(get_resource_path('assets/images/transparent_purple_plane_v1.png'))


# def plot_airplane_icon(ax, lon, lat, image, zoom=0.05):
#     imagebox = OffsetImage(image, zoom=zoom)
#     ab = AnnotationBbox(imagebox, (lon, lat), frameon=False, transform=ccrs.PlateCarree())
#     ax.add_artist(ab)

def load_shapefile(relative_path, target_crs="EPSG:4326"):
    """
    Load and reproject shapefile to WGS84 (EPSG:4326) by default.
    Handles both PyInstaller's bundled files and development paths.
    """
    if getattr(sys, 'frozen', False):  # If bundled with PyInstaller
        base_path = sys._MEIPASS
        # print(f"Base path in PyInstaller executable: {base_path}")
        # print(f"GDAL files: {os.listdir(os.path.join(base_path, 'gdal'))}")
        path = os.path.join(base_path, relative_path)
    else:
        path = os.path.abspath(relative_path)  # Normal path during development

    gdf = gpd.read_file(path, engine="pyogrio")
    
    if gdf.crs is None:
        gdf = gdf.set_crs(target_crs)
    elif gdf.crs != target_crs:
        gdf = gdf.to_crs(target_crs)
    return gdf



def decimal_degrees_to_dms(deg, is_lat=True):
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    direction = 'N' if is_lat and deg >= 0 else 'S' if is_lat else 'E' if deg >= 0 else 'W'
    return f"{abs(d):02d}°{abs(m):02d}'{abs(s):04.1f}\" {direction}"

def format_coord(x, y):
    if x is None or y is None:
        return ""
    lat_dms = decimal_degrees_to_dms(y, is_lat=True)
    lon_dms = decimal_degrees_to_dms(x, is_lat=False)
    return f"Lat: {lat_dms}, Lon: {lon_dms}"

def plot_great_circle_circle(ax, lon, lat, radius_nm, color, label):
    # Number of points to generate along the circle
    n_points = 360
    radius_deg = np.degrees(radius_nm * 1852 / 6371000)  # Convert radius from NM to degrees (approximate)
    angles = np.linspace(0, 360, n_points)
    lons = []
    lats = []

    for angle in angles:
        bearing = np.radians(angle)
        lat2 = np.arcsin(
            np.sin(np.radians(lat)) * np.cos(radius_nm / 3440.065) +
            np.cos(np.radians(lat)) * np.sin(radius_nm / 3440.065) * np.cos(bearing)
        )
        lon2 = np.radians(lon) + np.arctan2(
            np.sin(bearing) * np.sin(radius_nm / 3440.065) * np.cos(np.radians(lat)),
            np.cos(radius_nm / 3440.065) - np.sin(np.radians(lat)) * np.sin(lat2)
        )
        lats.append(np.degrees(lat2))
        lons.append(np.degrees(lon2))

    ax.plot(lons, lats, color=color, linestyle='--', transform=geodetic_spherical, label=label)

def plot_base_map(ax, countries_gdf, disputed_areas_gdf, elevation_points_gdf, raster_path=None):
    # Plot countries
    countries_gdf.plot(ax=ax, edgecolor='black', facecolor='tan', transform=geodetic_spherical)
    
    # Plot country names
    for _, country in countries_gdf.iterrows():
        centroid = country.geometry.centroid
        ax.text(centroid.x, centroid.y, country['NAME'], fontsize=10, color='black', transform=geodetic_spherical)
    
    # Plot disputed areas
    disputed_areas_gdf.plot(ax=ax, edgecolor='red', facecolor='none', linestyle='--', transform=geodetic_spherical, label="Disputed Areas")
    
    # Plot names of disputed areas
    for _, disputed_area in disputed_areas_gdf.iterrows():
        centroid = disputed_area.geometry.centroid
        ax.text(centroid.x, centroid.y, disputed_area['BRK_NAME'], fontsize=8, color='red', transform=geodetic_spherical)
    
    # Plot elevation points
    for _, elevation_point in elevation_points_gdf.iterrows():
        point_lon, point_lat = elevation_point.geometry.x, elevation_point.geometry.y
        name = elevation_point['name']
        elevation = elevation_point['elevation']
        elevation_text = f"{name} ({elevation} m)"
        ax.text(point_lon, point_lat, elevation_text, fontsize=8, color='green', transform=geodetic_spherical)

def plot_airports(ax, bounding_box, airports_gdf, center_lat, center_lon, max_distance_nm):
    # Reproject airports to WGS84 (EPSG:4326) if needed
    airports_gdf = airports_gdf.to_crs("EPSG:4326")

    # Filter airports by bounding box
    airports_within_bbox = airports_gdf.loc[airports_gdf.sindex.intersection(bounding_box.bounds)]
    
    # Prepare lists to store the plotted markers and their corresponding labels
    markers = []
    labels = []

    for _, record in airports_within_bbox.iterrows():
        airport_geometry = record.geometry
        if isinstance(airport_geometry, Point):
            airport_lon, airport_lat = airport_geometry.x, airport_geometry.y
            
            # Calculate the distance in NM between the center and each airport
            distance_nm = great_circle((center_lat, center_lon), (airport_lat, airport_lon)).nautical
            
            # Plot only the airports within the max_distance_nm
            if distance_nm <= max_distance_nm:
                # Plot the airport marker
                marker, = ax.plot(
                    airport_lon,
                    airport_lat,
                    marker='*',
                    markersize=6,
                    linestyle='-',
                    color='black',
                    transform=geodetic_spherical  # Use the spherical transform
                )
                markers.append(marker)
                
                # Store the airport label for the tooltip
                airport_ident_name = (
                    f"{record['ident']} - {record['name']}\n"
                    f"({decimal_degrees_to_dms(airport_lat, True)}, "
                    f"{decimal_degrees_to_dms(airport_lon, False)})\n"
                    f"Type: {record['type']}\n"
                )
                labels.append(airport_ident_name)

    # Use mplcursors to add hover annotations
    cursor = mplcursors.cursor(markers, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(labels[markers.index(sel.artist)])
    
    # Keep the cursor alive by attaching it to the axis object
    ax.airports_cursor = cursor



def plot_coordinates(original_coords, sorted_coords):
    parsed_original_coords = [parse_coordinate(coord) for coord in original_coords]
    parsed_sorted_coords = [parse_coordinate(coord) for coord in sorted_coords]
    original_lats, original_lons = zip(*parsed_original_coords)
    sorted_lats, sorted_lons = zip(*parsed_sorted_coords)

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': plate_carree_spherical})
    # Remove padding around the plot
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    margin = 1.7
    min_lon, max_lon = min(original_lons) - margin, max(original_lons) + margin
    min_lat, max_lat = min(original_lats) - margin, max(original_lats) + margin
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=plate_carree_spherical)

    # Plot base map layers
    plot_base_map(ax, 
              load_shapefile('shapes/ne_50m_admin_0_countries.shp'), 
              load_shapefile('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp'),
            #   load_shapefile('shapes/ne_50m_admin_0_boundary_lines_disputed_areas.shp'),
              load_shapefile('shapes/ne_50m_geography_regions_elevation_points.shp')
                )


    # Plot original coordinates
    ax.plot(original_lons, original_lats, marker='o', markersize=5, linestyle='-', color='blue', transform=geodetic_spherical, label='Original Coordinates')
    for i, txt in enumerate(range(1, len(original_lons) + 1)):
        ax.text(original_lons[i], original_lats[i], txt, fontsize=12, color='blue', transform=geodetic_spherical)

    # Plot sorted coordinates
    ax.plot(sorted_lons, sorted_lats, marker='o', markersize=5, linestyle='-', color='red',
        transform=geodetic_spherical, label='Sorted Coordinates')
    for i, txt in enumerate(range(1, len(sorted_lons) + 1)):
        ax.text(sorted_lons[i], sorted_lats[i], txt, fontsize=12, color='red', transform=geodetic_spherical)

    # Calculate geodesic center and max radius
    center_lat, center_lon = np.mean(sorted_lats), np.mean(sorted_lons)
    max_distance_nm = max(great_circle((center_lat, center_lon), (lat, lon)).nautical for lat, lon in zip(sorted_lats, sorted_lons))
    plot_great_circle_circle(ax, center_lon, center_lat, max_distance_nm, 'green', f'{max_distance_nm:.2f} NM Enclosing Circle')


    # Plot airports within bounding box
    delta_deg = max_distance_nm * 1.852 / 110.574 + 5  # Approx conversion of NM to degrees
    bounding_box = box(center_lon - delta_deg, center_lat - delta_deg, center_lon + delta_deg, center_lat + delta_deg)
    airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:3857")  # Ensure the airports are loaded correctly
    plot_airports(ax, bounding_box, airports_gdf, center_lat, center_lon, max_distance_nm + 25)

    # Display center coordinates and radius
    ax.text(center_lon, center_lat, f"Center: {decimal_degrees_to_dms(center_lat)}, {decimal_degrees_to_dms(center_lon)}\nRadius: {max_distance_nm:.2f} NM",
            fontsize=10, color='green', transform=plate_carree_spherical, ha='left')
    
    # Add mouse scroll event handler for zooming
    def on_scroll(event):
        base_scale = 2.0  # Zoom factor
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        x0, x1, y0, y1 = ax.get_extent(crs=plate_carree_spherical)
        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2
        x_width = (x1 - x0) * scale_factor / 2
        y_height = (y1 - y0) * scale_factor / 2
        new_extent = [x_center - x_width, x_center + x_width,
                      y_center - y_height, y_center + y_height]
        ax.set_extent(new_extent, crs=plate_carree_spherical)
        plt.draw()

    # Connect the scroll event to the handler
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    # Add legend
    plt.legend()
    ax.format_coord = lambda x, y: format_coord(x, y)
    plt.show()

def show_single_coord_on_map(coord):
    lat, lon = parse_coordinate(coord)
    if lat is None or lon is None:
        messagebox.showwarning('Warning', 'Invalid coordinate for plotting.')
        return

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': plate_carree_spherical})
    # Remove padding around the plot
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    extent_margin = .1
    ax.set_extent([lon - extent_margin, lon + extent_margin, lat - extent_margin, lat + extent_margin], crs=plate_carree_spherical)

    plot_base_map(ax, 
                  load_shapefile('shapes/ne_50m_admin_0_countries.shp'), 
                  load_shapefile('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp'),
                #   load_shapefile('shapes/ne_50m_admin_0_boundary_lines_disputed_areas.shp'),
                  load_shapefile('shapes/ne_50m_geography_regions_elevation_points.shp'),)

    ax.plot(lon, lat, marker='o', color='blue', markersize=8, transform=plate_carree_spherical, label=f'{coord}')
    ax.text(lon, lat, f'{coord}', fontsize=10, color='blue', transform=plate_carree_spherical, ha='left')
    plot_great_circle_circle(ax, lon, lat, 1, 'blue', '1NM Radius')
    plot_great_circle_circle(ax, lon, lat, 5, 'red', '5NM Radius')

    delta_deg = 5 * 1.852 / 110.574
    bounding_box = box(lon - delta_deg, lat - delta_deg, lon + delta_deg, lat + delta_deg)
    airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:3857")
    plot_airports(ax, bounding_box, airports_gdf, lat, lon, 5)

    # Add mouse scroll event handler for zooming
    def on_scroll(event):
        base_scale = 2.0  # Zoom factor
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        x0, x1, y0, y1 = ax.get_extent(crs=plate_carree_spherical)
        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2
        x_width = (x1 - x0) * scale_factor / 2
        y_height = (y1 - y0) * scale_factor / 2
        new_extent = [x_center - x_width, x_center + x_width,
                      y_center - y_height, y_center + y_height]
        ax.set_extent(new_extent, crs=plate_carree_spherical)
        plt.draw()

    # Connect the scroll event to the handler
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    plt.title('Single Coordinate with 1 NM and 5 NM Radius Circles')
    ax.format_coord = lambda x, y: format_coord(x, y)
    plt.legend()
    plt.show()

def show_on_map(original_coords, sorted_coords):
    if len(original_coords) == 1:
        show_single_coord_on_map(original_coords[0])
    else:
        plot_coordinates(original_coords, sorted_coords)

def draw_coordinates(coords, canvas, current_theme):
    canvas.delete("all")
    
    if not coords:
        return

    # Parse the coordinates and filter out invalid ones
    parsed_coords = [parse_coordinate(coord) for coord in coords]
    parsed_coords = [coord for coord in parsed_coords if coord != (None, None)]
    
    # Check if we have valid coordinates to plot
    if not parsed_coords:
        return
    
    # Unpack latitudes and longitudes
    lats, lons = zip(*parsed_coords)
    max_lat = max(lats)
    min_lat = min(lats)
    max_lon = max(lons)
    min_lon = min(lons)

    def transform(lat, lon):
        lon_diff = max_lon - min_lon if max_lon != min_lon else 1e-5
        lat_diff = max_lat - min_lat if max_lat != min_lat else 1e-5

        # Ensure the points stay within canvas bounds
        x = (lon - min_lon) / lon_diff * (canvas.winfo_width() - 20) + 10
        y = (max_lat - lat) / lat_diff * (canvas.winfo_height() - 20) + 10

        return x, y

    # Define the font for the text
    bold_font = tkFont.Font(family="Helvetica", size=10, weight="bold")

    # Get colors from current_theme
    point_fill_color = current_theme.get('point_fill_color', current_theme['canvas_fg'])
    line_color = current_theme.get('line_color', current_theme['canvas_fg'])
    text_color = current_theme.get('text_color', current_theme['canvas_fg'])

    # Plot points and lines on the canvas
    for i, (lat, lon) in enumerate(zip(lats, lons)):
        x, y = transform(lat, lon)
        canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=point_fill_color)
        canvas.create_text(x, y, text=str(i + 1), anchor=tk.NW, fill=text_color, font=bold_font)

    for i in range(len(lats) - 1):
        x1, y1 = transform(lats[i], lons[i])
        x2, y2 = transform(lats[i + 1], lons[i + 1])
        canvas.create_line(x1, y1, x2, y2, fill=line_color)

    # Close the polygon by connecting the last point to the first
    x1, y1 = transform(lats[-1], lons[-1])
    x2, y2 = transform(lats[0], lons[0])
    canvas.create_line(x1, y1, x2, y2, fill=line_color)
