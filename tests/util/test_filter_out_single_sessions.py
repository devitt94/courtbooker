from datetime import datetime, timedelta

import pytest

from courtbooker.schemas import CourtSession
from courtbooker.util import filter_out_single_sessions


@pytest.mark.parametrize(
    "venue_times, expected",
    [
        ([], []),
        (
            [
                {"venue": "venue1", "time": "2022-01-01T00:00:00"},
            ],
            [],
        ),
        (
            [
                {"venue": "venue1", "time": "2022-01-01T00:00:00"},
                {"venue": "venue1", "time": "2022-01-01T02:00:00"},
            ],
            [],
        ),
        (
            [
                {"venue": "venue1", "time": "2022-01-01T00:00:00"},
                {"venue": "venue2", "time": "2022-01-01T01:00:00"},
                {"venue": "venue3", "time": "2022-01-01T02:00:00"},
            ],
            [],
        ),
        (
            [
                {"venue": "venue1", "time": "2022-01-01T00:00:00"},
                {"venue": "venue1", "time": "2022-01-01T01:00:00"},
                {"venue": "venue2", "time": "2022-01-01T02:00:00"},
            ],
            [
                {"venue": "venue1", "time": "2022-01-01T00:00:00"},
            ],
        ),
    ],
)
def test_filter_out_single_sessions(venue_times, expected):
    court_sessions = [
        CourtSession(
            venue=venue_time["venue"],
            label="test-label",
            cost=10,
            start_time=datetime.strptime(
                venue_time["time"], "%Y-%m-%dT%H:%M:%S"
            ),
            end_time=datetime.strptime(venue_time["time"], "%Y-%m-%dT%H:%M:%S")
            + timedelta(hours=1),
            url="test-url",
        )
        for venue_time in venue_times
    ]

    filtered_sessions = filter_out_single_sessions(court_sessions)
    assert len(filtered_sessions) == len(expected)
    for session, expected_session in zip(filtered_sessions, expected):
        assert session.venue == expected_session["venue"]
        assert session.start_time == datetime.strptime(
            expected_session["time"], "%Y-%m-%dT%H:%M:%S"
        )
