# utils/coordinate_utils.py
import re
from tkinter import messagebox
import math
from math import atan2

def extract_coordinates(text):
    """
    Extracts coordinates from the given text using predefined regex patterns.
    """
    patterns = [
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{1})([NS])(\d{3})(\d{2})(\d{2}\.\d{1})([EW])'), # 123456.7N123456.7E
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{2})([NS])(\d{3})(\d{2})(\d{2}\.\d{2})([EW])'), # 123456.78N123456.78E
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{3})([NS])(\d{3})(\d{2})(\d{2}\.\d{3})([EW])'), # 123456.789N123456.789E
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{4})([NS])(\d{3})(\d{2})(\d{2}\.\d{4})([EW])'), # 123456.7890N123456.7890E
        re.compile(r'(\d{2})(\d{2})(\d{2}\d{2})([NS])(\d{3})(\d{2})(\d{2}\d{2})([EW])'), # 12345600N12345600E
        re.compile(r'(\d{2})(\d{2})(\d{2})([NS])(\d{3})(\d{2})(\d{2})([EW])'), # 123456N123456E
        re.compile(r'(\d{2})(\d{2})([NS])(\d{3})(\d{2})([EW])'), # 1234N12345E
        re.compile(r'([NS])(\d{2})(\d{2})(\d{2})([EW])(\d{3})(\d{2})(\d{2})'), # N123456E123456
        re.compile(r'([NS])(\d{2})(\d{2})(\d{2}\.\d{2})([EW])(\d{3})(\d{2})(\d{2}\.\d{2})') # N123456.78E123456.78
    ]
    # TODO: Add more patterns to match different coordinate formats
    # invalid_patterns = [
    #     re.compile(r'(\d{5}({NS})(\d{7}({EW}))'), # 12345N1234567E
    #     re.compile(r'(\d{6}({NS})(\d{6}({EW}))'), # 123456N123456E
    #     re.compile(r'(\d{5}({NS})(\d{6}({EW}))'), # 12345N123456E
    #     re.compile(r'(\d{4}({NS})(\d{6}({EW}))'), # 1234N123456E
    #     re.compile(r'(\d{4}({NS})(\d{4}({EW}))'), # 1234N1234E
    #     re.compile(r'(\d{1}\.\d{5}({NS})(\d{1}\.\d{5}({EW}))'), # 1.23456N1.23456E
    #     re.compile(r'(\d{1}\.\d{4}({NS})(\d{1}\.\d{4}({EW}))'), # 1.2345N1.2345E
    #     re.compile(r'(\d{1}\.\d{6}(\d{1}\.\d{5})'), # 1.234561.23456
    #     re.compile(r'(\d{1}\.\d{5}(\d{1}\.\d{4})'), # 1.23451.2345
    # ]

    # # to be trimmed patterns
    # coord_to_be_trimmed = [
    #    re.compile(r'\d{7,10}[NS]\d{8,11}[EW]'), # from 7 to 10 digits N/S and 8 to 11 digits E/W
    #    re.compile(r'\d{5}[NS]\d{7}[EW]'), # 5 digits N/S and 7 digits E/W
    #    re.compile(r'\d{5}[NS]\d{6}[EW]'), # 5 digits N/S and 6 digits E/W
    #    re.compile(r'\d{4}[NS]\d{6}[EW]'), # 4 digits N/S and 6 digits E/W
    # ]

    
    # Clean the input text
    cleaned_text = text.replace('\n', '').replace('\r', '').replace(' ', '').replace('/', '').replace(',', '').replace("'", "").replace('DEG', '').replace('-', '')
    coords = []
    invalid_coords = []

    for pattern in patterns:
        matches = pattern.findall(cleaned_text)
        for match in matches:
            coord = format_coordinates(match)
            if coord:
                coords.append(coord)
            else:
                invalid_coords.append(''.join(match))

    return coords, invalid_coords

def format_coordinates(match):
    """
    Formats the matched coordinate tuple into a standardized string.
    """
    try:
        if len(match) == 8 and match[0].isdigit():
            return f"{match[0]}{match[1]}{match[2][:2]}{match[3]}{match[4]}{match[5]}{match[6][:2]}{match[7]}"
        elif len(match) == 8 and match[0] in 'NS':
            return f"{match[1]}{match[2]}{match[3][:2]}{match[0]}{match[5]}{match[6]}{match[7][:2]}{match[4]}"
        elif len(match) == 6:
            return f"{match[0]}{match[1]}{match[2]}{match[3]}{match[4]}{match[5]}"
        elif len(match) == 7:
            return f"{match[0]}{match[1]}{match[2]}{match[3]}{match[4]}{match[5]}{match[6]}"
        elif len(match) == 10:
            return f"{match[0]}{match[1]}{match[2]}{match[4]}{match[5]}{match[6]}{match[7]}{match[9]}"
        elif len(match) == 12:
            return f"{match[0]}{match[1]}{match[2]}{match[5]}{match[6]}{match[7]}{match[8]}{match[11]}"
        else:
            return None
    except (IndexError, TypeError) as e:
        messagebox.showwarning('Warning', f'Coordinate formatting error: {e}')
        return None

def parse_coordinate(coord):
    """
    Parses a coordinate string into latitude and longitude.
    """
    match = re.match(r'(\d{2})(\d{2})(\d{2})([NS])(\d{3})(\d{2})(\d{2})([EW])', coord)
    if match:
        return convert_to_decimal(match)
    match = re.match(r'(\d{2})(\d{2})([NS])(\d{3})([EW])', coord)
    if match:
        return convert_to_decimal(match)
    match = re.match(r'(\d{2})(\d{2})(\d{2})([NS])(\d{3})(\d{2})(\d{2})([EW])', coord)
    if match:
        return convert_to_decimal(match)

    return None, None

def convert_to_decimal(match):
    """
    Converts a regex match object to decimal latitude and longitude.
    """
    try:
        if len(match.groups()) == 8:
            lat_deg = int(match[1])
            lat_min = int(match[2])
            lat_sec = float(match[3])
            lat_dir = match[4]
            lon_deg = int(match[5])
            lon_min = int(match[6])
            lon_sec = float(match[7])
            lon_dir = match[8]

            lat = lat_deg + lat_min / 60 + lat_sec / 3600
            if lat_dir == 'S':
                lat = -lat
            lon = lon_deg + lon_min / 60 + lon_sec / 3600
            if lon_dir == 'W':
                lon = -lon

            return lat, lon
        elif len(match.groups()) == 6:
            lat_deg = int(match[1])
            lat_min = int(match[2])
            lat_dir = match[3]
            lon_deg = int(match[4])
            lon_min = int(match[5])
            lon_dir = match[6]

            lat = lat_deg + lat_min / 60
            if lat_dir == 'S':
                lat = -lat
            lon = lon_deg + lon_min / 60
            if lon_dir == 'W':
                lon = -lon

            return lat, lon
    except (ValueError, TypeError) as e:
        messagebox.showwarning('Warning', f'Coordinate conversion error: {e}')
        return None, None

import math

from math import atan2

def sort_coordinates(coords):
    """
    Sorts coordinates to form a simple polygon without intersections.
    """
    # Parse the coordinates
    parsed_coords = [parse_coordinate(coord) for coord in coords]
    parsed_coords = [coord for coord in parsed_coords if coord != (None, None)]

    # Calculate the centroid
    centroid = (
        sum(point[0] for point in parsed_coords) / len(parsed_coords),
        sum(point[1] for point in parsed_coords) / len(parsed_coords)
    )

    # Sort points by polar angle with respect to the centroid
    sorted_points = sorted(parsed_coords, key=lambda point: atan2(point[1] - centroid[1], point[0] - centroid[0]))

    # Map back to the original coordinates format
    sorted_coords = [coords[parsed_coords.index(point)] for point in sorted_points]

    return sorted_coords

# Existing convex hull function to compute the convex boundary for reference
def convex_hull(points):
    """
    Computes the convex hull of a set of 2D points.
    Returns the vertices of the convex hull in counter-clockwise order.
    """
    points = sorted(points)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]




def trim_coordinates(coords):
    trimmed_coords = []
    for coord in coords:
        # Check if the coordinate is in the expected compact format (e.g., 574706N0614453E)
        if len(coord) == 15 and (coord[-1] in ['N', 'S'] or coord[-1] in ['E', 'W']):
            # Latitude: First 7 characters (DDMMSS[N/S])
            degrees_lat = coord[:2]
            minutes_lat = coord[2:4]
            lat_direction = coord[6]

            # Longitude: Next 8 characters (DDDMMSS[E/W])
            degrees_lon = coord[7:10]
            minutes_lon = coord[10:12]
            lon_direction = coord[-1]

            # Format to DDMM[N/S] DDDMM[E/W], omitting seconds
            lat_str = f"{degrees_lat}{minutes_lat}{lat_direction}"
            lon_str = f"{degrees_lon}{minutes_lon}{lon_direction}"

            trimmed_coords.append(f"{lat_str}{lon_str}")
        else:
            print(f"Invalid coordinate format: {coord}")
            continue

    return trimmed_coords

