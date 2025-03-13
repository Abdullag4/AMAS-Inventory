import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """Automatically generates purchase orders based on low-stock inventory, strictly if currentquantity < threshold."""
    st.subheader("📦 Automatic Purchase Order by Supplier")

    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    st.write("Below are items grouped by supplier. Generate POs as needed.")
    grouped = low_stock_df.groupby("supplierid")

    for supplier_id, group in grouped:
        supplier_name = group.iloc[0]["suppliername"]
        with st.expander(f"📦 Supplier: {supplier_name}"):
            st.write("**Items needing reorder from this supplier:**")
            st.dataframe(
                group[["itemnameenglish", "currentquantity", "threshold", "neededquantity"]],
                use_container_width=True
            )

            exp_date = st.date_input(
                f"📅 Expected Delivery Date for {supplier_name}",
                key=f"exp_date_{supplier_id}"
            )

            if st.button(f"Accept & Send Order to {supplier_name}", key=f"send_{supplier_id}"):
                items_for_supplier = []
                for _, row in group.iterrows():
                    items_for_supplier.append({
                        "item_id": int(row["itemid"]),
                        "quantity": int(row["neededquantity"]),
                        "estimated_price": None
                    })
                po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
                st.success(f"✅ Purchase Order created for {supplier_name} successfully!")
                st.stop()

def get_low_stock_items():
    """
    1) Only reorder items if currentquantity < threshold.
    2) neededquantity = averagerequired - currentquantity.
    3) Must have an available supplier.
    """
    # 1) Load item + aggregated inventory
    query = """
    SELECT 
        i.ItemID AS itemid,
        i.ItemNameEnglish AS itemnameenglish,
        i.Threshold AS threshold,
        i.AverageRequired AS averagerequired,
        COALESCE(SUM(inv.Quantity), 0) AS currentquantity
    FROM Item i
    LEFT JOIN Inventory inv ON i.ItemID = inv.ItemID
    GROUP BY i.ItemID, i.ItemNameEnglish, i.Threshold, i.AverageRequired
    """
    df = po_handler.fetch_data(query)
    if df.empty:
        return pd.DataFrame()

    # 2) Keep only items with currentquantity < threshold
    df = df[df["currentquantity"] < df["threshold"]].copy()
    if df.empty:
        return df

    # 3) Calculate neededquantity
    df["neededquantity"] = df["averagerequired"] - df["currentquantity"]
    # If, by chance, neededquantity ends up negative or zero, skip
    df = df[df["neededquantity"] > 0].copy()
    if df.empty:
        return df

    # 4) Attach 1 default supplier if available
    supplier_map = get_first_supplier_for_items()
    df["supplierid"] = df["itemid"].map(supplier_map)
    df.dropna(subset=["supplierid"], inplace=True)
    df["supplierid"] = df["supplierid"].astype(int)

    # 5) Convert SupplierID -> SupplierName
    sup_df = po_handler.get_suppliers()
    sup_lookup = dict(zip(sup_df["supplierid"], sup_df["suppliername"]))
    df["suppliername"] = df["supplierid"].map(sup_lookup).fillna("No Supplier")

    return df

def get_first_supplier_for_items():
    """Find the first supplier for each item from the ItemSupplier table."""
    mapping_df = po_handler.get_item_supplier_mapping()
    first_map = {}
    if not mapping_df.empty:
        for row in mapping_df.itertuples():
            item_id = getattr(row, "itemid")
            sup_id = getattr(row, "supplierid")
            if item_id not in first_map:
                first_map[item_id] = sup_id
    return first_map
