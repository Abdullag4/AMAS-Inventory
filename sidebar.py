import streamlit as st

def sidebar():
    """Handles sidebar navigation based on user permissions."""
    
    st.sidebar.image("assets/logo.png", use_container_width=True)
    
    # Logout button
    if st.sidebar.button("🔓 Log Out", on_click=st.logout):
        st.rerun()

    # Fetch user permissions
    permissions = st.session_state.get("permissions", {})

    # Show buttons based on permissions
    if permissions.get("CanAccessHome", False) and st.sidebar.button("🏠 Home"):
        return "Home"
    if permissions.get("CanAccessItems", False) and st.sidebar.button("📦 Item Management"):
        return "Item"
    if permissions.get("CanAccessReceive", False) and st.sidebar.button("📥 Receive Items"):
        return "Receive Items"
    if permissions.get("CanAccessPO", False) and st.sidebar.button("🛒 Purchase Order"):
        return "Purchase Order"
    if permissions.get("CanAccessReports", False) and st.sidebar.button("📊 Reports"):
        return "Reports"
    if st.session_state.get("user_role") == "Admin" and st.sidebar.button("⚙️ User Management"):
        return "User Management"

    return None
