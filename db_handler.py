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

    def get_suppliers(self):
        """Retrieve all suppliers and rename columns for consistency."""
        query = "SELECT supplierid, suppliername FROM supplier"
        df = self.fetch_data(query)

        # ✅ Rename columns to expected names
        df.columns = df.columns.str.lower()
        df.rename(columns={"supplierid": "SupplierID", "suppliername": "SupplierName"}, inplace=True)

        if df.empty:
            st.warning("⚠️ No suppliers found in the database!")
        else:
            st.write("🔍 Supplier Table Columns:", df.columns.tolist())

        return df

    def get_items(self):
        """Retrieve all items for editing."""
        query = """
        SELECT itemid, itemnameenglish, classcat, departmentcat, sectioncat, 
               familycat, subfamilycat, shelflife, origincountry, manufacturer, 
               brand, barcode, unittype, packaging, itempicture, threshold, 
               averagerequired
        FROM item
        """
        df = self.fetch_data(query)

        # ✅ Normalize column names
        df.columns = df.columns.str.lower()
        return df

