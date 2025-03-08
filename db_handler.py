import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """General database interaction methods."""

    def __init__(self):
        self.dsn = st.secrets["neon"]["dsn"]

    def get_connection(self):
        try:
            return psycopg2.connect(self.dsn)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def fetch_data(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        conn.close()
        return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame()

    def execute_command(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
        conn.close()

    def execute_command_returning(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return None
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            result = cur.fetchone()
            conn.commit()
        conn.close()
        return result
