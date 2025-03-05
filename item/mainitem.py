import streamlit as st
from item.add_item import add_item_tab
from item.bulk_add import bulk_add_tab
from item.edit_item import edit_item_tab
from item.dropdowns import manage_dropdowns_tab

def item_page():
    """Item management page with multiple tabs."""
    st.title("📦 Item Management")

    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add Item", "📂 Bulk Add", "✏️ Edit Item", "📋 Manage Dropdowns"
    ])

    with tab1:
        add_item_tab()  # ✅ Handles adding new items
    with tab2:
        bulk_add_tab()  # ✅ Handles bulk item upload via Excel
    with tab3:
        edit_item_tab()  # ✅ Handles editing existing items
    with tab4:
        manage_dropdowns_tab()  # ✅ Handles managing dropdown lists

