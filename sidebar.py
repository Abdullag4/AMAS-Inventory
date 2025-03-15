import streamlit as st
import os

def sidebar():
    """Handles sidebar navigation with a logo and button navigation."""
    
    # ✅ Define logo path
    logo_path = "assets/logo.png"

    # ✅ Sidebar Layout with Logo
    with st.sidebar:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.warning("⚠️ Logo not found! Please add 'assets/logo.png'.")

        st.divider()

        # ✅ Navigation Buttons
        nav_buttons = {
            "🏠 Home": "Home",
            "📦 Items": "Item",
            "📥 Receive Items": "Receive Items",
            "🛒 Purchase Order": "Purchase Order",
            "📊 Reports": "Reports"
        }

        # Initialize the page in session state
        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Home"

        # Display buttons and handle navigation
        for label, page in nav_buttons.items():
            if st.button(label, use_container_width=True, type="primary" if st.session_state.selected_page == page else "secondary"):
                st.session_state.selected_page = page
                st.rerun()

    return st.session_state.selected_page
