import datetime

import pytest
from courtbooker.scraper.clubspark import (
    _get_dt_from_mins_and_date,
)


@pytest.mark.parametrize(
    "mins, date, expected",
    [
        (0, datetime.date(2021, 1, 1), datetime.datetime(2021, 1, 1, 0, 0)),
        (60, datetime.date(2021, 1, 1), datetime.datetime(2021, 1, 1, 1, 0)),
        (120, datetime.date(2021, 1, 1), datetime.datetime(2021, 1, 1, 2, 0)),
        (180, datetime.date(2021, 1, 1), datetime.datetime(2021, 1, 1, 3, 0)),
    ],
)
def test__get_dt_from_mins_and_date(
    mins: int, date: datetime.date, expected: datetime.datetime
):
    assert _get_dt_from_mins_and_date(mins, date) == expected
