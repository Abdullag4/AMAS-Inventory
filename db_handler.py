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

    def execute_command_returning(self, query, params=None):
        """Execute an INSERT or UPDATE query and return affected rows."""
        conn = self.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                rows = cur.fetchall()
                conn.commit()
            conn.close()
            return rows
        return []

    def get_suppliers(self):
        """Retrieve all suppliers from the database."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def get_items(self):
        """Retrieve all items for editing."""
        query = """
        SELECT ItemID, ItemNameEnglish, ClassCat, DepartmentCat, SectionCat, FamilyCat, 
               SubFamilyCat, ShelfLife, OriginCountry, Manufacturer, Brand, Barcode, 
               UnitType, Packaging, Threshold, AverageRequired 
        FROM Item
        """
        return self.fetch_data(query)

    def update_item(self, item_id, updated_data):
        """Update item details based on provided data."""
        if not updated_data:
            st.warning("⚠️ No changes detected. Nothing to update.")
            return

        set_clause = ", ".join([f"{key} = %s" for key in updated_data.keys()])
        values = list(updated_data.values()) + [item_id]

        query = f"""
        UPDATE Item
        SET {set_clause}, UpdatedAt = CURRENT_TIMESTAMP
        WHERE ItemID = %s
        """

        self.execute_command(query, values)
        st.success("✅ Item updated successfully!")
