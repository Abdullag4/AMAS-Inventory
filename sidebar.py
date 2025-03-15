import streamlit as st

def sidebar():
    """Handles sidebar navigation and returns the selected page."""
    page = st.sidebar.radio("", [  # ✅ Removed extra labels for a cleaner look
        "Home", "Item", "Receive Items", "Purchase Order", "Reports"
    ])

    return page  # ✅ Return selected page
