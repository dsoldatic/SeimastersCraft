import os
from sqlmodel import SQLModel, create_engine, Session

# koristi env varijablu DATABASE_URL ili fallback na SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///watchcraft.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)

def init_db():
    SQLModel.metadata.create_all(engine)