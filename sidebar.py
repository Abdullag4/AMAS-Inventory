import streamlit as st
import os

def sidebar():
    """Handles sidebar navigation with buttons and logo."""

    # ✅ Define logo path
    logo_path = "assets/logo.png"

    # ✅ Sidebar Layout
    with st.sidebar:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.warning("⚠️ Logo not found! Please add 'assets/logo.png'.")

        # ✅ Sidebar Buttons for Navigation
        col1, col2 = st.columns(2)
        
        if col1.button("🏠 Home"):
            return "Home"
        if col2.button("📦 Item"):
            return "Item"
        
        if col1.button("📥 Receive Items"):
            return "Receive Items"
        if col2.button("🛒 Purchase Order"):
            return "Purchase Order"

        if st.button("📊 Reports", use_container_width=True):
            return "Reports"

    return None
