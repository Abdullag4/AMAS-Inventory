import streamlit as st
import home
from item import mainitem
import PO.mainpo as mainpo
from receive_items import main_receive
import reports.main_reports as main_reports
from sidebar import sidebar  # ✅ Import sidebar function

st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """Main entry point for the Inventory Management app."""
    
    page = sidebar()  # ✅ Use sidebar function for navigation

    if page == "Home":
        home.home()
    elif page == "Item":
        mainitem.item_page()
    elif page == "Receive Items":
        main_receive()
    elif page == "Purchase Order":
        mainpo.po_page()
    elif page == "Reports":
        main_reports.reports_page()

if __name__ == "__main__":
    main()
