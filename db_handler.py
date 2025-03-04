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

    def get_inventory(self):
        """Retrieve all inventory records and ensure Quantity is included."""
        query = """
        SELECT i.ItemNameEnglish, i.ClassCat, i.DepartmentCat, i.SectionCat, 
               i.FamilyCat, i.SubFamilyCat, inv.Quantity, inv.ExpirationDate, 
               inv.StorageLocation, i.Threshold, i.AverageRequired 
        FROM Inventory inv
        JOIN Item i ON inv.ItemID = i.ItemID
        """
        return self.fetch_data(query)

    def item_exists(self, item_data):
        """Check if an item already exists based on unique fields."""
        query = """
        SELECT 1 FROM Item 
        WHERE ItemNameEnglish = %s AND ClassCat = %s 
        AND Manufacturer = %s AND Brand = %s AND Barcode = %s
        """
        result = self.fetch_data(query, (
            item_data["ItemNameEnglish"], item_data["ClassCat"],
            item_data["Manufacturer"], item_data["Brand"], item_data["Barcode"]
        ))
        return not result.empty

    def add_item(self, item_data):
        """Insert a new item dynamically based on the provided dictionary keys."""
        if self.item_exists(item_data):
            st.warning("⚠️ This item already exists and cannot be added again.")
            return None  # Return None if the item already exists

        columns = ", ".join(item_data.keys())  # Convert dict keys to column names
        values_placeholders = ", ".join(["%s"] * len(item_data))  # Create "%s, %s, %s..."

        query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID  -- ✅ Ensure we get the newly created ItemID
        """

        result = self.execute_command_returning(query, list(item_data.values()))  
        return result[0][0] if result else None  # ✅ Return new ItemID

    def add_item_supplier(self, item_id, supplier_id):
        """Link an item to a supplier in the ItemSupplier table."""
        query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
        self.execute_command(query, (item_id, supplier_id))
