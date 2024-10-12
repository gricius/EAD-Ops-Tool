# utils/drawing_utils.py
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
# from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.crs import Geodetic
from cartopy.crs import Globe
# from cartopy.io.shapereader import Reader
# from cartopy.feature import ShapelyFeature
from shapely.geometry import Point, box
# from cartopy.crs import Mercator, PlateCarree
# from matplotlib.patches import Circle
import numpy as np
import sys
import os
from utils.coordinate_utils import parse_coordinate
from geopy.distance import great_circle  
from geopy.distance import geodesic
# from cartopy.geodesic import Geodesic
import warnings
# import pyogrio
from osgeo import gdal
import mplcursors
import random
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely.geometry import MultiPoint
from scipy.spatial import ConvexHull

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


# Ensure we're using a font that can handle glyph 133 \x85 (ellipsis)
matplotlib.rcParams['font.family'] = 'sans-serif'

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

def minimal_enclosing_circle(points):
    """
    Computes the minimal enclosing circle using Welzl's algorithm with Euclidean distances.
    :param points: List of tuples [(lat1, lon1), (lat2, lon2), ...]
    :return: (center_lat, center_lon, radius_nm)
    """
    import math
    import random
    from geopy.distance import geodesic

    def distance_euclidean(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def circle_two_points(p1, p2):
        center = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
        radius = distance_euclidean(p1, center)
        return (center[0], center[1], radius)

    def circle_three_points(p1, p2, p3):
        A = p2[0] - p1[0]
        B = p2[1] - p1[1]
        C = p3[0] - p1[0]
        D = p3[1] - p1[1]
        E = A*(p1[0] + p2[0]) + B*(p1[1] + p2[1])
        F = C*(p1[0] + p3[0]) + D*(p1[1] + p3[1])
        G = 2*(A*(p3[1] - p2[1]) - B*(p3[0] - p2[0]))
        if G == 0:
            return None  # Points are collinear
        center_x = (D*E - B*F) / G
        center_y = (A*F - C*E) / G
        radius = distance_euclidean(p1, (center_x, center_y))
        return (center_x, center_y, radius)

    def is_inside(p, c):
        return distance_euclidean(p, (c[0], c[1])) <= c[2] + 1e-8

    def welzl(P, R, n):
        if n == 0 or len(R) == 3:
            if len(R) == 0:
                return (0, 0, 0)
            elif len(R) == 1:
                return (R[0][0], R[0][1], 0)
            elif len(R) == 2:
                return circle_two_points(R[0], R[1])
            elif len(R) == 3:
                c = circle_three_points(R[0], R[1], R[2])
                if c is not None:
                    return c
                else:
                    # Collinear points, return the max two-point circle
                    return max([
                        circle_two_points(R[0], R[1]),
                        circle_two_points(R[0], R[2]),
                        circle_two_points(R[1], R[2])
                    ], key=lambda c: c[2])
        
        p = P[n - 1]
        c = welzl(P, R, n - 1)
        if is_inside(p, c):
            return c
        else:
            return welzl(P, R + [p], n - 1)

    # Remove duplicate points
    P = list(set(points))

    if not P:
        return (0, 0, 0)

    # Shuffle the points to ensure average-case performance
    random.shuffle(P)

    # Compute the minimal enclosing circle
    c = welzl(P, [], len(P))

    # Extract center and initial radius
    center_lat, center_lon, _ = c

    # Calculate the geodesic radius in nautical miles
    max_dist = 0
    for p in P:
        try:
            dist = geodesic((center_lat, center_lon), p).nautical
            if dist > max_dist:
                max_dist = dist
        except Exception as e:
            print(f"Error calculating geodesic distance for point {p}: {e}")
            continue

    # Debugging Statements
    print(f"Computed Circle Center: Latitude={center_lat}, Longitude={center_lon}, Radius={max_dist} NM")

    return (center_lat, center_lon, max_dist)

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
    n_points = 360
    angles = np.linspace(0, 360, n_points)
    lons = []
    lats = []

    for angle in angles:
        bearing = np.radians(angle)
        # Convert radius_nm to meters for accurate distance calculation
        dist_m = radius_nm * 1852  # 1 NM = 1852 meters

        # Use geodesic from geopy for accurate lat/lon points along the circle
        destination = geodesic(kilometers=dist_m / 1000).destination((lat, lon), np.degrees(bearing))
        lats.append(destination.latitude)
        lons.append(destination.longitude)

    ax.plot(lons, lats, color=color, linestyle='--', transform=Geodetic(), label=label)

def plot_base_map(ax, countries_gdf, disputed_areas_gdf, elevation_points_gdf):
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
    
    markers = []
    labels = []

    for _, record in airports_within_bbox.iterrows():
        airport_geometry = record.geometry
        if isinstance(airport_geometry, Point):
            airport_lon, airport_lat = airport_geometry.x, airport_geometry.y
            
            # Calculate the distance in NM between the center and each airport
            distance_nm = geodesic((center_lat, center_lon), (airport_lat, airport_lon)).nautical
            
            # Plot only the airports within the max_distance_nm
            if distance_nm <= max_distance_nm:
                marker, = ax.plot(
                    airport_lon,
                    airport_lat,
                    marker='*',
                    markersize=6,
                    linestyle='-',
                    color='black',
                    transform=Geodetic()  # Use the Geodetic transform for spherical plotting
                )
                markers.append(marker)
                
                # Store the airport label for the tooltip
                airport_ident_name = (
                    f"{record['ident']} - {record['name']}\n"
                    f"{decimal_degrees_to_dms(airport_lat, True)}, "
                    f"{decimal_degrees_to_dms(airport_lon, False)}\n"
                    f"Type: {record['type']}\n"
                )
                labels.append(airport_ident_name)

    cursor = mplcursors.cursor(markers, hover=False)
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(labels[markers.index(sel.artist)])

    ax.airports_cursor = cursor  # Attach cursor to the axis object

def on_scroll(event):
    """
    Handles zooming in and out of the plot on scroll.
    """
    base_scale = 2.0  # Zoom factor
    if event.button == 'up':
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        return

    # Get the current extent
    x0, x1, y0, y1 = event.inaxes.get_extent(crs=plate_carree_spherical)
    x_center = (x0 + x1) / 2
    y_center = (y0 + y1) / 2
    x_width = (x1 - x0) * scale_factor / 2
    y_height = (y1 - y0) * scale_factor / 2
    new_extent = [x_center - x_width, x_center + x_width,
                  y_center - y_height, y_center + y_height]
    
    # Set the new extent and redraw the plot
    event.inaxes.set_extent(new_extent, crs=plate_carree_spherical)
    plt.draw()

def plot_coordinates(original_coords, sorted_coords):
    parsed_original_coords = [parse_coordinate(coord) for coord in original_coords]
    parsed_original_coords = [coord for coord in parsed_original_coords if coord != (None, None)]
    parsed_sorted_coords = [parse_coordinate(coord) for coord in sorted_coords]
    parsed_sorted_coords = [coord for coord in parsed_sorted_coords if coord != (None, None)]
    
    original_lats, original_lons = zip(*parsed_original_coords)
    sorted_lats, sorted_lons = zip(*parsed_sorted_coords)

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': plate_carree_spherical})
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    margin = 1.7
    min_lon, max_lon = min(original_lons) - margin, max(original_lons) + margin
    min_lat, max_lat = min(original_lats) - margin, max(original_lats) + margin
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=plate_carree_spherical)

    # Load and plot base map layers
    plot_base_map(ax, 
                  load_shapefile('shapes/ne_50m_admin_0_countries.shp'), 
                  load_shapefile('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp'),
                  load_shapefile('shapes/ne_50m_geography_regions_elevation_points.shp'))

    # Plot original and sorted coordinates with updated functions
    ax.plot(original_lons, original_lats, marker='o', markersize=5, linestyle='-', color='blue', transform=Geodetic(), label='Original Coordinates')
    ax.plot(sorted_lons, sorted_lats, marker='o', markersize=5, linestyle='-', color='red', transform=Geodetic(), label='Sorted Coordinates')

    # Minimal enclosing circle update
    sorted_points = list(zip(sorted_lats, sorted_lons))
    center_lat, center_lon, radius_nm = minimal_enclosing_circle(sorted_points)
    plot_great_circle_circle(ax, center_lon, center_lat, radius_nm, 'green', f'{radius_nm:.2f} NM Enclosing Circle')

    # Plot airports with updated bounding box calculations
    delta_deg = radius_nm * 1.852 / 110.574 + 5
    bounding_box = box(center_lon - delta_deg, center_lat - delta_deg, center_lon + delta_deg, center_lat + delta_deg)
    airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:3857")
    plot_airports(ax, bounding_box, airports_gdf, center_lat, center_lon, radius_nm + 25)

    # Finalize plot with legend and interactive features
    legend_elements = [
        Patch(facecolor='none', edgecolor='red', linestyle='--', label='Disputed Areas'),
        Line2D([0], [0], marker='o', color='blue', label='Original Coordinates', markerfacecolor='blue', markersize=5),
        Line2D([0], [0], marker='o', color='red', label='Sorted Coordinates', markerfacecolor='red', markersize=5),
        Line2D([0], [0], color='green', linestyle='--', label=f'{radius_nm:.2f} NM Enclosing Circle'),
        Line2D([0], [0], marker='*', color='black', label='Airports', markerfacecolor='black', markersize=6)
    ]
    
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
    
    ax.format_coord = lambda x, y: format_coord(x, y)
    plt.show()

    # Define custom legend handles
    legend_elements = [
        Patch(facecolor='none', edgecolor='red', linestyle='--', label='Disputed Areas'),
        Line2D([0], [0], marker='o', color='blue', label='Original Coordinates',
            markerfacecolor='blue', markersize=5, linestyle='-'),
        Line2D([0], [0], marker='o', color='red', label='Sorted Coordinates',
            markerfacecolor='red', markersize=5, linestyle='-'),
        Line2D([0], [0], color='green', linestyle='--', label=f'{radius_nm:.2f} NM Enclosing Circle'),
        Line2D([0], [0], marker='*', color='black', label='Airports',
            markerfacecolor='black', markersize=6, linestyle='None')
    ]
    
    # Connect the scroll event to the handler
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    # Add custom legend
    ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
    
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

    extent_margin = 0.5  # Increased margin for better visibility
    ax.set_extent([lon - extent_margin, lon + extent_margin, lat - extent_margin, lat + extent_margin], crs=ccrs.PlateCarree())

    # Load shapefiles with target CRS as EPSG:4326 to match Plate Carree
    plot_base_map(ax, 
                  load_shapefile('shapes/ne_50m_admin_0_countries.shp', target_crs="EPSG:4326"), 
                  load_shapefile('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp', target_crs="EPSG:4326"),
                  load_shapefile('shapes/ne_50m_geography_regions_elevation_points.shp', target_crs="EPSG:4326"))

    # Plot the coordinate point
    ax.plot(lon, lat, marker='o', color='blue', markersize=8, transform=ccrs.PlateCarree(), label=f'{coord}')
    ax.text(lon, lat, f'{coord}', fontsize=10, color='blue', transform=ccrs.PlateCarree(), ha='left')

    # Plot 1 NM and 5 NM radius circles
    plot_great_circle_circle(ax, lon, lat, 1, 'blue', '1NM Radius')
    plot_great_circle_circle(ax, lon, lat, 5, 'red', '5NM Radius')

    # Define bounding box for airports (using 5 NM radius plus buffer)
    # delta_deg = 5 / 60.0  # Approximate conversion of NM to degrees
    # bounding_box = box(lon - delta_deg, lat - delta_deg, lon + delta_deg, lat + delta_deg)
    # print(f"Bounding Box: {decimal_degrees_to_dms(bounding_box.bounds[1], is_lat=True)}, {decimal_degrees_to_dms(bounding_box.bounds[0], is_lat=False)}, {decimal_degrees_to_dms(bounding_box.bounds[3], is_lat=True)}, {decimal_degrees_to_dms(bounding_box.bounds[2], is_lat=False)}")
    
    # Load airports shapefile with target CRS as EPSG:4326
    # airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:4326")
    # plot_airports(ax, bounding_box, airports_gdf, lat, lon, 100)
    delta_deg = 5 * 1.852 / 110.574 + 5
    bounding_box = box(lon - delta_deg, lat - delta_deg, lon + delta_deg, lat + delta_deg)
    airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:3857")
    plot_airports(ax, bounding_box, airports_gdf, lat, lon,10 + 20)

    # Add mouse scroll event handler for zooming
    def on_scroll(event):
        base_scale = 2.0  # Zoom factor
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        x0, x1, y0, y1 = ax.get_extent(crs=ccrs.PlateCarree())
        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2
        x_width = (x1 - x0) * scale_factor / 2
        y_height = (y1 - y0) * scale_factor / 2
        new_extent = [x_center - x_width, x_center + x_width,
                      y_center - y_height, y_center + y_height]
        ax.set_extent(new_extent, crs=ccrs.PlateCarree())
        plt.draw()

       
    legend_elements = [
        Patch(facecolor='none', edgecolor='red', linestyle='--', label='Disputed Areas'),
        Line2D([0], [0], marker='*', color='black', label='Airports',
            markerfacecolor='black', markersize=6, linestyle='None'),
        Line2D([0], [0], marker='o', color='blue', label='Coordinate',
            markerfacecolor='blue', markersize=8, linestyle='None'),
        Line2D([0], [0], color='blue', linestyle='--', label='1NM Radius'),
        Line2D([0], [0], color='red', linestyle='--', label='5NM Radius')
    ]
    
    # Connect the scroll event to the handler
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    # Add custom legend
    ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
    
    ax.format_coord = lambda x, y: format_coord(x, y)
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
    bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

    # Get colors from current_theme
    point_fill_color = current_theme.get('point_fill_color', current_theme['point_fill_color']) 
    line_color = current_theme.get('line_color', current_theme['line_color'])
    text_color = current_theme.get('text_color', current_theme['canvas_fg'])
    line_width = current_theme.get('line_width', current_theme['line_width'])
    text_bg_color = current_theme.get('text_bg_color', current_theme['text_bg_color'])  
    text_bg_outline_color = current_theme.get('text_bg_outline_color', current_theme['text_bg_outline_color'])

    # Define radius for the point and text background circle
    point_radius = 5  # Radius for the point
    text_radius = 10  # Radius for the text background circle

    # Plot lines connecting points
    for i in range(len(lats) - 1):
        x1, y1 = transform(lats[i], lons[i])
        x2, y2 = transform(lats[i + 1], lons[i + 1])
        canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)

    # Plot each point and its corresponding text with a background circle
    for i, (lat, lon) in enumerate(zip(lats, lons)):
        x, y = transform(lat, lon)
        
        # Draw a filled circle behind the text
        canvas.create_oval(
            x - text_radius, y - text_radius,
            x + text_radius, y + text_radius,
            fill=text_bg_color,
            outline=text_bg_outline_color,
            width=2
        )
        
        # Draw the text centered on the circle
        canvas.create_text(
            x, y,
            text=str(i + 1),
            anchor=tk.CENTER,  # Center the text on (x, y)
            fill=text_color,
            font=bold_font
        )

    # Close the polygon by connecting the last point to the first
    x1, y1 = transform(lats[-1], lons[-1])
    x2, y2 = transform(lats[0], lons[0])
    canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)
