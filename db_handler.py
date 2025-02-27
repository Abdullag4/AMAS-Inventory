import streamlit as st
import psycopg2

def get_connection():
    """Establish connection using DSN stored in Streamlit secrets."""
    try:
        conn = psycopg2.connect(st.secrets["neon"]["dsn"])
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(sql, params=None):
    """Execute SELECT queries and return fetched rows."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
        conn.close()
        return rows
    return []

def run_command(sql, params=None):
    """Execute INSERT, UPDATE, DELETE queries without returning data."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
        conn.close()

def run_command_returning(sql, params=None):
    """Execute commands like INSERT ... RETURNING and return rows."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            conn.commit()
        conn.close()
        return rows
    return []
