from sqlalchemy import create_engine, text
from config import DB_URL

engine = create_engine(DB_URL)


def get_connection():
    return engine.connect()
