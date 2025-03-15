import streamlit as st
import os

def sidebar():
    """Handles sidebar navigation with a logo and upload option."""

    # ✅ Define logo path
    logo_path = "assets/logo.png"

    # ✅ Sidebar Layout
    with st.sidebar:
        if os.path.exists(logo_path):
            st.image(logo_path, use_column_width=True)
        else:
            st.warning("⚠️ Logo not found! Upload a new one below.")

        # ✅ Upload option for logo
        uploaded_logo = st.file_uploader("Upload a new logo", type=["png", "jpg", "jpeg"])
        if uploaded_logo:
            os.makedirs("assets", exist_ok=True)  # Ensure folder exists
            with open(logo_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            st.success("✅ Logo uploaded! Refresh to see changes.")

    # ✅ Sidebar Navigation
    page = st.sidebar.radio("", [
        "Home", "Item", "Receive Items", "Purchase Order", "Reports"
    ])

    return page  # ✅ Return selected page
