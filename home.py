import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def home():
    """Home page displaying an inventory overview."""
    st.title("🏠 Inventory Home Page")
    st.subheader("📊 Inventory Overview")

    # ✅ Fetch inventory with item details
    query = """
    SELECT i.ItemNameEnglish, i.ClassCat, i.DepartmentCat, i.SectionCat, 
           i.FamilyCat, i.SubFamilyCat, inv.Quantity, inv.ExpirationDate, inv.StorageLocation 
    FROM Inventory inv
    JOIN Item i ON inv.ItemID = i.ItemID
    """
    df = db.fetch_data(query)

    if not df.empty:
        st.metric(label="Total Inventory Items", value=len(df))

        # ✅ Ensure Quantity is interpreted as an integer in Pandas
        if "Quantity" in df.columns:
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").astype("Int64")  # Ensures it's an integer

        # ✅ Sum only valid numeric quantities
        total_quantity = df["Quantity"].sum() if df["Quantity"].notna().any() else 0

        st.metric(label="Total Stock Quantity", value=total_quantity)

        st.subheader("⚠️ Items Near Reorder")
        low_stock_items = df[df["Quantity"] <= 10] if "Quantity" in df.columns else pd.DataFrame()

        if not low_stock_items.empty:
            st.dataframe(low_stock_items)
        else:
            st.success("All stock levels are sufficient.")
        
        # ✅ Show the full inventory with item names and categories
        st.subheader("📋 Full Inventory Data")
        st.dataframe(df)
    else:
        st.info("No inventory data available.")
