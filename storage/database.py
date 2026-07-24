from sqlalchemy import create_engine, text
from config import DB_URL
from pgvector.sqlalchemy import Vector
from sqlalchemy import event
from pgvector.psycopg2 import register_vector
import psycopg2


engine = create_engine(DB_URL)


@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    register_vector(dbapi_connection)

def get_connection():
    return engine.connect()
