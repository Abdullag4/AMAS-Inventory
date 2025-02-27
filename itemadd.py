import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    """Establish connection using DSN stored in Streamlit secrets."""
    try:
        dsn = st.secrets["dsn"]
        return psycopg2.connect(dsn)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_inventory():
    """Retrieve inventory batches from the database."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM InventoryBatch")
            df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        conn.close()
        return df
    return pd.DataFrame()

def add_inventory(item_id, quantity, expiration_date, location):
    """Add new inventory batch to the database."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            query = """
            INSERT INTO InventoryBatch (ItemID, Quantity, ExpirationDate, StorageLocation, DateReceived, LastUpdated)
            VALUES (%s, %s, %s, %s, CURRENT_DATE, CURRENT_TIMESTAMP)"""
            cursor.execute(query, (item_id, quantity, expiration_date, location))
        conn.commit()
        conn.close()
        st.success("New inventory batch added successfully!")

def update_inventory(batch_id, quantity, expiration_date, location):
    """Update existing inventory batch."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            query = """
            UPDATE InventoryBatch
            SET Quantity = %s, ExpirationDate = %s, StorageLocation = %s, LastUpdated = CURRENT_TIMESTAMP
            WHERE BatchID = %s"""
            cursor.execute(query, (quantity, expiration_date, location, batch_id))
        conn.commit()
        conn.close()
        st.success("Inventory batch updated successfully!")

def delete_inventory(batch_id):
    """Delete inventory batch."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM InventoryBatch WHERE BatchID = %s", (batch_id,))
        conn.commit()
        conn.close()
        st.warning("Inventory batch deleted!")
