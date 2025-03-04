import streamlit as st
from Item.add_item import add_item_tab
from Item.bulk_add import bulk_add_tab
from Item.edit_item import edit_item_tab
from Item.dropdowns import manage_dropdowns_tab

def itemadd():
    """Item Management Page"""
    st.title("🛒 Item Management")

    # ✅ Create tab structure
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add New Item", "📂 Bulk Upload", "✏️ Edit Items", "⚙️ Manage Dropdowns"])

    # ✅ Call respective tab functions
    with tab1:
        add_item_tab()
    with tab2:
        bulk_add_tab()
    with tab3:
        edit_item_tab()
    with tab4:
        manage_dropdowns_tab()
