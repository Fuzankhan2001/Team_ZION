import psycopg2
from psycopg2.extras import RealDictCursor

# Update with your credentials
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

def execute_query(query, params=None, fetch_one=False, commit=False):
    """
    Helper to run queries.
    Fix: Now supports 'INSERT ... RETURNING' by fetching BEFORE committing.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        
        result = None
        
        # 1. Fetch Data (if requested or available)
        if fetch_one:
            result = cur.fetchone()
        elif cur.description: # If the query returns rows (like SELECT)
            result = cur.fetchall()
            
        # 2. Commit (Save to Hard Drive)
        # We check explicit 'commit' flag OR if it looks like a write operation
        is_write = query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
        if commit or is_write:
            conn.commit()
            
        # 3. Return the captured result, or True if just a success signal
        return result if result is not None else True

    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        conn.close()