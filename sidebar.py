import streamlit as st

def sidebar():
    """Handles sidebar navigation with a logo."""
    
    # ✅ Add logo above the sidebar
    st.sidebar.image("assets/logo.png", use_column_width=True)  # Adjust path if needed

    # ✅ Sidebar Navigation (cleaner version)
    page = st.sidebar.radio("", [
        "Home", "Item", "Receive Items", "Purchase Order", "Reports"
    ])

    return page  # ✅ Return selected page
