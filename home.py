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

        # ✅ Debugging: Show available column names
        st.write("🔍 Columns in Inventory Data:", df.columns.tolist())

        # ✅ Normalize column names to lowercase
        df.columns = df.columns.str.lower()  # Convert all column names to lowercase

        # ✅ Use lowercase column name for checking
        if "quantity" in df.columns:
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")  # Convert to integer
            total_quantity = df["quantity"].sum()
        else:
            st.warning("⚠️ 'quantity' column not found in database. Check table schema.")
            total_quantity = "N/A"

        st.metric(label="Total Stock Quantity", value=total_quantity)

        st.subheader("⚠️ Items Near Reorder")
        if "quantity" in df.columns:
            low_stock_items = df[df["quantity"] <= 10]  # Example threshold for low stock
        else:
            low_stock_items = pd.DataFrame()  # Empty DataFrame if missing columns

        if not low_stock_items.empty:
            st.dataframe(low_stock_items)
        else:
            st.success("All stock levels are sufficient.")
        
        # ✅ Show the full inventory with item names and categories
        st.subheader("📋 Full Inventory Data")
        st.dataframe(df)
    else:
        st.info("No inventory data available.")
