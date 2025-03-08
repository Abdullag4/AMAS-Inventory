import streamlit as st
import pandas as pd
from db_handler import DatabaseManager
from PIL import Image
import io
import base64

db = DatabaseManager()

def convert_image(image_bytes):
    """Convert image bytes to base64 for display in Streamlit data editor."""
    if image_bytes:
        return f'data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}'
    return None

def home():
    st.title("🏠 Inventory Home Page")
    st.subheader("📊 Inventory Overview")

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
            df["itempicture"] = df["itempicture"].apply(convert_image)

            df = df.groupby(["itemid", "expirationdate", "storagelocation"], as_index=False).agg({
                "itemnameenglish": "first",
                "classcat": "first",
                "departmentcat": "first",
                "sectioncat": "first",
                "familycat": "first",
                "subfamilycat": "first",
                "threshold": "first",
                "averagerequired": "first",
                "itempicture": "first",
                "quantity": "sum"
            })

            total_quantity = df["quantity"].sum()
        else:
            st.warning("⚠️ 'quantity' column not found in database. Check table schema.")
            total_quantity = "N/A"

        st.metric(label="Total Stock Quantity", value=total_quantity)

        # Items Near Reorder
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
                "averagerequired": "first",
                "itempicture": "first"
            })

            low_stock_items = grouped_reorder_df[grouped_reorder_df["quantity"] < grouped_reorder_df["threshold"]].copy()

            if not low_stock_items.empty:
                low_stock_items["quantity"].fillna(0, inplace=True)
                low_stock_items["averagerequired"].fillna(0, inplace=True)
                low_stock_items["reorderamount"] = low_stock_items["averagerequired"] - low_stock_items["quantity"]

                st.data_editor(
                    low_stock_items[["itempicture", "itemnameenglish", "quantity", "threshold", "reorderamount"]],
                    column_config={
                        "itempicture": st.column_config.ImageColumn("Item Picture"),
                        "itemnameenglish": "Item Name (English)",
                        "quantity": "Quantity",
                        "threshold": "Threshold",
                        "reorderamount": "Reorder Amount"
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("All stock levels are sufficient.")

        # Full Inventory Data
        st.subheader("📋 Full Inventory Data")
        st.data_editor(
            df,
            column_config={
                "itempicture": st.column_config.ImageColumn("Item Picture"),
                "itemnameenglish": "Item Name (English)",
                "classcat": "Class Category",
                "departmentcat": "Department Category",
                "sectioncat": "Section Category",
                "familycat": "Family Category",
                "subfamilycat": "Sub-Family Category",
                "quantity": "Quantity",
                "threshold": "Threshold",
                "averagerequired": "Average Required",
                "expirationdate": "Expiration Date",
                "storagelocation": "Storage Location"
            },
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
    else:
        st.info("No inventory data available.")
