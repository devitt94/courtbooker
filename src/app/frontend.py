import logging
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from util import get_court_sessions

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
    start_time_gte: datetime = None,
    start_time_lte: datetime = None,
):
    logging.warning(f"Venues: {venues}")
    court_sessions = get_court_sessions(
        venues=venues,
        start_time_after=start_time_gte,
        start_time_before=start_time_lte,
    )

    return templates.TemplateResponse(
        "courts.html", {"request": request, "courts": court_sessions}
    )
