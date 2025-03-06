import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """Handles all database interactions."""

    def __init__(self):
        """Initialize database connection from Streamlit secrets."""
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
        """Execute an INSERT or UPDATE query and return a single row (e.g. for RETURNING)."""
        conn = self.get_connection()
        result = None
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()  # fetchone() because we expect 1 row for RETURNING
                conn.commit()
            conn.close()
        return result

    # ============= DROPDOWNS TABLE METHODS =============
    def get_dropdown_values(self, section):
        """Retrieve all values for a specific section from the Dropdowns table."""
        query = "SELECT value FROM Dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        return df["value"].tolist() if not df.empty else []

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
        query = "DELETE FROM Dropdowns WHERE section = %s AND value = %s"
        self.execute_command(query, (section, value))

    def get_all_sections(self):
        """Retrieve all unique sections from the Dropdowns table."""
        query = "SELECT DISTINCT section FROM Dropdowns"
        df = self.fetch_data(query)
        return df["section"].tolist() if not df.empty else []

    # ============= SUPPLIERS METHODS =============
    def get_suppliers(self):
        """Retrieve all suppliers from the Supplier table."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    # ============= ITEMS & SUPPLIER LINKING =============
    def get_items(self):
        """Retrieve all items for editing or reference."""
        query = "SELECT * FROM Item"
        return self.fetch_data(query)

    def get_item_suppliers(self, item_id):
        """Retrieve supplier names linked to a specific item."""
        query = """
        SELECT s.SupplierName 
        FROM ItemSupplier isup
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE isup.ItemID = %s
        """
        df = self.fetch_data(query, (item_id,))
        return df["suppliername"].tolist() if not df.empty else []

    def add_item(self, item_data, supplier_ids):
        """Insert a new item and link it to suppliers."""
        columns = ", ".join(item_data.keys())
        values_placeholders = ", ".join(["%s"] * len(item_data))

        query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID
        """
        
        # Use execute_command_returning for the newly inserted ID
        new_id = self.execute_command_returning(query, list(item_data.values()))
        if new_id:  # e.g., new_id = (30,) from fetchone()
            item_id = new_id[0]  # e.g., 30
            self.link_item_suppliers(item_id, supplier_ids)
            return item_id
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """Link an item to multiple suppliers in the ItemSupplier table."""
        for supplier_id in supplier_ids:
            query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(query, (item_id, supplier_id))

    def update_item(self, item_id, updated_data):
        """Update item details."""
        columns = ", ".join(f"{col} = %s" for col in updated_data.keys())
        values = list(updated_data.values()) + [item_id]

        query = f"UPDATE Item SET {columns}, UpdatedAt = CURRENT_TIMESTAMP WHERE ItemID = %s"
        self.execute_command(query, values)

    def update_item_suppliers(self, item_id, supplier_ids):
        """Update suppliers linked to an item (Remove old, then add new)."""
        delete_query = "DELETE FROM ItemSupplier WHERE ItemID = %s"
        self.execute_command(delete_query, (item_id,))

        for supplier_id in supplier_ids:
            insert_query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(insert_query, (item_id, supplier_id))
