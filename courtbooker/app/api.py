from datetime import datetime

from fastapi import APIRouter

from courtbooker import schemas
from courtbooker.app.refresh import refresh_court_data
from courtbooker.mapper import get_venues_by_location
from courtbooker.util import get_court_sessions

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.get("/courts", response_model=schemas.CourtsResponse)
def courts(
    venues: list[str] | None = None,
    start_time_after: datetime | None = None,
    start_time_before: datetime | None = None,
    only_double_headers: bool = False,
    exclude_working_hours: bool = False,
    use_location: bool = False,
    latitude: float | None = None,
    longitude: float | None = None,
    distance_km: float | None = None,
):
    if use_location:
        if latitude is None or longitude is None or distance_km is None:
            return {
                "message": "Latitude and longitude must be provided when using location",
            }

        if venues is not None:
            return {
                "message": "Venues cannot be provided when using location",
            }

        venue_distance_map = get_venues_by_location(
            latitude=latitude,
            longitude=longitude,
            radius_in_metres=distance_km * 1000,
        )

        venues = list(venue_distance_map.keys())

    court_sessions = get_court_sessions(
        venues=venues,
        start_time_after=start_time_after,
        start_time_before=start_time_before,
        only_double_headers=only_double_headers,
        exclude_working_hours=exclude_working_hours,
    )

    return {
        "message": "Success",
        "courts": court_sessions,
    }


@router.get("/refresh-courts")
def refresh_courts():
    refresh_court_data()
