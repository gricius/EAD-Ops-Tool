import re
from tkinter import messagebox

def extract_coordinates(text):
    """
    Extracts coordinates from the given text using predefined regex patterns.
    """
    patterns = [
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{1})([NS])(\d{3})(\d{2})(\d{2}\.\d{1})([EW])'),
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{2})([NS])(\d{3})(\d{2})(\d{2}\.\d{2})([EW])'),
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{3})([NS])(\d{3})(\d{2})(\d{2}\.\d{3})([EW])'),
        re.compile(r'(\d{2})(\d{2})(\d{2}\.\d{4})([NS])(\d{3})(\d{2})(\d{2}\.\d{4})([EW])'),
        re.compile(r'(\d{2})(\d{2})(\d{2}\d{2})([NS])(\d{3})(\d{2})(\d{2}\d{2})([EW])'),
        re.compile(r'(\d{2})(\d{2})(\d{2})([NS])(\d{3})(\d{2})(\d{2})([EW])'),
        re.compile(r'(\d{2})(\d{2})([NS])(\d{3})(\d{2})([EW])'),
        re.compile(r'([NS])(\d{2})(\d{2})(\d{2})([EW])(\d{3})(\d{2})(\d{2})'),
        re.compile(r'([NS])(\d{2})(\d{2})(\d{2}\.\d{2})([EW])(\d{3})(\d{2})(\d{2}\.\d{2})')
    ]
    
    # Clean the input text
    cleaned_text = text.replace('\n', '').replace('\r', '').replace(' ', '').replace('/', '').replace(',', '.').replace("'", "").replace('DEG', '').replace('-', '')
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

def sort_coordinates(coords):
    """
    Sorts coordinates to avoid intersections in the polygon.
    """
    parsed_coords = [parse_coordinate(coord) for coord in coords]
    parsed_coords = [coord for coord in parsed_coords if coord != (None, None)]
    hull_points = convex_hull(parsed_coords)
    sorted_coords = [coords[parsed_coords.index(point)] for point in hull_points]
    return sorted_coords

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
