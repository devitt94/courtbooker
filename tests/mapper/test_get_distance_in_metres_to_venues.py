from unittest.mock import patch

from courtbooker.mapper import get_distance_in_metres_to_venues


def test_get_distance_in_metres_to_venues():
    latitude = 51.5361238
    longitude = -0.0870316

    with patch(
        "courtbooker.mapper.googlemaps.Client"
    ) as mock_googlemaps_client:
        mock_googlemaps_client.return_value.distance_matrix.return_value = {
            "rows": [
                {
                    "elements": [
                        {"distance": {"value": 1112}},
                        {"distance": {"value": 3453}},
                        {"distance": {"value": 2658}},
                        {"distance": {"value": 4206}},
                        {"distance": {"value": 3158}},
                        {"distance": {"value": 1687}},
                        {"distance": {"value": 2538}},
                        {"distance": {"value": 3369}},
                        {"distance": {"value": 3369}},
                        {"distance": {"value": 2601}},
                        {"distance": {"value": 4638}},
                        {"distance": {"value": 5064}},
                        {"distance": {"value": 448}},
                        {"distance": {"value": 418}},
                        {"distance": {"value": 4289}},
                    ]
                }
            ]
        }

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
            "LondonFields": 2601,
            "Millfieldsparkmiddlesex": 4638,
            "Springhillparktennis": 5064,
            "RosemaryGardensTennis": 448,
            "ShoreditchPark": 418,
            "VictoriaPark": 4289,
        }
