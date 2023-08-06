from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(settings.POSTGRES_CONNECTION_STRING)

Base = declarative_base()

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db_session():
    try:
        yield db_session
    finally:
        db_session.close()
