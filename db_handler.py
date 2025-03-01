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
            return

        columns = ", ".join(item_data.keys())  # Convert dict keys to column names
        values_placeholders = ", ".join(["%s"] * len(item_data))  # Create "%s, %s, %s..."

        query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """

        self.execute_command(query, list(item_data.values()))  # Convert dict values to tuple
        st.success("✅ Item added successfully!")

    def add_inventory(self, inventory_data):
        """Insert received items into the Inventory table or update quantity if same ItemID, ExpirationDate, and StorageLocation exist."""
        
        check_query = """
        SELECT Quantity FROM Inventory 
        WHERE ItemID = %s AND ExpirationDate = %s AND StorageLocation = %s
        """
        existing_row = self.fetch_data(check_query, (
            inventory_data["ItemID"], inventory_data["ExpirationDate"], inventory_data["StorageLocation"]
        ))

        if not existing_row.empty:
            # ✅ Update quantity if row exists
            update_query = """
            UPDATE Inventory
            SET Quantity = Quantity + %s, LastUpdated = CURRENT_TIMESTAMP
            WHERE ItemID = %s AND ExpirationDate = %s AND StorageLocation = %s
            """
            self.execute_command(update_query, (
                inventory_data["Quantity"], inventory_data["ItemID"], 
                inventory_data["ExpirationDate"], inventory_data["StorageLocation"]
            ))
            st.success("✅ Inventory updated: Quantity increased.")
        else:
            # ✅ Insert new record if no matching row
            columns = ", ".join(inventory_data.keys())  
            values_placeholders = ", ".join(["%s"] * len(inventory_data))  

            insert_query = f"""
            INSERT INTO Inventory ({columns}, LastUpdated)
            VALUES ({values_placeholders}, CURRENT_TIMESTAMP)
            """
            
            self.execute_command(insert_query, list(inventory_data.values()))  
            st.success("✅ New item added to inventory.")
