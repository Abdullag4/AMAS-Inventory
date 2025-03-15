import streamlit as st
import os

def sidebar():
    """Handles sidebar navigation with a logo."""

    # ✅ Define logo path
    logo_path = "assets/logo.png"

    # ✅ Check if file exists before displaying
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
    else:
        st.sidebar.warning("⚠️ Logo not found! Please add 'assets/logo.png'.")

    # ✅ Sidebar Navigation (cleaner version)
    page = st.sidebar.radio("", [
        "Home", "Item", "Receive Items", "Purchase Order", "Reports"
    ])

    return page  # ✅ Return selected page
