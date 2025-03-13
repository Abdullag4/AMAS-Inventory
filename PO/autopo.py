import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """
    Automatically generates purchase orders based on low-stock inventory.
    Each supplier is handled separately with an expander.
    We show item pictures in a custom table layout using st.columns().
    """
    st.subheader("📦 Automatic Purchase Order by Supplier")

    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    st.write("Items are grouped by supplier. You can create a separate PO for each supplier.")

    grouped = low_stock_df.groupby("supplierid")

    for supplier_id, group in grouped:
        supplier_name = group.iloc[0]["suppliername"]
        with st.expander(f"📦 Supplier: {supplier_name}"):
            st.write("### Items needing reorder from this supplier:")

            # ✅ Display items in a custom table layout
            for idx, row in group.iterrows():
                columns = st.columns([1, 3, 2, 2])
                
                # Column 1: Item Picture
                if row["itempicture"]:
                    columns[0].image(BytesIO(row["itempicture"]), width=60)
                else:
                    columns[0].write("No Image")

                # Column 2: Item Name
                columns[1].write(f"**{row['itemnameenglish']}**")

                # Column 3: Current Quantity & Threshold
                columns[2].write(f"Q: {int(row['currentquantity'])} / Th: {int(row['threshold'])}")

                # Column 4: Needed Quantity
                columns[3].write(f"Needed: {int(row['neededquantity'])}")

            # 📅 Let the user pick an Expected Delivery Date
            exp_date = st.date_input(
                f"📅 Expected Delivery Date for {supplier_name}",
                key=f"exp_date_{supplier_id}"
            )

            # Button to accept & send a single PO for this supplier
            if st.button(f"Accept & Send Order to {supplier_name}", key=f"send_{supplier_id}"):
                items_for_supplier = []
                for _, row in group.iterrows():
                    items_for_supplier.append({
                        "item_id": int(row["itemid"]),
                        "quantity": int(row["neededquantity"]),
                        "estimated_price": None,
                    })
                # Create the new PO for this supplier
                po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
                st.success(f"✅ Purchase Order created for {supplier_name} successfully!")
                st.stop()  # End execution, effectively refresh the page

def get_low_stock_items():
    """
    Retrieves items below threshold with needed quantity = averagerequired - currentquantity.
    Picks the first available supplier for each item. If no supplier is found, that item is excluded.
    Returns columns: itemid, itemnameenglish, currentquantity, threshold, neededquantity, supplierid, suppliername, itempicture.
    """
    query = """
    SELECT 
        i.ItemID AS itemid,
        i.ItemNameEnglish AS itemnameenglish,
        i.Threshold AS threshold,
        i.AverageRequired AS averagerequired,
        i.ItemPicture AS itempicture,
        COALESCE(SUM(inv.Quantity), 0) AS currentquantity
    FROM Item i
    LEFT JOIN Inventory inv ON i.ItemID = inv.ItemID
    GROUP BY i.ItemID, i.ItemNameEnglish, i.Threshold, i.AverageRequired, i.ItemPicture
    """
    df = po_handler.fetch_data(query)
    if df.empty:
        return pd.DataFrame()

    df["neededquantity"] = df["averagerequired"] - df["currentquantity"]
    # Keep only those with positive needed qty
    df = df[df["neededquantity"] > 0].copy()
    if df.empty:
        return df

    # Attach the default supplier
    supplier_map = get_first_supplier_for_items()  # { itemid: firstSupplierID }
    df["supplierid"] = df["itemid"].map(supplier_map)
    df.dropna(subset=["supplierid"], inplace=True)
    df["supplierid"] = df["supplierid"].astype(int)

    # Convert SupplierID -> SupplierName
    sup_df = po_handler.get_suppliers()
    sup_lookup = dict(zip(sup_df["supplierid"], sup_df["suppliername"]))
    df["suppliername"] = df["supplierid"].map(sup_lookup).fillna("No Supplier")

    return df

def get_first_supplier_for_items():
    """Returns { itemid: firstSupplierID } picking the first supplier from ItemSupplier if multiple."""
    mapping_df = po_handler.get_item_supplier_mapping()
    first_map = {}
    if not mapping_df.empty:
        for row in mapping_df.itertuples():
            item_id = getattr(row, "itemid")
            sup_id = getattr(row, "supplierid")
            if item_id not in first_map:
                first_map[item_id] = sup_id
    return first_map
