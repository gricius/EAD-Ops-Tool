# EAD OPS Tool
Currently aveilable features:
## Home
Information about the app.
In addition displays content of news.txt file which can be esily edited to provide any important to the user information.
## INO Tool
* Tool to help formating coordinates for NOTAM processing. Extracts coordinates in a different formats from a text, formats to ICAO standard, visualizes extracted coordinates in original order and sorted in order to avoid intersections. To avoid intersections in the polygon and keep all coordinates as in the original text used the Convex Hull algorithm. The Convex Hull is the smallest convex polygon that can enclose all given points, ensuring no intersections within the polygon. In addition original and sorted coordinates can be viewed on map to confirm that coordinates are within the area of responsiblity of a data originator.
* Converters from NM to KM and from M to FT and vice versa.
* To do: Flight Level Calculator for NOTAM processing in case FL999 provided by an originator and heights are provided in AGL (Above Ground Level). The calculator will use internal EAD Ms Excel file Abbreviation and Elevation Tool to find the highest elevation in FIR and to add original height in M  or FT.
## Abbreviation Tool
Code a text to ICAO abbreviation or decode a national or military abbreviation.
## Notepad
A textual editor with find and replace function.
## ToDo
A simple tasks list. You can add or remove a text. The data stored locally in a json file.
## Templates
Stndard comments for Seervice Desk, INO, SDM etc. Possibility to add, edit, delete, reorder or copy a template text to Window Clipboard for pasting the template to another application. The data stored locally in a json file.