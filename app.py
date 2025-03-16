import streamlit as st 
import home
from item import mainitem
import PO.mainpo as mainpo
from receive_items.main_receive import main_receive_page
import reports.main_reports as main_reports
from sidebar import sidebar
from inv_signin import authenticate_user, logout

st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """Main entry point for the app."""

    # ✅ Authenticate user with Google login
    user_info = authenticate_user()

    # ✅ Sidebar with logout button
    if st.sidebar.button("🔓 Logout"):
        logout()

    # ✅ Sidebar Navigation
    page = sidebar()

    # ✅ Route user to the selected page
    if page == "Home":
        home.home()
    elif page == "Item":
        mainitem.item_page()
    elif page == "Receive Items":
        main_receive_page()
    elif page == "Purchase Order":
        mainpo.po_page()
    elif page == "Reports":
        main_reports.reports_page()

if __name__ == "__main__":
    main()
