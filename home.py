import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def home():
    """Home page displaying an inventory overview."""
    st.title("🏠 Inventory Home Page")
    st.subheader("📊 Inventory Overview")

    df = db.get_inventory()

    if not df.empty:
        st.metric(label="Total Inventory Items", value=len(df))
        total_quantity = df["QuantityInStock"].sum()
        st.metric(label="Total Stock Quantity", value=total_quantity)

        st.subheader("⚠️ Items Near Reorder")
        low_stock_items = df[df["QuantityInStock"] <= df["ReorderThreshold"]]
        if not low_stock_items.empty:
            st.dataframe(low_stock_items)
        else:
            st.success("All stock levels are sufficient.")
    else:
        st.info("No inventory data available.")
