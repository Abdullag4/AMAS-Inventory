import streamlit as st
import home
from item import mainitem
import PO.mainpo as mainpo
import receive_items

st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """Main entry point for the Inventory Management app."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Item", "Receive Items", "Purchase Order"])  # ✅ Added "Purchase Order"

    if page == "Home":
        home.home()
    elif page == "Item":
        mainitem.item_page()
    elif page == "Receive Items":
        receive_items.receive_items()
    elif page == "Purchase Order":
        mainpo.po_page()

if __name__ == "__main__":
    main()
