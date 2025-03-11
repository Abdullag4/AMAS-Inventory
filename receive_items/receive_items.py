import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def receive_items():
    """Page for receiving items into the inventory."""
    st.title("📦 Receive Items into Inventory")

    # Fetch existing items from the Item table
    items_df = db.fetch_data("SELECT ItemID, ItemNameEnglish FROM Item")

    # ✅ Ensure the DataFrame has proper column names
    if not items_df.empty:
        items_df.columns = ["ItemID", "ItemNameEnglish"]  # ✅ Force correct column names
    else:
        st.warning("⚠️ No items available. Please add items first.")
        return

    # Select an item from dropdown
    item_options = dict(zip(items_df["ItemNameEnglish"], items_df["ItemID"]))
    selected_item_name = st.selectbox("Select an Item", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    # Input fields for inventory data
    quantity = st.number_input("Quantity Received", min_value=1, step=1)
    expiration_date = st.date_input("Expiration Date")
    storage_location = st.text_input("Storage Location")
    date_received = st.date_input("Date Received")

    if st.button("Receive Item"):
        inventory_data = {
            "ItemID": selected_item_id,
            "Quantity": quantity,
            "ExpirationDate": expiration_date,
            "StorageLocation": storage_location,
            "DateReceived": date_received
        }
        db.add_inventory(inventory_data)
        st.success(f"✅ {selected_item_name} added to inventory!")
