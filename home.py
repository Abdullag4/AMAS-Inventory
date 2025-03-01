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

        # ✅ Check available column names
        st.write("🔍 Columns in Inventory Data:", df.columns.tolist())

        # ✅ Check if "QuantityInStock" exists, otherwise use "Quantity"
        if "QuantityInStock" in df.columns:
            total_quantity = df["QuantityInStock"].sum()
        elif "Quantity" in df.columns:
            total_quantity = df["Quantity"].sum()
        else:
            total_quantity = 0  # Fallback to avoid errors

        st.metric(label="Total Stock Quantity", value=total_quantity)

        st.subheader("⚠️ Items Near Reorder")
        if "QuantityInStock" in df.columns and "ReorderThreshold" in df.columns:
            low_stock_items = df[df["QuantityInStock"] <= df["ReorderThreshold"]]
        elif "Quantity" in df.columns and "ReorderThreshold" in df.columns:
            low_stock_items = df[df["Quantity"] <= df["ReorderThreshold"]]
        else:
            low_stock_items = pd.DataFrame()  # Empty DataFrame if missing columns

        if not low_stock_items.empty:
            st.dataframe(low_stock_items)
        else:
            st.success("All stock levels are sufficient.")
    else:
        st.info("No inventory data available.")
