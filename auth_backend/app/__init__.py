import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "hospitaldb",
    "user": "postgres",
    "password": "posthack",
    "host": "localhost",
    "port": 5432
}


def get_db_connection():
    """Establishes a connection to the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn
