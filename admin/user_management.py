import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def user_management():
    """Admin page to manage user permissions."""
    st.title("👤 User Management")

    # Fetch all users
    users_df = db.fetch_data("SELECT * FROM Users")

    if users_df.empty:
        st.warning("No users found.")
        return

    # Select user to manage
    user_options = dict(zip(users_df["email"], users_df["userid"]))
    selected_email = st.selectbox("📧 Select User", list(user_options.keys()))
    selected_user_id = user_options[selected_email]

    # Fetch current user permissions
    user_info = users_df[users_df["userid"] == selected_user_id].iloc[0]

    # Editable checkboxes for permissions
    st.subheader("🛠️ Manage Access Permissions")
    updated_permissions = {
        "CanAccessHome": st.checkbox("🏠 Home", value=user_info["canaccesshome"]),
        "CanAccessItems": st.checkbox("📦 Item Management", value=user_info["canaccessitems"]),
        "CanAccessReceive": st.checkbox("📥 Receive Items", value=user_info["canaccessreceive"]),
        "CanAccessPO": st.checkbox("🛒 Purchase Order", value=user_info["canaccesspo"]),
        "CanAccessReports": st.checkbox("📊 Reports", value=user_info["canaccessreports"])
    }

    # Update button
    if st.button("✅ Update Permissions"):
        set_clause = ", ".join([f"{col} = %s" for col in updated_permissions.keys()])
        query = f"""
        UPDATE Users
        SET {set_clause}
        WHERE UserID = %s
        """
        params = list(updated_permissions.values()) + [selected_user_id]
        db.execute_command(query, params)
        st.success("✅ User permissions updated successfully!")
        st.rerun()
