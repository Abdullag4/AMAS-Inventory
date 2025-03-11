import streamlit as st
import pandas as pd
from receive_items.receive_handler import ReceiveHandler

receive_handler = ReceiveHandler()

def receive_items():
    """Page for manually receiving items into inventory."""
    st.header("➕ Manually Add Items to Inventory")

    items_df = receive_handler.fetch_data("SELECT ItemID, ItemNameEnglish FROM Item")

    if items_df.empty:
        st.warning("⚠️ No items available. Please add items first.")
        return

    item_options = dict(zip(items_df["itemnameenglish"], items_df["itemid"]))
    selected_item_name = st.selectbox("Select Item", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    quantity = st.number_input("Quantity Received", min_value=1, step=1)
    expiration_date = st.date_input("Expiration Date")
    storage_location = st.text_input("Storage Location")
    date_received = st.date_input("Date Received")

    if st.button("Receive Item"):
        inventory_data = [{
            "item_id": selected_item_id,
            "quantity": quantity,
            "expiration_date": expiration_date,
            "storage_location": storage_location
        }]
        receive_handler.add_items_to_inventory(inventory_data)
        st.success(f"✅ {selected_item_name} added to inventory!")
