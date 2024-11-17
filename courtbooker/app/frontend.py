import logging
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from courtbooker.app.refresh import refresh_court_data
from courtbooker.mapper import InvalidLocationError, get_venues_by_location
from courtbooker.util import (
    get_court_sessions,
    get_latest_update_time,
    get_venues,
)


class SearchType(str, Enum):
    venue = "venueSearch"
    location = "locationSearch"


router = APIRouter(
    prefix="/html",
    tags=["html"],
)

router.mount(
    "/static", StaticFiles(directory="courtbooker/static"), name="static"
)


templates = Jinja2Templates(directory="./courtbooker/templates")


@router.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
):
    all_venues = get_venues()
    last_update_time = get_latest_update_time()

    if last_update_time is not None:
        last_update_time = last_update_time.strftime("%d/%m/%y %H:%M")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "venues": all_venues,
            "last_update_time": last_update_time,
        },
    )


def _return_error_response(request: Request, error_message: str):
    return templates.TemplateResponse(
        "courts.html",
        {
            "request": request,
            "courts": [],
            "error_message": error_message,
        },
    )


def _empty_to_none(value_str: str | None = Query(None)) -> float | None:
    if value_str is None or value_str == "":  # Convert empty string to None
        return None
    return float(value_str)


@router.get("/courts", response_class=HTMLResponse)
def get_courts(
    request: Request,
    search_type: SearchType = Query(SearchType.venue),
    daterange: str = Query(None),
    venues: list[str] | None = Query(None),
    distance_km: float | None = Query(None),
    only_double_headers: str | None = Query(None),
    exclude_working_hours: str | None = Query(None),
    latitude: float | None = Depends(_empty_to_none),
    longitude: float | None = Depends(_empty_to_none),
    postcode: str | None = Query(None),
):
    logging.info(f"Venues: {venues}")
    logging.info(f"Daterange: {daterange}")
    logging.info(f"Only multiple sessions: {only_double_headers}")

    if latitude == "":
        latitude = None
    if longitude == "":
        longitude = None

    if daterange is None:
        start_time_gte, start_time_lte = None, None
    else:
        begin, end = daterange.split(" - ")
        start_time_gte = datetime.strptime(begin, "%d/%m/%y %H:%M")
        start_time_lte = datetime.strptime(end, "%d/%m/%y %H:%M")

    if search_type == SearchType.location:
        location_valid = (
            (latitude is not None) and (longitude is not None)
        ) ^ (postcode is not None)
        if not location_valid:
            return _return_error_response(
                request,
                "Location is not determinable. Specify exactly one of coordinates or postcode must be provided when using location",
            )

        elif distance_km is None:
            _return_error_response(
                request, "Distance must be provided when using location search"
            )

        if latitude and longitude:
            location = (latitude, longitude)
        else:
            location = postcode

        try:
            venues = get_venues_by_location(
                location=location,
                radius_in_metres=distance_km * 1000,
            )
        except InvalidLocationError as e:
            return _return_error_response(request, str(e))

        if not venues:
            return _return_error_response(
                request, "No venues found within the specified range"
            )

        venues = list(venues.keys())

    court_sessions = get_court_sessions(
        venues=venues,
        start_time_after=start_time_gte,
        start_time_before=start_time_lte,
        only_double_headers=only_double_headers == "on",
        exclude_working_hours=exclude_working_hours == "on",
    )

    return templates.TemplateResponse(
        "courts.html",
        {
            "request": request,
            "venues": len(venues),
            "courts": court_sessions,
            "error_message": None,
        },
    )


@router.get("/refresh-courts", response_class=HTMLResponse)
def refresh_data(request: Request):
    court_task = refresh_court_data()
    return templates.TemplateResponse(
        "refresh-data.html",
        {
            "request": request,
            "message": court_task["message"],
        },
    )
