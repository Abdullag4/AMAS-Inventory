import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """Automatically generates purchase orders based on low-stock inventory, grouped by supplier."""
    st.subheader("📦 Automatic Purchase Order – Per Supplier")

    # 1) Fetch items near reorder level
    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    # 2) Group low-stock items by supplier
    grouped_suppliers = low_stock_df.groupby("supplierid")

    # 3) For each supplier, show a table and a button to confirm
    for supplier_id, group_df in grouped_suppliers:
        supplier_name = group_df.iloc[0]["suppliername"]
        st.write("---")
        st.write(f"### Supplier: **{supplier_name}** (ID: {supplier_id})")

        # Show a small table of needed items for that supplier
        st.dataframe(
            group_df[["itemnameenglish", "currentquantity", "threshold", "neededquantity"]],
            use_container_width=True
        )

        # Let user set an expected delivery date for this supplier's items
        exp_date = st.date_input(
            f"📅 Expected Delivery Date (Supplier: {supplier_name})",
            key=f"date_{supplier_id}"
        )

        # When user clicks, create a PO specifically for this supplier
        if st.button(f"Accept and Send PO to {supplier_name}", key=f"send_{supplier_id}"):
            items_for_supplier = []
            for _, row in group_df.iterrows():
                items_for_supplier.append({
                    "item_id": int(row["itemid"]),
                    "quantity": int(row["neededquantity"]),
                    "estimated_price": None
                })
            po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
            st.success(f"✅ Purchase Order created for supplier: {supplier_name}")
            st.stop()  # Stop to refresh page after creation

    st.info("No more suppliers below threshold to show.")


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

    # a) Gather item + inventory data
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

    # b) Filter items below threshold
    df["neededquantity"] = df["averagerequired"] - df["currentquantity"]
    df = df[df["neededquantity"] > 0].copy()
    if df.empty:
        return df

    # c) Map each item to its first supplier
    supplier_map = get_first_supplier_for_items()
    df["supplierid"] = df["itemid"].map(supplier_map)
    # Drop items that have no supplier
    df.dropna(subset=["supplierid"], inplace=True)
    df["supplierid"] = df["supplierid"].astype(int)

    # d) Convert SupplierID -> SupplierName
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
