import logging
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from courtbooker.app.refresh import refresh_court_data
from courtbooker.util import (
    get_court_sessions,
    get_latest_update_time,
    get_venues,
)

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


@router.get("/courts", response_class=HTMLResponse)
def get_courts(
    request: Request,
    venues: list[str] = Query(None),
    daterange: str = Query(None),
    only_double_headers: str = Query(None),
    exclude_working_hours: str = Query(None),
):
    logging.info(f"Venues: {venues}")
    logging.info(f"Daterange: {daterange}")
    logging.info(f"Only multiple sessions: {only_double_headers}")

    if daterange is None:
        start_time_gte, start_time_lte = None, None
    else:
        begin, end = daterange.split(" - ")
        start_time_gte = datetime.strptime(begin, "%d/%m/%y %H:%M")
        start_time_lte = datetime.strptime(end, "%d/%m/%y %H:%M")

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
            "courts": court_sessions,
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
