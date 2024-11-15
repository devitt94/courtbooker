import googlemaps

from courtbooker.settings import app_settings

VENUE_NAME_TO_GOOGLE_MAPS_NAME = {
    "Askegardens": "Joe White Gardens Tennis Court",
    "BethnalGreenGardens": "Bethnal Green Gardens Tennis Courts",
    "ClissoldPark": "Clissold Park Tennis Courts",
    "Finsburypark": "Finsbury Park Tennis Courts",
    "HackneyDowns": "Hackney Downs Tennis Courts",
    "HaggerstonPark": "Haggerston Park Tennis Courts",
    "HighburyTennis": "Highbury Fields Tennis Courts",
    "IslingtonTennisCentreOutdoor": "Islington Tennis Centre and Gym",
    "IslingtonTennisCentreIndoor": "Islington Tennis Centre and Gym",
    "LondonFields": "London Fields Tennis Courts",
    "Millfieldsparkmiddlesex": "Millfields Tennis Courts",
    "Springhillparktennis": "Spring Hill Tennis Courts",
    "RosemaryGardensTennis": "Rosemary Gardens Tennis Court",
    "ShoreditchPark": "Britannia Leisure Centre",
    "VictoriaPark": "Tower Hamlets Tennis - Victoria Park, East London",
}


def get_distance_in_metres_to_venues(
    origin: str | tuple[float, float]
) -> dict[str, int]:
    gmaps = googlemaps.Client(key=app_settings.GOOGLE_MAPS_API_KEY)

    destinations = list(VENUE_NAME_TO_GOOGLE_MAPS_NAME.values())

    matrix = gmaps.distance_matrix(
        origin,
        destinations,
        mode="walking",
    )

    distances = matrix["rows"][0]["elements"]

    return {
        destination: distance["distance"]["value"]
        for destination, distance in zip(destinations, distances)
    }


def get_venues_by_location(
    latitiude: float,
    longitude: float,
    radius: float,
) -> dict[str, float]:
    distance_map = get_distance_in_metres_to_venues(
        (latitiude, longitude),
    )

    venues = {
        venue: distance
        for venue, distance in distance_map.items()
        if distance <= radius
    }

    return venues
