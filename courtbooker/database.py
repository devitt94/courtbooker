from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from courtbooker.settings import settings

engine = create_engine(settings.POSTGRES_CONNECTION_STRING)

Base = declarative_base()


class DbSession:
    def __init__(self, read_only=False):
        self.read_only = read_only

    def __enter__(self):
        self.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.read_only:
            self.session.commit()
        self.session.close()

        if exc_type:
            raise exc_type(exc_val)
