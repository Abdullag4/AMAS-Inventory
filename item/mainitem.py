import streamlit as st
from item.add_item import add_item_tab
from item.bulk_add import bulk_add_tab
from item.edit_item import edit_item_tab
from item.manage_dropdowns import manage_dropdowns_tab
from item.add_pictures import add_pictures_tab  # ✅ New Import

def item_page():
    st.title("📦 Item Management")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Add Item", "📂 Bulk Add", "✏️ Edit Item", "📋 Manage Dropdowns", "🖼️ Add Pictures"])

    with tab1:
        add_item_tab()
    with tab2:
        bulk_add_tab()
    with tab3:
        edit_item_tab()
    with tab4:
        manage_dropdowns_tab()
    with tab5:
        add_pictures_tab()  # ✅ New Tab for Adding Pictures
