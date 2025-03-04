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

    def get_items(self):
        """Retrieve all items from the Item table."""
        query = "SELECT * FROM Item"
        return self.fetch_data(query)

    def get_suppliers(self):
        """Retrieve all suppliers from the Supplier table."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
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

    def add_item(self, item_data, supplier_ids):
        """Insert a new item dynamically based on the provided dictionary keys and link it to suppliers."""
        if self.item_exists(item_data):
            st.warning("⚠️ This item already exists and cannot be added again.")
            return

        columns = ", ".join(item_data.keys())  # Convert dict keys to column names
        values_placeholders = ", ".join(["%s"] * len(item_data))  # Create "%s, %s, %s..."

        query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID
        """

        item_id = self.execute_command_returning(query, list(item_data.values()))  # Get new item ID
        if item_id:
            item_id = item_id[0][0]  # Extract the actual ItemID
            self.link_item_to_suppliers(item_id, supplier_ids)
            st.success("✅ Item added successfully!")

    def link_item_to_suppliers(self, item_id, supplier_ids):
        """Links an item to multiple suppliers in the ItemSupplier table."""
        if not supplier_ids:
            st.warning("⚠️ No suppliers selected. Skipping linking process.")
            return

        try:
            conn = self.get_connection()
            if conn:
                with conn.cursor() as cur:
                    query = """
                    INSERT INTO ItemSupplier (ItemID, SupplierID) 
                    VALUES (%s, %s)
                    ON CONFLICT (ItemID, SupplierID) DO NOTHING
                    """  # ✅ Prevent duplicate entries

                    # ✅ Insert each supplier link
                    for supplier_id in supplier_ids:
                        cur.execute(query, (item_id, supplier_id))

                    conn.commit()
                    st.success("✅ Item and supplier(s) linked successfully!")
        except Exception as e:
            st.error(f"❌ Failed to link item to suppliers: {e}")

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

    def get_item_suppliers(self, item_id):
        """Retrieve suppliers linked to a specific item."""
        query = """
        SELECT s.SupplierID, s.SupplierName 
        FROM Supplier s
        JOIN ItemSupplier isup ON s.SupplierID = isup.SupplierID
        WHERE isup.ItemID = %s
        """
        return self.fetch_data(query, (item_id,))
