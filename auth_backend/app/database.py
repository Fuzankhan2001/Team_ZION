import psycopg
from psycopg.rows import dict_row

DB_CONFIG = {
    "dbname": "hospitaldb",
    "user": "postgres",
    "password": "posthack",
    "host": "localhost",
    "port": 5432
}


def get_db_connection():
    """Establishes a connection to the database."""
    conn = psycopg.connect(**DB_CONFIG, row_factory=dict_row)
    return conn


def execute_query(query, params=None, fetch_one=False, commit=False):
    """
    Helper to run queries.
    Supports 'INSERT ... RETURNING' by fetching BEFORE committing.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)

        result = None
        attempted_fetch = False

        if fetch_one:
            result = cur.fetchone()
            attempted_fetch = True
        elif cur.description:
            result = cur.fetchall()
            attempted_fetch = True

        is_write = query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
        if commit or is_write:
            conn.commit()

        # For SELECT queries: return result as-is (None = not found, list/dict = found)
        # For write queries with no RETURNING: return True to indicate success
        return result if attempted_fetch else True

    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        conn.close()
