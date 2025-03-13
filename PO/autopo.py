import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """
    Automatically generates purchase orders based on low-stock inventory.
    Groups items by supplier, letting the user generate a PO for each supplier individually,
    and shows item pictures in the table.
    """
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
            st.write(f"**Items needing reorder from this supplier:**")
            
            # Show each item with picture in a manual layout
            for _, row in group.iterrows():
                cols = st.columns([1, 3, 1, 1])
                
                # 1) Display item picture
                if row["itempicture"] is not None:
                    cols[0].image(BytesIO(row["itempicture"]), width=60)
                else:
                    cols[0].write("No Image")
                
                # 2) Display item name
                cols[1].write(f"**{row['itemnameenglish']}**")
                
                # 3) Show current quantity & threshold
                cols[2].write(f"Current: {row['currentquantity']}\nThreshold: {row['threshold']}")
                
                # 4) Show needed quantity
                cols[3].write(f"Needed: {int(row['neededquantity'])}")

            # Let user choose ExpectedDelivery date for that supplier's PO
            exp_date = st.date_input(
                f"📅 Expected Delivery Date for {supplier_name}",
                key=f"exp_date_{supplier_id}"
            )

            # Accept & Send Button for that supplier
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
                st.stop()  # Refresh page after creating the PO


def get_low_stock_items():
    """
    Retrieves items below threshold with needed quantity = AverageRequired - CurrentQuantity.
    Picks the first supplier for each item if possible.
    Returns a DF with columns:
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
