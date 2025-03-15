import streamlit as st
import os

def sidebar():
    """Handles sidebar navigation with a logo and improved UI."""

    # ✅ Define logo path
    logo_path = "assets/logo.png"

    # ✅ Sidebar Layout
    with st.sidebar:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)  # ✅ Updated parameter
        else:
            st.warning("⚠️ Logo not found! Please add 'assets/logo.png'.")

    # ✅ Sidebar Navigation
    page = st.sidebar.radio("", [
        "Home", "Item", "Receive Items", "Purchase Order", "Reports"
    ])

    return page  # ✅ Return selected page
