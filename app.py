import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# Database connection settings
DB_PARAMS = {
    "dbname": "your_db_name",
    "user": "your_db_user",
    "password": "your_db_password",
    "host": "your_neon_host",
    "port": "your_db_port"
}

def get_connection():
    """Establish connection with PostgreSQL database."""
    return psycopg2.connect(**DB_PARAMS)

def fetch_inventory():
    """Retrieve inventory batches from the database."""
    conn = get_connection()
    query = """SELECT * FROM InventoryBatch"""
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def add_inventory(item_id, quantity, expiration_date, location):
    """Add new inventory batch to the database."""
    conn = get_connection()
    cursor = conn.cursor()
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
    cursor = conn.cursor()
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
    cursor = conn.cursor()
    query = "DELETE FROM InventoryBatch WHERE BatchID = %s"
    cursor.execute(query, (batch_id,))
    conn.commit()
    conn.close()
    st.warning("Inventory batch deleted!")

# Streamlit App UI
st.title("📦 Inventory Management App")
menu = st.sidebar.radio("Navigation", ["View Inventory", "Add Inventory", "Update Inventory", "Delete Inventory"])

if menu == "View Inventory":
    st.subheader("📋 Inventory List")
    df = fetch_inventory()
    st.dataframe(df)

elif menu == "Add Inventory":
    st.subheader("➕ Add New Inventory Batch")
    item_id = st.number_input("Item ID", min_value=1, step=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    expiration_date = st.date_input("Expiration Date")
    location = st.text_input("Storage Location")
    if st.button("Add Inventory"):
        add_inventory(item_id, quantity, expiration_date, location)

elif menu == "Update Inventory":
    st.subheader("✏️ Update Inventory Batch")
    batch_id = st.number_input("Batch ID", min_value=1, step=1)
    quantity = st.number_input("New Quantity", min_value=1, step=1)
    expiration_date = st.date_input("New Expiration Date")
    location = st.text_input("New Storage Location")
    if st.button("Update Inventory"):
        update_inventory(batch_id, quantity, expiration_date, location)

elif menu == "Delete Inventory":
    st.subheader("❌ Delete Inventory Batch")
    batch_id = st.number_input("Batch ID to Delete", min_value=1, step=1)
    if st.button("Delete Inventory"):
        delete_inventory(batch_id)
