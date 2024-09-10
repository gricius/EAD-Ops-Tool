# utils/drawing_utils.py
import tkinter as tk
from tkinter import messagebox
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from shapely.geometry import Point, box
from cartopy.crs import Mercator, PlateCarree
from matplotlib.patches import Circle
from scipy.spatial import ConvexHull
import numpy as np
import sys
import os
from utils.coordinate_utils import parse_coordinate
from geopy.distance import geodesic  # Geodesic distance for accurate filtering
from shapely.geometry import box
from cartopy.geodesic import Geodesic
import warnings
import rasterio
from rasterio.plot import show
from cartopy.io.img_tiles import Stamen

# Ensure we're using a font that can handle most glyphs
matplotlib.rcParams['font.family'] = 'Arial'

airplane_img = plt.imread('assets/images/transparent_purple_plane_v1.png')

def plot_airplane_icon(ax, lon, lat, image, zoom=0.05):
    imagebox = OffsetImage(image, zoom=zoom)
    ab = AnnotationBbox(imagebox, (lon, lat), frameon=False, transform=ccrs.PlateCarree())
    ax.add_artist(ab)

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_shapefile(path, target_crs="EPSG:4326"):
    """
    Load and reproject shapefile to WGS84 (EPSG:4326) by default.
    If the CRS is missing, assume it's in EPSG:4326.
    """
    gdf = gpd.read_file(get_resource_path(path))
    
    # Check if the shapefile has a CRS
    if gdf.crs is None:
        # Set a default CRS if the shapefile has no CRS (assuming EPSG:4326)
        gdf = gdf.set_crs(target_crs)
    
    # Reproject to the target CRS if necessary
    return gdf.to_crs(target_crs) if gdf.crs != target_crs else gdf


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

def plot_geodesic_circle(ax, lon, lat, radius_nm, color, label):
    geod = Geodesic()
    circle = geod.circle(lon=lon, lat=lat, radius=radius_nm * 1852, n_samples=360)  # Convert NM to meters
    ax.plot(circle[:, 0], circle[:, 1], color=color, linestyle='--', transform=ccrs.Geodetic(), label=label)
    warnings.filterwarnings("ignore", message="Legend does not support handles for PatchCollection instances.")

def plot_base_map(ax, countries_gdf, disputed_areas_gdf, disputed_boundaries_gdf, elevation_points_gdf, raster_path=None):
    """
    Plot base map including countries, disputed areas, and an optional raster background.
    
    Parameters:
    - ax: The matplotlib axis on which to plot.
    - countries_gdf: Geopandas GeoDataFrame for countries.
    - disputed_areas_gdf: Geopandas GeoDataFrame for disputed areas.
    - disputed_boundaries_gdf: Geopandas GeoDataFrame for disputed boundaries.
    - elevation_points_gdf: Geopandas GeoDataFrame for elevation points.
    - raster_path: Optional path to a GeoTIFF raster file to plot as a background.
    """
    
    # If a raster_path is provided, load and plot the raster using rasterio
    if raster_path:
        with rasterio.open(raster_path) as src:
            extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
            ax.imshow(src.read(1), extent=extent, transform=ccrs.PlateCarree(), origin='upper', alpha=0.6)
    
    # Plot vector layers
    countries_gdf.plot(ax=ax, edgecolor='black', facecolor='none', transform=ccrs.PlateCarree())
    for _, country in countries_gdf.iterrows():
        centroid = country.geometry.centroid
        ax.text(centroid.x, centroid.y, country['NAME'], fontsize=10, color='black', transform=ccrs.PlateCarree())

    disputed_areas_gdf.plot(ax=ax, edgecolor='red', facecolor='none', linestyle='--', transform=ccrs.PlateCarree(), label="Disputed Areas")
    disputed_boundaries_gdf.plot(ax=ax, edgecolor='red', linestyle='--', transform=ccrs.PlateCarree(), label="Disputed Boundaries")

    # Plot elevation points
    for _, elevation_point in elevation_points_gdf.iterrows():
        point_lon, point_lat = elevation_point.geometry.x, elevation_point.geometry.y
        name = elevation_point['name']
        elevation = elevation_point['elevation']
        elevation_text = f"{name} ({elevation} m)"
        ax.text(point_lon, point_lat, elevation_text, fontsize=8, color='green', transform=ccrs.PlateCarree())

    warnings.filterwarnings("ignore", message="Glyph .* missing from font")

def plot_airports(ax, bounding_box, airports_gdf, center_lat, center_lon, max_distance_nm):
    # Reproject airports to WGS84 (EPSG:4326) if needed
    airports_gdf = airports_gdf.to_crs("EPSG:4326")

    # Filter airports by bounding box and plot
    airports_within_bbox = airports_gdf.loc[airports_gdf.sindex.intersection(bounding_box.bounds)]
    for _, record in airports_within_bbox.iterrows():
        airport_geometry = record.geometry
        if isinstance(airport_geometry, Point):
            airport_lon, airport_lat = airport_geometry.x, airport_geometry.y
            distance_nm = geodesic((center_lat, center_lon), (airport_lat, airport_lon)).nautical
            if distance_nm <= max_distance_nm:
                plot_airplane_icon(ax, airport_lon, airport_lat, airplane_img)
                airport_ident_name = f"{record['ident']} - {record['name']} ({decimal_degrees_to_dms(airport_lat, True)}, {decimal_degrees_to_dms(airport_lon, False)})"
                ax.text(airport_lon + 0.05, airport_lat, airport_ident_name, fontsize=8, color='black', transform=ccrs.PlateCarree())

def plot_coordinates(original_coords, sorted_coords):
    parsed_original_coords = [parse_coordinate(coord) for coord in original_coords]
    parsed_sorted_coords = [parse_coordinate(coord) for coord in sorted_coords]
    original_lats, original_lons = zip(*parsed_original_coords)
    sorted_lats, sorted_lons = zip(*parsed_sorted_coords)

    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    # Remove padding around the plot
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    margin = 2.0
    min_lon, max_lon = min(original_lons) - margin, max(original_lons) + margin
    min_lat, max_lat = min(original_lats) - margin, max(original_lats) + margin
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    # Plot base map layers
    plot_base_map(ax, 
              load_shapefile('shapes/ne_50m_admin_0_countries.shp'), 
              load_shapefile('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp'),
              load_shapefile('shapes/ne_50m_admin_0_boundary_lines_disputed_areas.shp'),
              load_shapefile('shapes/ne_50m_geography_regions_elevation_points.shp'),
              raster_path='shapes/HYP_50M_SR_W.tif')


    # Plot original coordinates
    ax.plot(original_lons, original_lats, marker='o', markersize=5, linestyle='-', color='blue', transform=ccrs.Geodetic(), label='Original Coordinates')
    for i, txt in enumerate(range(1, len(original_lons) + 1)):
        ax.text(original_lons[i], original_lats[i], txt, fontsize=12, color='blue', transform=ccrs.Geodetic())

    # Plot sorted coordinates
    ax.plot(sorted_lons, sorted_lats, marker='o', markersize=5, linestyle='-', color='red', transform=ccrs.Geodetic(), label='Sorted Coordinates')
    for i, txt in enumerate(range(1, len(sorted_lons) + 1)):
        ax.text(sorted_lons[i], sorted_lats[i], txt, fontsize=12, color='red', transform=ccrs.Geodetic())

    # Calculate geodesic center and max radius
    center_lat, center_lon = np.mean(sorted_lats), np.mean(sorted_lons)
    max_distance_nm = max(geodesic((center_lat, center_lon), (lat, lon)).nautical for lat, lon in zip(sorted_lats, sorted_lons))
    plot_geodesic_circle(ax, center_lon, center_lat, max_distance_nm, 'green', f'{max_distance_nm:.2f} NM Enclosing Circle')

    # Plot airports within bounding box
    delta_deg = 100 * 1.852 / 110.574  # Approx conversion of NM to degrees
    bounding_box = box(center_lon - delta_deg, center_lat - delta_deg, center_lon + delta_deg, center_lat + delta_deg)
    airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:3857")  # Ensure the airports are loaded correctly
    plot_airports(ax, bounding_box, airports_gdf, center_lat, center_lon, 100)

    # Display center coordinates and radius
    ax.text(center_lon, center_lat, f"Center: {decimal_degrees_to_dms(center_lat)}, {decimal_degrees_to_dms(center_lon)}\nRadius: {max_distance_nm:.2f} NM",
            fontsize=10, color='green', transform=ccrs.PlateCarree(), ha='left')
    

    # Add title and legend
    plt.legend()
    plt.title(f"Original and Sorted Coordinates with Minimum Enclosing Circle ({max_distance_nm:.2f} NM radius) and Airports")
    ax.format_coord = lambda x, y: format_coord(x, y)
    plt.show()

def show_single_coord_on_map(coord):
    lat, lon = parse_coordinate(coord)
    if lat is None or lon is None:
        messagebox.showwarning('Warning', 'Invalid coordinate for plotting.')
        return

    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    # Remove padding around the plot
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    extent_margin = 1.0
    ax.set_extent([lon - extent_margin, lon + extent_margin, lat - extent_margin, lat + extent_margin], crs=ccrs.PlateCarree())

    plot_base_map(ax, 
                  load_shapefile('shapes/ne_50m_admin_0_countries.shp'), 
                  load_shapefile('shapes/ne_50m_admin_0_breakaway_disputed_areas.shp'),
                  load_shapefile('shapes/ne_50m_admin_0_boundary_lines_disputed_areas.shp'),
                  load_shapefile('shapes/ne_50m_geography_regions_elevation_points.shp'),
                  raster_path='shapes/HYP_50M_SR_W.tif')

    ax.plot(lon, lat, marker='o', color='blue', markersize=8, transform=ccrs.PlateCarree(), label=f'{coord}')
    ax.text(lon, lat, f'{coord}', fontsize=10, color='blue', transform=ccrs.PlateCarree(), ha='left')
    plot_geodesic_circle(ax, lon, lat, 1, 'blue', '1NM Radius')
    plot_geodesic_circle(ax, lon, lat, 5, 'red', '5NM Radius')

    delta_deg = 5 * 1.852 / 110.574
    bounding_box = box(lon - delta_deg, lat - delta_deg, lon + delta_deg, lat + delta_deg)
    airports_gdf = load_shapefile('shapes/world_airports.shp', target_crs="EPSG:3857")
    plot_airports(ax, bounding_box, airports_gdf, lat, lon, 5)

    plt.title('Single Coordinate with 1 NM and 5 NM Radius Circles')
    ax.format_coord = lambda x, y: format_coord(x, y)
    plt.legend()
    plt.show()

def show_on_map(original_coords, sorted_coords):
    if len(original_coords) == 1:
        show_single_coord_on_map(original_coords[0])
    else:
        plot_coordinates(original_coords, sorted_coords)

def draw_coordinates(coords, canvas):
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

        x1, y1 = transform(lats[-1], lons[-1])
        x2, y2 = transform(lats[0], lons[0])
        canvas.create_line(x1, y1, x2, y2, fill="blue")

    except Exception as e:
        messagebox.showwarning('Warning', f'Coordinate drawing error: {e}')
