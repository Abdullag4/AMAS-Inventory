import streamlit as st

def sidebar():
    """Handles sidebar navigation with logout button at the bottom."""
    st.sidebar.image("assets/logo.png", use_container_width=True)

    # Available pages
    pages = ["Home", "Item", "Receive Items", "Purchase Order", "Reports"]

    if st.session_state.get("user_role") == "Admin":
        pages.append("User Management")

    # Initialize selected page if not already set
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = pages[0]

    # Create buttons for each page
    for page in pages:
        if st.sidebar.button(page, use_container_width=True):
            st.session_state.selected_page = page

    # Spacer pushes logout to the bottom
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    
    # Logout button at the bottom
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.logout()

    return st.session_state.selected_page
