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
    SELECT i.ItemID, i.ItemNameEnglish, i.ClassCat, i.DepartmentCat, i.SectionCat, 
           i.FamilyCat, i.SubFamilyCat, inv.Quantity, inv.ExpirationDate, 
           inv.StorageLocation, i.Threshold, i.AverageRequired 
    FROM Inventory inv
    JOIN Item i ON inv.ItemID = i.ItemID
    """
    df = db.fetch_data(query)

    if not df.empty:
        st.metric(label="Total Inventory Items", value=len(df))

        # ✅ Normalize column names to lowercase
        df.columns = df.columns.str.lower()

        # ✅ Ensure "quantity" column exists before summing
        if "quantity" in df.columns:
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")  # Convert to integer

            # ✅ Group inventory by ItemID, ExpirationDate, StorageLocation
            df = df.groupby(["itemid", "expirationdate", "storagelocation"], as_index=False).agg({
                "itemnameenglish": "first",  # Keep item name
                "classcat": "first",
                "departmentcat": "first",
                "sectioncat": "first",
                "familycat": "first",
                "subfamilycat": "first",
                "threshold": "first",
                "averagerequired": "first",
                "quantity": "sum"  # Sum quantity for merged rows
            })

            total_quantity = df["quantity"].sum()
        else:
            st.warning("⚠️ 'quantity' column not found in database. Check table schema.")
            total_quantity = "N/A"

        st.metric(label="Total Stock Quantity", value=total_quantity)

        # ✅ Items Near Reorder (Summed per ItemID)
        st.subheader("⚠️ Items Near Reorder")
        required_columns = {"itemid", "quantity", "threshold", "averagerequired"}

        # ✅ Ensure all required columns exist before processing reorder logic
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            st.warning(f"⚠️ Missing columns in database: {missing_columns}")
        else:
            # ✅ Sum total quantity per ItemID
            grouped_reorder_df = df.groupby("itemid", as_index=False).agg({
                "itemnameenglish": "first",  
                "quantity": "sum",  
                "threshold": "first",
                "averagerequired": "first"
            })

            low_stock_items = grouped_reorder_df[grouped_reorder_df["quantity"] < grouped_reorder_df["threshold"]].copy()

            if not low_stock_items.empty:
                # ✅ Fill NaN values to avoid errors
                low_stock_items["quantity"].fillna(0, inplace=True)
                low_stock_items["averagerequired"].fillna(0, inplace=True)

                # ✅ Create reorder amount column safely
                low_stock_items["reorderamount"] = low_stock_items["averagerequired"] - low_stock_items["quantity"]

                st.dataframe(low_stock_items[["itemnameenglish", "quantity", "threshold", "reorderamount"]])
            else:
                st.success("All stock levels are sufficient.")

        # ✅ Show full inventory with merged rows
        st.subheader("📋 Full Inventory Data")
        st.dataframe(df)
    else:
        st.info("No inventory data available.")
