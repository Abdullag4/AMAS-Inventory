import streamlit as st
from PO.po_handler import POHandler

po_handler = POHandler()

def manual_po_tab():
    st.header("🖐️ Manual Purchase Order")

    suppliers = po_handler.fetch_data("SELECT SupplierID, SupplierName FROM Supplier")
    items = po_handler.fetch_data("SELECT ItemID, ItemNameEnglish FROM Item")

    supplier_options = dict(zip(suppliers['suppliername'], suppliers['supplierid']))
    item_options = dict(zip(items['itemnameenglish'], items['itemid']))

    selected_supplier = st.selectbox("Select Supplier", list(supplier_options.keys()))
    selected_item = st.selectbox("Select Item", list(item_options.keys()))
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Create Purchase Order"):
        po_handler.create_manual_po(supplier_options[selected_supplier], item_options[selected_item], quantity)
        st.success("✅ Purchase Order created successfully!")
