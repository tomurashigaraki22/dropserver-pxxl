import math

def haversine(coord1, coord2):
    # Radius of the Earth in kilometers
    R = 6371.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in kilometers

def find_closest_rider(user_location, available_riders):
    closest_rider = None
    min_distance = float('inf')

    for rider in available_riders:
        rider_location = (rider['latitude'], rider['longitude'])
        distance = haversine((user_location['latitude'], user_location['longitude']), rider_location)

        if distance < min_distance:
            min_distance = distance
            closest_rider = rider

    return closest_rider