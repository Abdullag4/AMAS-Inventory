import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from PO.po_handler import POHandler

po_handler = POHandler()

def auto_po_tab():
    """
    Automatically generates purchase orders based on low-stock inventory,
    grouped by supplier. Each supplier is shown in a single table, with pictures.
    """
    st.subheader("📦 Auto Purchase Orders by Supplier (Table + Images)")

    low_stock_df = get_low_stock_items()
    if low_stock_df.empty:
        st.success("✅ All stock levels are sufficient. No purchase orders needed.")
        return

    st.write("Below are the items grouped by supplier that need reordering.")

    # Group low-stock items by SupplierID
    grouped = low_stock_df.groupby("supplierid")

    for supplier_id, group in grouped:
        supplier_name = group.iloc[0]["suppliername"]

        # Show an expander for each supplier
        with st.expander(f"📦 Supplier: {supplier_name}"):
            # Build an HTML table with pictures for that supplier
            table_html = build_supplier_table(group)

            # Display the table with images
            st.markdown(table_html, unsafe_allow_html=True)

            # Let user pick an expected delivery date
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
                        "estimated_price": None
                    })
                # Create the new PO for this supplier
                po_handler.create_manual_po(supplier_id, exp_date, items_for_supplier)
                st.success(f"✅ Purchase Order created for {supplier_name} successfully!")
                st.stop()  # End execution, effectively refresh the page


def get_low_stock_items():
    """
    Retrieves items below threshold with needed quantity = averagerequired - currentquantity.
    Picks the first available supplier for each item. If none, item is excluded.
    Returns columns:
      itemid, itemnameenglish, currentquantity, threshold, neededquantity, supplierid, suppliername, itempicture
    """
    # 1) Query aggregated inventory
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
    """Returns { itemid: firstSupplierID }, picking the first supplier from ItemSupplier."""
    mapping_df = po_handler.get_item_supplier_mapping()
    first_map = {}
    if not mapping_df.empty:
        for row in mapping_df.itertuples():
            it_id = getattr(row, "itemid")
            sup_id = getattr(row, "supplierid")
            if it_id not in first_map:
                first_map[it_id] = sup_id
    return first_map

def build_supplier_table(group_df):
    """
    Builds an HTML table showing item images, names, current/threshold, needed quantity.
    group_df columns: itemid, itemnameenglish, currentquantity, threshold, neededquantity, itempicture
    """
    # Start HTML table
    html = """
    <table style="width: 100%; border-collapse: collapse;">
      <thead>
        <tr style="border-bottom: 1px solid #999;">
          <th style="text-align: left; padding: 8px;">Picture</th>
          <th style="text-align: left; padding: 8px;">Item Name</th>
          <th style="text-align: left; padding: 8px;">Current / Threshold</th>
          <th style="text-align: left; padding: 8px;">Needed</th>
        </tr>
      </thead>
      <tbody>
    """

    for _, row in group_df.iterrows():
        # Convert item picture to base64 if available
        if row["itempicture"] is not None:
            img_base64 = convert_img_to_base64(row["itempicture"])
            img_html = f"<img src='data:image/png;base64,{img_base64}' width='60'/>"
        else:
            img_html = "No Image"

        item_name = row["itemnameenglish"]
        cur_qty = int(row["currentquantity"])
        thr = int(row["threshold"])
        needed = int(row["neededquantity"])

        html += f"""
        <tr>
          <td style="padding: 8px;">{img_html}</td>
          <td style="padding: 8px;">{item_name}</td>
          <td style="padding: 8px;">{cur_qty} / {thr}</td>
          <td style="padding: 8px;">{needed}</td>
        </tr>
        """

    html += """
      </tbody>
    </table>
    """
    return html

def convert_img_to_base64(img_bytes):
    """
    Convert raw image bytes to Base64 so we can embed it in HTML.
    """
    import base64
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
