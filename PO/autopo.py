import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """
    Automatically generates purchase orders based on low-stock inventory,
    showing items in a single table with a 'Picture' column.
    """
    st.subheader("📦 Automatic Purchase Order")

    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    # Replace the raw binary with a simple icon or text for st.dataframe
    low_stock_df["picture"] = low_stock_df["itempicture"].apply(
        lambda img: "🖼️" if img else "No Image"
    )

    # Show the single table
    st.write("The following items need restocking:")
    st.dataframe(
        low_stock_df[["picture", "itemnameenglish", "currentquantity", "threshold", "neededquantity", "suppliername"]],
        use_container_width=True
    )

    # Let user pick an expected delivery date
    exp_date = st.date_input("📅 Expected Delivery Date")

    if st.button("Generate Purchase Orders"):
        create_auto_pos(low_stock_df, exp_date)
        st.success("✅ Automatic Purchase Orders created successfully!")
        st.stop()

def get_low_stock_items():
    """
    Retrieves items below threshold with needed quantity = AverageRequired - CurrentQuantity.
    If an item has no supplier, it won't appear.
    Returns a DataFrame with columns:
      itemid, itemnameenglish, itempicture, currentquantity, threshold,
      neededquantity, supplierid, suppliername
    """
    query = """
    SELECT 
        i.ItemID AS itemid,
        i.ItemNameEnglish AS itemnameenglish,
        i.ItemPicture AS itempicture,
        i.Threshold AS threshold,
        i.AverageRequired AS averagerequired,
        COALESCE(SUM(inv.Quantity), 0) AS currentquantity
    FROM Item i
    LEFT JOIN Inventory inv ON i.ItemID = inv.ItemID
    GROUP BY i.ItemID, i.ItemNameEnglish, i.ItemPicture, i.Threshold, i.AverageRequired
    """
    df = po_handler.fetch_data(query)

    if df.empty:
        return pd.DataFrame()

    # Calculate needed quantity
    df["neededquantity"] = df["averagerequired"] - df["currentquantity"]
    df = df[df["neededquantity"] > 0].copy()
    if df.empty:
        return df

    # Attach a default supplier if available
    supplier_map = get_first_supplier_for_items()
    df["supplierid"] = df["itemid"].map(supplier_map)
    df.dropna(subset=["supplierid"], inplace=True)
    df["supplierid"] = df["supplierid"].astype(int)

    # Convert SupplierID -> SupplierName
    sup_df = po_handler.get_suppliers()
    sup_lookup = dict(zip(sup_df["supplierid"], sup_df["suppliername"]))
    df["suppliername"] = df["supplierid"].map(sup_lookup).fillna("No Supplier")

    return df

def get_first_supplier_for_items():
    """
    Returns { itemid: firstSupplierID } picking the first supplier from ItemSupplier if multiple.
    """
    mapping_df = po_handler.get_item_supplier_mapping()
    first_map = {}
    if not mapping_df.empty:
        for row in mapping_df.itertuples():
            item_id = getattr(row, "itemid")
            sup_id = getattr(row, "supplierid")
            if item_id not in first_map:
                first_map[item_id] = sup_id
    return first_map

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
