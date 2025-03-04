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
        """Retrieve all suppliers."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def add_item(self, item_data, supplier_ids):
        """Insert a new item dynamically and link it to suppliers."""
        columns = ", ".join(item_data.keys())  
        values_placeholders = ", ".join(["%s"] * len(item_data))  

        insert_query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID
        """

        item_id = self.execute_command_returning(insert_query, list(item_data.values()))
        
        if item_id:
            self.link_item_suppliers(item_id[0][0], supplier_ids)  
            return item_id[0][0]
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """Link an item to multiple suppliers in ItemSupplier table."""
        for supplier_id in supplier_ids:
            query = """
            INSERT INTO ItemSupplier (ItemID, SupplierID) 
            VALUES (%s, %s) ON CONFLICT DO NOTHING
            """
            self.execute_command(query, (item_id, supplier_id))
