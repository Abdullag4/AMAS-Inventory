import streamlit as st
import home
from item import mainitem
import PO.mainpo as mainpo
from receive_items.main_receive import main_receive_page
import reports.main_reports as main_reports
from sidebar import sidebar
from inv_signin import authenticate_user, logout  # ✅ Ensure correct import

st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """Main function handling authentication and user access."""
    authenticate_user()  # ✅ Ensure user is authenticated

    page = sidebar()  # ✅ Get selected page from sidebar

    permissions = st.session_state.get("permissions", {})

    if page == "Home" and permissions.get("CanAccessHome", False):
        home.home()
    elif page == "Item" and permissions.get("CanAccessItems", False):
        mainitem.item_page()
    elif page == "Receive Items" and permissions.get("CanAccessReceive", False):
        main_receive_page()
    elif page == "Purchase Order" and permissions.get("CanAccessPO", False):
        mainpo.po_page()
    elif page == "Reports" and permissions.get("CanAccessReports", False):
        main_reports.reports_page()
    elif page == "User Management" and st.session_state.get("user_role") == "Admin":
        from admin.user_management import user_management  # ✅ Import only if needed
        user_management()
    else:
        st.error("❌ You do not have permission to access this page.")

if __name__ == "__main__":
    main()
