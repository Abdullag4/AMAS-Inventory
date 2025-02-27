import streamlit as st
import pandas as pd
from neon_handler import get_connection, fetch_inventory, add_inventory, update_inventory, delete_inventory

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
