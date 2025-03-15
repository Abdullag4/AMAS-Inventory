import streamlit as st

def sidebar():
    """Handles sidebar navigation and returns the selected page."""
    st.sidebar.title("📌 Navigation")

    page = st.sidebar.radio("Go to", [
        "Home", "Item", "Receive Items", "Purchase Order", "Reports"
    ])  # ✅ Navigation options

    return page  # ✅ Return selected page
