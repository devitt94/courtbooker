import googlemaps

from courtbooker import app_settings

VENUE_NAME_TO_MAPS_NAME = {
    "Joe White Gardens Tennis Court": ["Askegardens"],
    "Bethnal Green Gardens Tennis Courts": ["BethnalGreenGardens"],
    "Clissold Park Tennis Courts": ["ClissoldPark"],
    "Finsbury Park Tennis Courts": ["Finsburypark"],
    "Hackney Downs Tennis Courts": ["HackneyDowns"],
    "Haggerston Park Tennis Courts": ["HaggerstonPark"],
    "Highbury Fields Tennis Courts": ["HighburyTennis"],
    "Islington Tennis Centre and Gym": [
        "IslingtonTennisCentreOutdoor",
        "IslingtonTennisCentreIndoor",
    ],
    "London Fields Tennis Courts": ["LondonFields"],
    "Millfields Tennis Courts": ["Millfieldsparkmiddlesex"],
    "Spring Hill Tennis Courts": ["Springhillparktennis"],
    "Rosemary Gardens Tennis Court": ["RosemaryGardensTennis"],
    "Britannia Leisure Centre": ["ShoreditchPark"],
    "Tower Hamlets Tennis - Victoria Park, East London": ["VictoriaPark"],
}


def get_distance_in_metres_to_venues(origin: str) -> dict[str, int]:
    gmaps = googlemaps.Client(key=app_settings.GOOGLE_MAPS_API_KEY)

    destinations = list(VENUE_NAME_TO_MAPS_NAME.keys())

    matrix = gmaps.distance_matrix(
        origin,
        list(VENUE_NAME_TO_MAPS_NAME.keys()),
        mode="walking",
    )

    distances = matrix["rows"][0]["elements"]

    return {
        destination: distance["distance"]["value"]
        for destination, distance in zip(destinations, distances)
    }
