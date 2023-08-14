import models
import schemas
from database import Base, engine, get_db_session
from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session
from worker import scrape_sessions

Base.metadata.create_all(bind=engine)
app = FastAPI()


running_task = None


@app.get("/scrape", response_model=schemas.ScrapeTaskResponse)
def scrape(request: Request, db: Session = Depends(get_db_session)):
    global running_task

    if running_task is not None:
        return {
            "message": "ScrapeTask already running",
            "task_id": running_task.id,
        }

    running_task = scrape_sessions.delay()

    return {"message": "ScrapeTask started", "task_id": running_task.id}


@app.get("/courts", response_model=schemas.CourtsResponse)
def courts(request: Request, db: Session = Depends(get_db_session)):
    court_sessions = [
        schemas.CourtSession(
            venue=court_session.venue.name,
            label=court_session.label,
            start_time=court_session.start_time,
            end_time=court_session.end_time,
            cost=court_session.cost,
            url=court_session.url,
        )
        for court_session in db.query(models.CourtSession).all()
    ]

    return {
        "message": "Success",
        "courts": court_sessions,
    }
