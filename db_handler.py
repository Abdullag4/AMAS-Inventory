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
        """Retrieve all items from the Item table."""
        query = "SELECT * FROM Item"
        return self.fetch_data(query)

    def get_suppliers(self):
        """Retrieve all suppliers from the Supplier table."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def item_exists(self, item_name):
        """Check if an item already exists based on the name."""
        query = "SELECT ItemID FROM Item WHERE ItemNameEnglish = %s"
        result = self.fetch_data(query, (item_name,))
        return result["itemid"].iloc[0] if not result.empty else None

    def add_item(self, item_data, supplier_ids=None):
        """Insert a new item and link it to suppliers."""
        item_id = self.item_exists(item_data["ItemNameEnglish"])
        if item_id:
            st.warning("⚠️ This item already exists. Linking to new suppliers only.")
        else:
            columns = ", ".join(item_data.keys())
            values_placeholders = ", ".join(["%s"] * len(item_data))
            query = f"""
            INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
            VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING ItemID
            """
            result = self.execute_command_returning(query, list(item_data.values()))
            item_id = result[0][0] if result else None
            st.success("✅ Item added successfully!")

        if item_id and supplier_ids:
            self.link_item_to_suppliers(item_id, supplier_ids)

        return item_id  # ✅ Return ItemID

    def link_item_to_suppliers(self, item_id, supplier_ids):
        """Links an item to multiple suppliers."""
        if not supplier_ids:
            return

        query = """
        INSERT INTO ItemSupplier (ItemID, SupplierID)
        VALUES (%s, %s)
        ON CONFLICT (ItemID, SupplierID) DO NOTHING
        """
        conn = self.get_connection()
        if conn:
            with conn.cursor() as cur:
                for supplier_id in supplier_ids:
                    cur.execute(query, (item_id, supplier_id))
                conn.commit()
            conn.close()
            st.success("✅ Item and supplier(s) linked successfully!")
