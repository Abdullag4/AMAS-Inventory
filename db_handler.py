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

    def get_items(self):
        """Retrieve all items for editing."""
        query = """
        SELECT itemid, itemnameenglish, classcat, departmentcat, sectioncat, 
               familycat, subfamilycat, shelflife, origincountry, manufacturer, 
               brand, barcode, unittype, packaging, threshold, averagerequired, 
               itempicture, createdat, updatedat 
        FROM item
        """
        return self.fetch_data(query)

    def update_item(self, item_id, updated_data):
        """Update item details in the database."""
        if not updated_data:
            st.warning("⚠️ No changes made.")
            return
        
        set_clause = ", ".join(f"{col} = %s" for col in updated_data.keys())
        query = f"""
        UPDATE item
        SET {set_clause}, updatedat = CURRENT_TIMESTAMP
        WHERE itemid = %s
        """
        
        params = list(updated_data.values()) + [item_id]
        self.execute_command(query, params)
        st.success("✅ Item updated successfully!")

    def get_suppliers(self):
        """Retrieve all supplier records."""
        query = "SELECT supplierid, suppliername FROM supplier"
        return self.fetch_data(query)

    def add_item(self, item_data, supplier_ids):
        """Insert a new item and link it to suppliers."""
        columns = ", ".join(item_data.keys())  # Convert dict keys to column names
        values_placeholders = ", ".join(["%s"] * len(item_data))  # Create "%s, %s, %s..."
        
        query = f"""
        INSERT INTO item ({columns}, createdat, updatedat)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING itemid
        """

        item_id = self.execute_command_returning(query, list(item_data.values()))

        if item_id:
            self.link_item_suppliers(item_id[0][0], supplier_ids)
            return item_id[0][0]
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """Link item to multiple suppliers in the ItemSupplier table."""
        if not supplier_ids:
            return
        
        values = ", ".join(["(%s, %s)"] * len(supplier_ids))
        params = []
        for supplier_id in supplier_ids:
            params.extend([item_id, supplier_id])

        query = f"""
        INSERT INTO itemsupplier (itemid, supplierid) 
        VALUES {values} 
        ON CONFLICT DO NOTHING
        """
        
        self.execute_command(query, params)
