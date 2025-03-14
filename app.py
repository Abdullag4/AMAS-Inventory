import streamlit as st
import home
from item import mainitem
import PO.mainpo as mainpo
from receive_items import main_receive
import reports.main_reports as main_reports  # ✅ Import Reports Page

st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """Main entry point for the Inventory Management app."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Item", "Receive Items", "Purchase Order", "Reports"])

    if page == "Home":
        home.home()
    elif page == "Item":
        mainitem.item_page()
    elif page == "Receive Items":
        main_receive.main_receive_page()
    elif page == "Purchase Order":
        mainpo.po_page()
    elif page == "Reports":
        main_reports.reports_page()  # ✅ Corrected function call

if __name__ == "__main__":
    main()
