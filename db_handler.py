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

    def get_items(self):
        """Retrieve all items."""
        query = "SELECT * FROM Item"
        return self.fetch_data(query)

    def get_suppliers(self):
        """Retrieve all suppliers."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def get_item_suppliers(self, item_id):
        """Retrieve supplier names linked to a specific item."""
        query = """
        SELECT s.SupplierName FROM ItemSupplier isup
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE isup.ItemID = %s
        """
        result = self.fetch_data(query, (item_id,))
        return result["suppliername"].tolist() if not result.empty else []

    def add_item(self, item_data, supplier_ids):
        """Insert a new item and link it to suppliers."""
        columns = ", ".join(item_data.keys())
        values_placeholders = ", ".join(["%s"] * len(item_data))
        
        query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID
        """

        item_id = self.fetch_data(query, list(item_data.values()))

        if not item_id.empty:
            item_id_int = int(item_id.iloc[0, 0])  # ✅ Convert numpy.int64 → Python int**
            self.link_item_suppliers(item_id_int, supplier_ids)
            return item_id_int
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """Link an item to multiple suppliers in the ItemSupplier table."""
        for supplier_id in supplier_ids:
            query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(query, (item_id, int(supplier_id)))  # ✅ Convert supplier_id to int

    def update_item(self, item_id, updated_data):
        """Update item details."""
        columns = ", ".join(f"{col} = %s" for col in updated_data.keys())
        values = list(updated_data.values()) + [item_id]

        query = f"UPDATE Item SET {columns}, UpdatedAt = CURRENT_TIMESTAMP WHERE ItemID = %s"
        self.execute_command(query, values)

    def update_item_suppliers(self, item_id, supplier_ids):
        """Update suppliers linked to an item (Remove old, add new)."""
        delete_query = "DELETE FROM ItemSupplier WHERE ItemID = %s"
        self.execute_command(delete_query, (item_id,))

        for supplier_id in supplier_ids:
            insert_query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(insert_query, (item_id, int(supplier_id)))  # ✅ Convert supplier_id to int
