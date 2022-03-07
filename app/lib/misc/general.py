from math import pi, sin, cos, asin, sqrt


def pop_from_dict(d: dict, k: str):
    if k in d:
        d.pop(k)


def _dtr(angle: float):
    return angle * (pi / 180)


def _get_distance(c_lat: float, c_long: float, p_lat: float, p_long: float):
    earths_radius = 6371

    d_lat = _dtr(p_lat - c_lat)
    d_long = _dtr(p_long - c_long)

    a = sin(d_lat/2) ** 2 + \
        (cos(_dtr(c_lat)) * cos(_dtr(p_lat))) * sin(d_long / 2) ** 2
    c = 2 * asin(sqrt(a))
    d = earths_radius * c

    return d


def within_radius(
    c_lat: float,
    c_long: float,
    p_lat: float,
    p_long: float,
    radius: float
):
    distance = _get_distance(c_lat, c_long, p_lat, p_long)
    return distance < radius
