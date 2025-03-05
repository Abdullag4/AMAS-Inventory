import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """Handles all database interactions in a structured and modular way."""

    def __init__(self):
        """Initialize database connection."""
        self.dsn = st.secrets["neon"]["dsn"]

    def get_connection(self):
        """Create a new database connection."""
        try:
            return psycopg2.connect(self.dsn)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def fetch_data(self, query, params=None):
        """Execute a SELECT query and return results as a Pandas DataFrame."""
        conn = self.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
            conn.close()
            return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame()
        return pd.DataFrame()

    def execute_command(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries (No Return)."""
        conn = self.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()
            conn.close()

    def get_items(self):
        """Retrieve all items for editing."""
        query = "SELECT * FROM Item"
        return self.fetch_data(query)

    def update_item(self, item_id, updated_data):
        """Update item details dynamically."""
        if not updated_data:
            return False  # No data to update

        columns = ", ".join([f"{key} = %s" for key in updated_data.keys()])
        values = list(updated_data.values()) + [item_id]

        query = f"""
        UPDATE Item 
        SET {columns}, UpdatedAt = CURRENT_TIMESTAMP
        WHERE ItemID = %s
        """
        self.execute_command(query, values)
        return True  # Update successful
