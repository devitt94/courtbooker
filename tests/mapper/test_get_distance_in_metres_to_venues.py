from courtbooker.mapper import get_distance_in_metres_to_venues


def test_get_distance_in_metres_to_venues():
    latitude = 51.5361238
    longitude = -0.0870316

    distance_map = get_distance_in_metres_to_venues(
        (latitude, longitude),
    )

    assert distance_map == {
        "Askegardens": 1112,
        "BethnalGreenGardens": 3453,
        "ClissoldPark": 2658,
        "Finsburypark": 4206,
        "HackneyDowns": 3158,
        "HaggerstonPark": 1687,
        "HighburyTennis": 2538,
        "IslingtonTennisCentreOutdoor": 3369,
        "IslingtonTennisCentreIndoor": 3369,
        "LondonFields": 2602,
        "Millfieldsparkmiddlesex": 4638,
        "Springhillparktennis": 5064,
        "RosemaryGardensTennis": 448,
        "ShoreditchPark": 418,
        "VictoriaPark": 4289,
    }
