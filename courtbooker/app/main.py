from fastapi import FastAPI

from courtbooker.app import api, frontend
from courtbooker.database import Base, engine

Base.metadata.create_all(bind=engine)
fastapi = FastAPI()

fastapi.include_router(api.router)
fastapi.include_router(frontend.router)
