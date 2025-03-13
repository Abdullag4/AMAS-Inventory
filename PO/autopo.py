import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """Automatically generates purchase orders based on low-stock inventory."""

    st.subheader("📦 Automatic Purchase Order")

    # 1) Fetch items near reorder level
    low_stock_df = get_low_stock_items()

    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    st.write("The following items need restocking:")
    st.dataframe(low_stock_df[["ItemNameEnglish", "CurrentQuantity", "Threshold", "NeededQuantity", "SupplierName"]])

    # 2) Let user pick an expected delivery date
    exp_date = st.date_input("📅 Expected Delivery Date")

    # 3) If user confirms, create POs grouped by supplier
    if st.button("Generate Purchase Orders"):
        create_auto_pos(low_stock_df, exp_date)
        st.success("✅ Automatic Purchase Orders created successfully!")
        st.experimental_rerun()

def get_low_stock_items():
    """
    Retrieves items below threshold with their needed quantity.
    Also fetches one supplier for each item. 
    If an item has multiple suppliers, picks the first found.
    """

    # a) Fetch inventory + item data
    # We'll compute total quantity from Inventory. 
    # Adjust this query to match your actual Inventory table structure.
    query = """
    SELECT 
        i.ItemID, i.ItemNameEnglish, i.Threshold, i.AverageRequired,
        COALESCE(SUM(inv.Quantity), 0) AS CurrentQuantity
    FROM Item i
    LEFT JOIN Inventory inv ON i.ItemID = inv.ItemID
    GROUP BY i.ItemID, i.ItemNameEnglish, i.Threshold, i.AverageRequired
    """
    df = po_handler.fetch_data(query)

    if df.empty:
        return pd.DataFrame()

    # b) Filter items with quantity < threshold
    df["NeededQuantity"] = df["averagerequired"] - df["currentquantity"]
    df = df[df["NeededQuantity"] > 0].copy()
    if df.empty:
        return df  # no low stock

    # c) For each item, get one supplier if available
    #    We'll pick the *first* supplier from ItemSupplier; 
    #    if none found, we skip the item.
    supplier_map = get_first_supplier_for_items()
    df["SupplierID"] = df["itemid"].map(supplier_map.get)
    df = df.dropna(subset=["SupplierID"])  # skip if no supplier found
    df["SupplierID"] = df["SupplierID"].astype(int)

    # d) Convert SupplierID -> SupplierName for display
    supplier_df = po_handler.get_suppliers()
    supplier_lookup = dict(zip(supplier_df["supplierid"], supplier_df["suppliername"]))
    df["SupplierName"] = df["SupplierID"].map(supplier_lookup).fillna("No Supplier")

    return df

def get_first_supplier_for_items():
    """
    Returns a dict: { ItemID: firstSupplierID } to pick a default supplier 
    for each item if multiple exist.
    """
    supplier_df = po_handler.get_item_supplier_mapping()
    # We'll keep the first supplier encountered
    first_supplier_map = {}
    for row in supplier_df.itertuples():
        # row.ItemID, row.SupplierID
        item_id = getattr(row, "itemid")
        sup_id = getattr(row, "supplierid")
        if item_id not in first_supplier_map:
            first_supplier_map[item_id] = sup_id
    return first_supplier_map

def create_auto_pos(low_stock_df, exp_date):
    """
    Groups items by supplier, then creates one PO per supplier with item details.
    Uses 'create_manual_po' from po_handler.
    """
    # Group items by supplier
    grouped = low_stock_df.groupby("SupplierID")

    for supplier_id, group in grouped:
        items_for_supplier = []
        for _, row in group.iterrows():
            items_for_supplier.append({
                "item_id": int(row["itemid"]),
                "quantity": int(row["NeededQuantity"]),
                "estimated_price": None  # or we can guess some price if needed
            })

        po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
