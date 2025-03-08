import streamlit as st
import pandas as pd
import base64
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Single DB instance

# Helper function to display images as HTML
def image_to_html(img_bytes):
    if img_bytes:
        encoded = base64.b64encode(img_bytes).decode()
        return f'<img src="data:image/jpeg;base64,{encoded}" width="60" height="60">'
    return 'No image'

def home():
    """Home page displaying an inventory overview with item pictures."""
    st.title("🏠 Inventory Home Page")
    st.subheader("📊 Inventory Overview")

    # ✅ Fetch inventory with item details, including ItemPicture
    query = """
    SELECT i.ItemID, i.ItemNameEnglish, i.ClassCat, i.DepartmentCat, i.SectionCat, 
           i.FamilyCat, i.SubFamilyCat, i.ItemPicture, inv.Quantity, inv.ExpirationDate, 
           inv.StorageLocation, i.Threshold, i.AverageRequired 
    FROM Inventory inv
    JOIN Item i ON inv.ItemID = i.ItemID
    """
    df = db.fetch_data(query)

    if not df.empty:
        st.metric(label="Total Inventory Items", value=len(df))

        df.columns = df.columns.str.lower()

        if "quantity" in df.columns:
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")

            df = df.groupby(["itemid", "expirationdate", "storagelocation"], as_index=False).agg({
                "itemnameenglish": "first",
                "classcat": "first",
                "departmentcat": "first",
                "sectioncat": "first",
                "familycat": "first",
                "subfamilycat": "first",
                "threshold": "first",
                "averagerequired": "first",
                "quantity": "sum",
                "itempicture": "first"
            })

            total_quantity = df["quantity"].sum()
        else:
            st.warning("⚠️ 'quantity' column not found in database. Check table schema.")
            total_quantity = "N/A"

        st.metric(label="Total Stock Quantity", value=total_quantity)

        st.subheader("⚠️ Items Near Reorder")
        required_columns = {"itemid", "quantity", "threshold", "averagerequired"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            st.warning(f"⚠️ Missing columns in database: {missing_columns}")
        else:
            grouped_reorder_df = df.groupby("itemid", as_index=False).agg({
                "itemnameenglish": "first",
                "quantity": "sum",
                "threshold": "first",
                "averagerequired": "first"
            })

            low_stock_items = grouped_reorder_df[grouped_reorder_df["quantity"] < grouped_reorder_df["threshold"]].copy()

            if not low_stock_items.empty:
                low_stock_items["reorderamount"] = low_stock_items["averagerequired"] - low_stock_items["quantity"]
                st.dataframe(low_stock_items[["itemnameenglish", "quantity", "threshold", "reorderamount"]])
            else:
                st.success("All stock levels are sufficient.")

        st.subheader("📋 Full Inventory Data")

        # ✅ Display item pictures
        df["item picture"] = df["itempicture"].apply(image_to_html)
        df.drop(columns=["itempicture"], inplace=True)

        st.write(
            df.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

    else:
        st.info("No inventory data available.")
