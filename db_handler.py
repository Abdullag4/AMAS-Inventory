import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """Handles all database interactions in a structured and modular way."""

    def __init__(self):
        """Initialize the database connection DSN from Streamlit secrets."""
        self.dsn = st.secrets["neon"]["dsn"]

    def get_connection(self):
        """Create a new PostgreSQL database connection using the DSN."""
        try:
            return psycopg2.connect(self.dsn)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def fetch_data(self, query, params=None):
        """
        Execute a SELECT query and return results as a Pandas DataFrame.
        """
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()

        with conn.cursor() as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        conn.close()

        if rows:
            return pd.DataFrame(rows, columns=columns)
        return pd.DataFrame()

    def execute_command(self, query, params=None):
        """
        Execute an INSERT, UPDATE, or DELETE query with no return.
        """
        conn = self.get_connection()
        if not conn:
            return

        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
        conn.close()

    def execute_command_returning(self, query, params=None):
        """
        Execute an INSERT or UPDATE query that returns a row (e.g. for RETURNING).
        Returns the first row of results as a tuple, or None if no results.
        """
        conn = self.get_connection()
        if not conn:
            return None

        result = None
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            result = cur.fetchone()  # Fetch exactly one row
            conn.commit()
        conn.close()

        return result

    # ─────────────────────────────
    #  SECTION: Dropdowns Management
    # ─────────────────────────────
    def get_all_sections(self):
        """
        Retrieve all unique sections from the 'Dropdowns' table.
        """
        query = "SELECT DISTINCT section FROM Dropdowns"
        df = self.fetch_data(query)
        return df["section"].tolist() if not df.empty else []

    def get_dropdown_values(self, section):
        """
        Retrieve all values for a specific section from 'Dropdowns'.
        """
        query = "SELECT Value FROM Dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        return df["value"].tolist() if not df.empty else []

    def add_dropdown_value(self, section, value):
        """
        Add a new value to a specific section in the 'Dropdowns' table.
        Uses ON CONFLICT to prevent duplicates.
        """
        query = """
        INSERT INTO Dropdowns (Section, Value)
        VALUES (%s, %s)
        ON CONFLICT (Section, Value) DO NOTHING
        """
        self.execute_command(query, (section, value))

    def delete_dropdown_value(self, section, value):
        """
        Delete a value from a specific section in the 'Dropdowns' table.
        """
        query = "DELETE FROM Dropdowns WHERE section = %s AND value = %s"
        self.execute_command(query, (section, value))

    # ─────────────────────────────
    #  SECTION: Supplier Management
    # ─────────────────────────────
    def get_suppliers(self):
        """
        Retrieve all suppliers from the 'Supplier' table.
        Returns columns: SupplierID, SupplierName
        """
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    # ─────────────────────────────
    #  SECTION: Item & Supplier Linking
    # ─────────────────────────────
    def get_items(self):
        """
        Retrieve all items from the 'Item' table for editing or reference.
        """
        query = "SELECT * FROM Item"
        return self.fetch_data(query)

    def get_item_suppliers(self, item_id):
        """
        Retrieve all supplier names linked to a specific item via 'ItemSupplier'.
        """
        query = """
        SELECT s.SupplierName
        FROM ItemSupplier isup
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE isup.ItemID = %s
        """
        df = self.fetch_data(query, (item_id,))
        return df["suppliername"].tolist() if not df.empty else []

    def add_item(self, item_data, supplier_ids):
        """
        Insert a new item into 'Item' and link it to suppliers via 'ItemSupplier'.
        Returns the newly added ItemID, or None if insertion failed.
        """
        columns = ", ".join(item_data.keys())
        placeholders = ", ".join(["%s"] * len(item_data))

        query = f"""
        INSERT INTO Item ({columns}, CreatedAt, UpdatedAt)
        VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID
        """

        new_id = self.execute_command_returning(query, list(item_data.values()))
        if new_id:
            item_id = new_id[0]  # e.g. (30,) -> 30
            self.link_item_suppliers(item_id, supplier_ids)
            return item_id
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """
        Link an item to multiple suppliers in 'ItemSupplier' table.
        """
        for supplier_id in supplier_ids:
            query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(query, (item_id, supplier_id))

    def update_item(self, item_id, updated_data):
        """
        Update item details in the 'Item' table.
        updated_data is a dict {column_name: new_value, ...}.
        """
        if not updated_data:
            st.warning("⚠️ No changes made.")
            return

        set_clause = ", ".join(f"{col} = %s" for col in updated_data.keys())
        values = list(updated_data.values()) + [item_id]

        query = f"""
        UPDATE Item
        SET {set_clause}, UpdatedAt = CURRENT_TIMESTAMP
        WHERE ItemID = %s
        """
        self.execute_command(query, values)

    def update_item_suppliers(self, item_id, supplier_ids):
        """
        Update suppliers linked to an item (remove old, add new).
        """
        delete_query = "DELETE FROM ItemSupplier WHERE ItemID = %s"
        self.execute_command(delete_query, (item_id,))

        for supplier_id in supplier_ids:
            insert_query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(insert_query, (item_id, supplier_id))
