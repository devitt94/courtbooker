import logging

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
def get_courts(request: Request, venues: list[str] = Query(None)):
    if isinstance(venues, str):
        venues = [venues]
    logging.warning(f"Venues: {venues}")
    court_sessions = get_court_sessions(venues=venues)

    return templates.TemplateResponse(
        "courts.html", {"request": request, "courts": court_sessions}
    )
