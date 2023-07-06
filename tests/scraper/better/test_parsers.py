import pytest

from scraper.better import (
    parse_cost,
    parse_start_end_time,
    parse_availability,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("£5.00", 5.00),
        ("£5.50", 5.50),
        ("£5.5", 5.50),
    ],
)
def test_parse_cost(input, expected):
    assert parse_cost(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("09:00 - 10:00", (9, 10)),
        ("10:00-11:00", (10, 11)),
        ("11 - 12", (11, 12)),
        ("12-13", (12, 13)),
    ],
)
def test_parse_start_end_time(input, expected):
    assert parse_start_end_time(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("0 courts available", 0),
        ("1 court Available", 1),
        ("2 courts available", 2),
        ("3 courts Available", 3),
        ("None available", 0),
        ("not available", 0),
    ],
)
def test_parse_availability(input, expected):
    assert parse_availability(input) == expected

