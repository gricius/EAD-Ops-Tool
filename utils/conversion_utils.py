def convert_units(value, from_unit, to_unit):
    try:
        value = float(value)
        if from_unit == "KM" and to_unit == "NM":
            return value * 0.539957
        elif from_unit == "NM" and to_unit == "KM":
            return value / 0.539957
        elif from_unit == "MT" and to_unit == "FT":
            return value * 3.28084
        elif from_unit == "FT" and to_unit == "MT":
            return value / 3.28084
        else:
            return None
    except ValueError:
        return None
