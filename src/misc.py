from datetime import datetime, timezone
import re
import math

def calculate_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    angle_radians = math.atan2(dy, dx)
    
    angle_degrees = math.degrees(angle_radians)
    
    return angle_degrees

def parse_identity_number(str: str | None):
    if not str:
        raise ValueError()

    pattern = re.compile(r"^(\d{2})(\d{2})(\d{2})(\d{4})([0-1])\d{2}$")
    match = pattern.match(str)

    if not match:
        raise ValueError()

    year, month, day, serial, citizenship_flag = match.groups()

    if int(month) > 12:
        raise ValueError()

    if int(day) > 31:
        raise ValueError()

    current_year = datetime.now(timezone.utc).year
    century = (current_year // 100) * 100

    year = century + int(year) if century + \
        int(year) <= current_year else century - 100 + int(year)

    return {
        "citizen": citizenship_flag == "0",
        "date_of_birth": f"{year:04d}-{month}-{day}",
        "gender": "FEMALE" if int(serial) < 5000 else "MALE",
        "permanent_resident": citizenship_flag == "1"
    }
