import logging
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from util import get_court_sessions, get_latest_update_time, get_venues

router = APIRouter(
    prefix="/html",
    tags=["html"],
)

router.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="./templates")


@router.get("/courts", response_class=HTMLResponse)
def get_courts(
    request: Request,
    venues: list[str] = Query(None),
    daterange: str = Query(None),
):
    logging.info(f"Venues: {venues}")
    logging.info(f"Daterange: {daterange}")

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
    )

    all_venues = get_venues()
    last_update_time = get_latest_update_time()

    return templates.TemplateResponse(
        "courts.html",
        {
            "request": request,
            "courts": court_sessions,
            "venues": all_venues,
            "last_update_time": last_update_time.strftime("%d/%m/%y %H:%M"),
        },
    )
