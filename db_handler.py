import streamlit as st
import psycopg2
import pandas as pd

class DatabaseManager:
    """General Database Interactions"""

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
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()
            conn.close()

    def execute_command_returning(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return None
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            result = cur.fetchone()
            conn.commit()
        conn.close()
        return result

    # ─────────── Dropdown Management ───────────
    def get_all_sections(self):
        df = self.fetch_data("SELECT DISTINCT section FROM Dropdowns")
        return df["section"].tolist() if not df.empty else []

    def get_dropdown_values(self, section):
        query = "SELECT value FROM Dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        return df["value"].tolist() if not df.empty else []

    # ───────────── Supplier Management ─────────────
    def get_suppliers(self):
        return self.fetch_data("SELECT SupplierID, SupplierName FROM Supplier")

    # ───────────── Inventory Management ─────────────
    def add_inventory(self, inventory_data):
        columns = ", ".join(inventory_data.keys())
        placeholders = ", ".join(["%s"] * len(inventory_data))

        query = f"""
        INSERT INTO Inventory ({columns})
        VALUES ({placeholders})
        """

        self.execute_command(query, list(inventory_data.values()))
