import streamlit as st
import home
from item import mainitem
import PO.mainpo as mainpo
from receive_items.main_receive import main_receive_page
import reports.main_reports as main_reports
from sidebar import sidebar

st.set_page_config(page_title="Inventory Management System", layout="wide")

# ✅ Password authentication
def authenticate():
    def login_form():
        with st.form("login"):
            st.subheader("🔐 Please log in to continue:")
            password_input = st.text_input("Enter Password", type="password")
            submit = st.form_submit_button("Login")
            return password_input, submit

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        password, submit = login_form()
        if submit:
            if password == st.secrets["app_password"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect password, please try again.")
        return False
    else:
        return True

def main():
    if authenticate():
        page = sidebar()

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
