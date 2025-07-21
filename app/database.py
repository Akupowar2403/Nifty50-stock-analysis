
# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite database file in the project root folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./stocks.db"

# The connect_args is required for SQLite with SQLAlchemy in multi-threaded environments (like FastAPI's dev server)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# This SessionLocal class will be used to generate new DB sessions for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

