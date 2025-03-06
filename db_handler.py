import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """Handles all database interactions."""

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
        """Execute INSERT, UPDATE, DELETE queries."""
        conn = self.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()
            conn.close()

    ### 🔽🔽 NEW METHODS FOR MANAGING DROPDOWNS 🔽🔽 ###
    
    def get_dropdown_values(self, section):
        """Retrieve all values for a specific section from Dropdowns table."""
        query = "SELECT Value FROM Dropdowns WHERE Section = %s"
        result = self.fetch_data(query, (section,))
        return result["value"].tolist() if not result.empty else []

    def add_dropdown_value(self, section, value):
        """Add a new value to a specific section in the Dropdowns table."""
        query = """
        INSERT INTO Dropdowns (Section, Value) 
        VALUES (%s, %s) 
        ON CONFLICT (Section, Value) DO NOTHING
        """
        self.execute_command(query, (section, value))

    def delete_dropdown_value(self, section, value):
        """Delete a value from a specific section in the Dropdowns table."""
        query = "DELETE FROM Dropdowns WHERE Section = %s AND Value = %s"
        self.execute_command(query, (section, value))

    def get_all_sections(self):
        """Retrieve all unique sections from the Dropdowns table."""
        query = "SELECT DISTINCT Section FROM Dropdowns"
        result = self.fetch_data(query)
        return result["section"].tolist() if not result.empty else []
