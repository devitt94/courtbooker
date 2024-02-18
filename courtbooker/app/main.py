from app import api, frontend
from database import Base, engine
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)
fastapi = FastAPI()

fastapi.include_router(api.router)
fastapi.include_router(frontend.router)
