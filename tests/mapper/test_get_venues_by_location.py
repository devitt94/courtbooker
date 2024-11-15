from unittest.mock import patch

import pytest

from courtbooker.mapper import get_venues_by_location


@pytest.mark.parametrize(
    "distance_map, radius, expected_venues",
    [
        (
            {
                "venue1": 100,
                "venue2": 200,
                "venue3": 300,
            },
            150,
            {"venue1": 100},
        ),
        (
            {
                "venue1": 200,
                "venue2": 100,
                "venue3": 300,
            },
            199,
            {"venue2": 100},
        ),
        (
            {
                "venue1": 300,
                "venue2": 200,
                "venue3": 100,
            },
            240,
            {"venue2": 200, "venue3": 100},
        ),
        (
            {
                "venue1": 200,
                "venue2": 100,
                "venue3": 200,
            },
            99,
            {},
        ),
        (
            {
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
            },
            2000,
            {
                "Askegardens": 1112,
                "HaggerstonPark": 1687,
                "RosemaryGardensTennis": 448,
                "ShoreditchPark": 418,
            },
        ),
    ],
)
def test_get_venues_by_location(distance_map, radius, expected_venues):
    with patch(
        "courtbooker.mapper.get_distance_in_metres_to_venues"
    ) as mock_get_distance_in_metres_to_venues:
        mock_get_distance_in_metres_to_venues.return_value = distance_map

        venues = get_venues_by_location(
            (51.5074, 0.1278),
            radius_in_metres=radius,
        )

        assert venues == expected_venues
