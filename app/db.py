import psycopg2
from .config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_orders_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            tgid INTEGER NOT NULL,
            username TEXT NOT NULL,
            ordertext TEXT NOT NULL,
            status TEXT NOT NULL,
            count INTEGER,
            price INTEGER,
            location TEXT,
            archive INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def init_db():
    create_orders_table()


