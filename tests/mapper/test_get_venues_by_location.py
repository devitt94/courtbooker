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
    ],
)
def test_get_venues_by_location(distance_map, radius, expected_venues):
    with patch(
        "courtbooker.mapper.get_distance_in_metres_to_venues"
    ) as mock_get_distance_in_metres_to_venues:
        mock_get_distance_in_metres_to_venues.return_value = distance_map

        venues = get_venues_by_location(
            latitiude=51.5074,
            longitude=0.1278,
            radius=radius,
        )

        assert venues == expected_venues
