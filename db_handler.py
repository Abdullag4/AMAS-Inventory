import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """Handles all database interactions in a concise way."""

    def __init__(self):
        self.dsn = st.secrets["neon"]["dsn"]

    def get_connection(self):
        try:
            return psycopg2.connect(self.dsn)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def fetch_data(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return pd.DataFrame()

        with conn.cursor() as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        conn.close()

        return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame()

    def execute_command(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
        conn.close()

    ########################
    # Dropdown Management
    ########################
    def get_all_sections(self):
        df = self.fetch_data("SELECT DISTINCT section FROM Dropdowns")
        return df["section"].tolist() if not df.empty else []

    def get_dropdown_values(self, section):
        query = "SELECT value FROM Dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        return df["value"].tolist() if not df.empty else []

    def add_dropdown_value(self, section, value):
        query = """
        INSERT INTO Dropdowns (section, value)
        VALUES (%s, %s)
        ON CONFLICT (section, value) DO NOTHING
        """
        self.execute_command(query, (section, value))

    def delete_dropdown_value(self, section, value):
        query = "DELETE FROM Dropdowns WHERE section = %s AND value = %s"
        self.execute_command(query, (section, value))

    ########################
    # Supplier Management
    ########################
    def get_suppliers(self):
        """
        Retrieve suppliers from the 'Supplier' table and rename
        columns to exactly "supplierid" and "suppliername".
        """
        df = self.fetch_data("SELECT supplierid, suppliername FROM Supplier")

        # Important: rename to ensure code can reference them as .loc[:, "suppliername"]
        if not df.empty:
            df.columns = ["supplierid", "suppliername"]
        return df

    ########################
    # Items & Linking
    ########################
    def get_items(self):
        return self.fetch_data("SELECT * FROM Item")

    def get_item_suppliers(self, item_id):
        query = """
        SELECT s.SupplierName
        FROM ItemSupplier isup
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE isup.ItemID = %s
        """
        df = self.fetch_data(query, (item_id,))
        if not df.empty:
            df.columns = df.columns.str.lower()  # => ["suppliername"]
            return df["suppliername"].tolist()
        return []

    def add_item(self, item_data, supplier_ids):
        cols = ", ".join(item_data.keys())
        placeholders = ", ".join(["%s"] * len(item_data))
        query = f"""
        INSERT INTO Item ({cols}, CreatedAt, UpdatedAt)
        VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING ItemID
        """

        conn = self.get_connection()
        if not conn:
            return None

        new_id = None
        with conn.cursor() as cur:
            cur.execute(query, list(item_data.values()))
            row = cur.fetchone()  # e.g. (31,)
            conn.commit()
            if row:
                new_id = row[0]
        conn.close()

        if new_id:
            self.link_item_suppliers(new_id, supplier_ids)
            return new_id
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        for sid in supplier_ids:
            query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(query, (item_id, sid))

    def update_item(self, item_id, updated_data):
        if not updated_data:
            st.warning("No changes made.")
            return

        set_clause = ", ".join(f"{col} = %s" for col in updated_data.keys())
        vals = list(updated_data.values()) + [item_id]
        query = f"UPDATE Item SET {set_clause}, UpdatedAt = CURRENT_TIMESTAMP WHERE ItemID = %s"
        self.execute_command(query, vals)

    def update_item_suppliers(self, item_id, supplier_ids):
        self.execute_command("DELETE FROM ItemSupplier WHERE ItemID = %s", (item_id,))
        for sid in supplier_ids:
            self.execute_command(
                "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)",
                (item_id, sid)
            )
