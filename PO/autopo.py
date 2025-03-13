import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """Automatically generates purchase orders based on low-stock inventory."""
    st.subheader("📦 Automatic Purchase Order")

    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    st.write("The following items need restocking:")
    st.dataframe(low_stock_df[["itemnameenglish", "currentquantity", "threshold", "neededquantity", "suppliername"]])

    # Let user pick an expected delivery date for the generated POs
    exp_date = st.date_input("📅 Expected Delivery Date")

    # If user confirms, create POs grouped by supplier
    if st.button("Generate Purchase Orders"):
        create_auto_pos(low_stock_df, exp_date)
        st.success("✅ Automatic Purchase Orders created successfully!")
        st.stop()  # ✅ End execution to prevent further code from running, effectively refreshing the page

def get_low_stock_items():
    """
    Retrieves items below threshold with needed quantity = averagerequired - currentquantity.
    Grabs 1 default supplier for each item if possible.
    Returns a DataFrame with columns:
      - itemid
      - itemnameenglish
      - threshold
      - averagerequired
      - currentquantity
      - neededquantity
      - supplierid
      - suppliername
    """
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

    df["neededquantity"] = df["averagerequired"] - df["currentquantity"]
    df = df[df["neededquantity"] > 0].copy()
    if df.empty:
        return df  # no low-stock items

    # Attach a default supplier if available
    supplier_map = get_first_supplier_for_items()  # { itemid: firstSupplierID }
    df["supplierid"] = df["itemid"].map(supplier_map)
    df.dropna(subset=["supplierid"], inplace=True)
    df["supplierid"] = df["supplierid"].astype(int)

    # Convert SupplierID -> SupplierName
    supplier_df = po_handler.get_suppliers()
    supplier_lookup = dict(zip(supplier_df["supplierid"], supplier_df["suppliername"]))
    df["suppliername"] = df["supplierid"].map(supplier_lookup).fillna("No Supplier")

    return df

def get_first_supplier_for_items():
    """
    Returns { itemid: firstSupplierID } picking the first supplier from ItemSupplier if multiple.
    """
    supplier_df = po_handler.get_item_supplier_mapping()
    first_supplier_map = {}
    if not supplier_df.empty:
        for row in supplier_df.itertuples():
            item_id = getattr(row, "itemid")
            sup_id = getattr(row, "supplierid")
            if item_id not in first_supplier_map:
                first_supplier_map[item_id] = sup_id
    return first_supplier_map

def create_auto_pos(low_stock_df, exp_date):
    """
    Groups items by 'supplierid', then creates one PO per supplier with item details.
    Uses create_manual_po(supplier_id, exp_date, items_for_supplier).
    """
    grouped = low_stock_df.groupby("supplierid")

    for supplier_id, group in grouped:
        items_for_supplier = []
        for _, row in group.iterrows():
            items_for_supplier.append({
                "item_id": int(row["itemid"]),
                "quantity": int(row["neededquantity"]),
                "estimated_price": None
            })
        po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
