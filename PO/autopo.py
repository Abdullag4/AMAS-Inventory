import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """
    Automatically generates purchase orders based on low-stock inventory.
    Groups items by supplier, letting the user generate a PO for each supplier individually.
    """
    st.subheader("📦 Automatic Purchase Order by Supplier")

    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    # If you want, you can set a single global date; 
    # or let each supplier choose a separate date in each expander.
    st.write("Below are items grouped by supplier. Generate POs as needed.")

    grouped = low_stock_df.groupby("supplierid")

    for supplier_id, group in grouped:
        supplier_name = group.iloc[0]["suppliername"]
        with st.expander(f"📦 Supplier: {supplier_name}"):
            st.write("**Items needing reorder from this supplier:**")
            st.dataframe(group[["itemnameenglish", "currentquantity", "threshold", "neededquantity"]], use_container_width=True)

            # Let user choose ExpectedDelivery date for that supplier's PO
            exp_date = st.date_input(
                f"📅 Expected Delivery Date for {supplier_name}",
                key=f"exp_date_{supplier_id}"
            )

            # Accept & Send Button for that supplier
            if st.button(f"Accept & Send Order to {supplier_name}", key=f"send_{supplier_id}"):
                # Build the list of items for this supplier
                items_for_supplier = []
                for _, row in group.iterrows():
                    items_for_supplier.append({
                        "item_id": int(row["itemid"]),
                        "quantity": int(row["neededquantity"]),
                        "estimated_price": None
                    })
                
                po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
                st.success(f"✅ Purchase Order created for {supplier_name} successfully!")
                st.stop()  # End execution so we refresh the page

def get_low_stock_items():
    """
    Retrieves items below threshold with needed quantity = AverageRequired - CurrentQuantity.
    Picks the first available supplier for each item. If no supplier, item is excluded.
    Returns columns: itemid, itemnameenglish, currentquantity, threshold, neededquantity, supplierid, suppliername.
    """

    # 1) Get current quantity from Inventory
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

    # 2) Calculate needed quantity
    df["neededquantity"] = df["averagerequired"] - df["currentquantity"]
    df = df[df["neededquantity"] > 0].copy()
    if df.empty:
        return df

    # 3) For each item, pick the first supplier
    supplier_map = get_first_supplier_for_items()
    df["supplierid"] = df["itemid"].map(supplier_map)
    df.dropna(subset=["supplierid"], inplace=True)
    df["supplierid"] = df["supplierid"].astype(int)

    # 4) Convert SupplierID -> SupplierName
    sup_df = po_handler.get_suppliers()
    sup_lookup = dict(zip(sup_df["supplierid"], sup_df["suppliername"]))
    df["suppliername"] = df["supplierid"].map(sup_lookup).fillna("No Supplier")

    return df

def get_first_supplier_for_items():
    """
    Returns { itemid: firstSupplierID }.
    If an item has multiple suppliers, picks the first. 
    If none, item won't appear in final DF.
    """
    mapping_df = po_handler.get_item_supplier_mapping()
    first_map = {}
    if not mapping_df.empty:
        for row in mapping_df.itertuples():
            # row.itemid, row.supplierid
            item_id = getattr(row, "itemid")
            sup_id = getattr(row, "supplierid")
            if item_id not in first_map:
                first_map[item_id] = sup_id
    return first_map
